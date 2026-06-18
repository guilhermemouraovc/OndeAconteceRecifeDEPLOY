"""
Carrega eventos de teste a partir de data/dashboard_eventos.csv.

Uso local (grava em data/events.json):
  cd backend && python -m scripts.seed_dashboard_events --limit 30

Uso em produção (API Render):
  cd backend && python -m scripts.seed_dashboard_events \\
    --api https://onde-acontece-api.onrender.com \\
    --moderator-key SEU_MODERATOR_KEY \\
    --limit 30

Ou via curl (após deploy):
  curl -X POST "https://onde-acontece-api.onrender.com/admin/seed-dashboard?limit=30" \\
    -H "X-Moderator-Key: SEU_MODERATOR_KEY"
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any
from urllib import error, request

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dashboard_service import _read_csv_safe, normalize_events
from ml.classifier import predict_gratuito_pago
from pipeline import process_event_dict
from storage.events_store import EventsStore

CSV_PATH = ROOT / "data" / "dashboard_eventos.csv"
STORE_PATH = ROOT / "data" / "events.json"


def _extract_local(nome: str, bairro: str) -> str:
    if "—" in nome:
        local = nome.split("—", 1)[1].strip()
        if local:
            return local[:300]
    if "-" in nome:
        local = nome.split("-", 1)[1].strip()
        if local:
            return local[:300]
    return f"{bairro}, Recife"[:300]


def _shift_inicio_iso(value: str | None, offset_days: int) -> str | None:
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(value.replace("Z", ""))
    except ValueError:
        return value
    shifted = dt + timedelta(days=offset_days)
    return shifted.strftime("%Y-%m-%dT%H:%M:%S")


def load_dashboard_seed_rows(limit: int | None = None, shift_days: int = 365) -> list[dict[str, Any]]:
    df = normalize_events(_read_csv_safe(CSV_PATH))
    if limit is not None:
        df = df.head(limit)

    rows: list[dict[str, Any]] = []
    for idx, row in df.iterrows():
        titulo = str(row["titulo"]).strip()
        bairro = str(row.get("bairro") or "Recife").strip()
        plataforma = str(row.get("source") or "dashboard").strip()
        rows.append(
            {
                "external_id": str(row.get("id") or f"dashboard-{idx}"),
                "titulo": titulo,
                "descricao": (
                    f"Evento de teste ({plataforma}) em {bairro}. "
                    f"Público estimado: {int(row.get('publico_estimado') or 0)} pessoas."
                ),
                "categoria": str(row.get("categoria") or "Outros"),
                "bairro": bairro,
                "local": _extract_local(titulo, bairro),
                "lat": float(row["lat"]) if pd.notna(row.get("lat")) else None,
                "lng": float(row["lng"]) if pd.notna(row.get("lng")) else None,
                "inicio_iso": _shift_inicio_iso(str(row.get("inicio_iso") or ""), shift_days),
                "preco": float(row["preco"]) if pd.notna(row.get("preco")) else None,
                "gratuito": bool(row.get("gratuito")),
                "organizador": plataforma,
                "email_contato": "contato@ondeacontece.recife",
                "source": plataforma.lower().replace(" ", "_"),
                "link_compra": None,
                "slug": None,
            }
        )
    return rows


def _finalize_seed_row(raw: dict[str, Any]) -> dict[str, Any]:
    row = process_event_dict(raw)
    row["status_moderacao"] = "aprovado"
    row["cadastro_via"] = "seed_dashboard"
    row["criado_em"] = datetime.now().isoformat(timespec="seconds")
    if raw.get("external_id"):
        row["external_id"] = raw["external_id"]
    texto = f"{row.get('titulo', '')} {row.get('descricao', '')}"
    row["classificacao_texto"] = predict_gratuito_pago(texto)
    return row


def build_seed_events(limit: int | None = None, shift_days: int = 365) -> list[dict[str, Any]]:
    return [_finalize_seed_row(raw) for raw in load_dashboard_seed_rows(limit=limit, shift_days=shift_days)]


def seed_local_store(
    *,
    limit: int | None = 30,
    shift_days: int = 365,
    replace: bool = False,
) -> dict[str, Any]:
    store = EventsStore(STORE_PATH)
    seeded = build_seed_events(limit=limit, shift_days=shift_days)
    existing = [] if replace else store.list()
    existing_ids = {event.get("external_id") for event in existing if event.get("external_id")}
    merged = list(existing)
    added = 0
    for event in seeded:
        if event.get("external_id") in existing_ids:
            continue
        merged.append(event)
        existing_ids.add(event.get("external_id"))
        added += 1
    store.replace_all(merged)
    return {"adicionados": added, "total": len(merged), "modo": "local"}


def _http_json(method: str, url: str, payload: dict | None = None, headers: dict | None = None) -> Any:
    data = None
    req_headers = {"Accept": "application/json", **(headers or {})}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        req_headers["Content-Type"] = "application/json"
    req = request.Request(url, data=data, headers=req_headers, method=method)
    try:
        with request.urlopen(req, timeout=60) as resp:
            body = resp.read().decode("utf-8")
            return json.loads(body) if body else {}
    except error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"{method} {url} -> {exc.code}: {detail}") from exc


def seed_via_api(
    api_base: str,
    moderator_key: str,
    *,
    limit: int | None = 30,
    shift_days: int = 365,
) -> dict[str, Any]:
    base = api_base.rstrip("/")
    headers = {"X-Moderator-Key": moderator_key}
    seeded = build_seed_events(limit=limit, shift_days=shift_days)
    added = 0
    skipped = 0
    for event in seeded:
        payload = {
            "titulo": event["titulo"],
            "descricao": event.get("descricao", ""),
            "categoria": event.get("categoria"),
            "bairro": event.get("bairro"),
            "local": event.get("local", ""),
            "lat": event.get("lat"),
            "lng": event.get("lng"),
            "inicio_iso": event.get("inicio_iso"),
            "preco": event.get("preco"),
            "gratuito": event.get("gratuito"),
            "organizador": event.get("organizador", "Produtor"),
            "email_contato": event.get("email_contato", "contato@exemplo.com"),
            "source": event.get("source"),
            "link_compra": event.get("link_compra"),
        }
        created = _http_json("POST", f"{base}/events", payload)
        event_id = created.get("id")
        if not event_id:
            skipped += 1
            continue
        _http_json("PATCH", f"{base}/moderacao/{event_id}/aprovar", None, headers)
        added += 1
    return {"adicionados": added, "ignorados": skipped, "modo": "api", "api": base}


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed de eventos a partir do dashboard_eventos.csv")
    parser.add_argument("--limit", type=int, default=30, help="Quantidade de eventos (padrão: 30)")
    parser.add_argument("--shift-days", type=int, default=365, help="Desloca datas para o futuro")
    parser.add_argument("--replace", action="store_true", help="Substitui todos os eventos locais")
    parser.add_argument("--api", help="URL da API (ex.: https://onde-acontece-api.onrender.com)")
    parser.add_argument("--moderator-key", help="Chave de moderação para aprovar eventos na API")
    args = parser.parse_args()

    if args.api:
        if not args.moderator_key:
            parser.error("--moderator-key é obrigatório com --api")
        result = seed_via_api(
            args.api,
            args.moderator_key,
            limit=args.limit,
            shift_days=args.shift_days,
        )
    else:
        result = seed_local_store(
            limit=args.limit,
            shift_days=args.shift_days,
            replace=args.replace,
        )

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
