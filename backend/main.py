from __future__ import annotations

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from unicodedata import normalize

from fastapi import FastAPI, File, Header, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from chat.responder import build_chat_response
from chat.retriever import retrieve_events
from dashboard_service import load_dashboard_data
from ml.classifier import predict_gratuito_pago
from pipeline import process_event_dict
from scrapers import run_all as _run_scrapers
from scrapers.ticketpe import scrape as _scrape_ticketpe
from dotenv import load_dotenv
from storage.events_store import EventsStore

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")
DATA_DIR = BASE_DIR / "data"
UPLOADS_DIR = BASE_DIR / "uploads"
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Onde Acontece Recife", version="0.5.0-ciclo3")

def _cors_origins() -> list[str]:
    defaults = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:9000",
        "http://127.0.0.1:9000",
        "http://localhost:9200",
        "http://127.0.0.1:9200",
        "http://localhost:9300",
        "http://127.0.0.1:9300",
    ]
    extra = os.environ.get("CORS_ORIGINS", "").strip()
    if not extra:
        return defaults
    return defaults + [origin.strip() for origin in extra.split(",") if origin.strip()]


app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/uploads", StaticFiles(directory=UPLOADS_DIR), name="uploads")

logger = logging.getLogger(__name__)
store = EventsStore(DATA_DIR / "events.json")


def _slug(text: str) -> str:
    s = normalize("NFD", text or "")
    s = "".join(c for c in s if not (0x0300 <= ord(c) <= 0x036F))
    s = s.lower()
    import re

    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def _parse_iso(value: Optional[str]):
    if not value:
        return None
    try:
        s = value.strip()
        if "T" not in s:
            s += "T00:00:00"
        return datetime.fromisoformat(s)
    except ValueError:
        return None


def _now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _moderator_key() -> str:
    return os.environ.get("MODERATOR_KEY", "demo-moderador")


def _require_moderator_key(header_value: Optional[str]) -> None:
    received = (header_value or "").strip()
    if received != _moderator_key():
        raise HTTPException(status_code=401, detail="Chave de moderacao invalida.")


def _list_all_events() -> list[dict[str, Any]]:
    return store.list()


def _list_public_events() -> list[dict[str, Any]]:
    return [event for event in _list_all_events() if event.get("status_moderacao") == "aprovado"]


def _with_common_fields(
    raw: Dict[str, Any],
    *,
    status: str,
    cadastro_via: str,
    flyer_path: Optional[str] = None,
) -> Dict[str, Any]:
    row = process_event_dict(raw)
    for extra_key in ("lat", "lng", "source", "link_compra", "slug", "external_id", "image_url"):
        if raw.get(extra_key) is not None:
            row[extra_key] = raw[extra_key]

    row["slug"] = row.get("slug") or _slug(row.get("titulo", ""))
    row["status_moderacao"] = status
    row["flyer_path"] = flyer_path
    row["observacoes_flyer"] = raw.get("observacoes_flyer")
    row["motivo_rejeicao"] = raw.get("motivo_rejeicao")
    row["cadastro_via"] = cadastro_via
    row["criado_em"] = raw.get("criado_em") or _now_iso()
    texto = f"{row.get('titulo', '')} {row.get('descricao', '')}"
    row["classificacao_texto"] = predict_gratuito_pago(texto)
    return row


def _seed() -> None:
    if _list_all_events():
        return
    loaded = _scrape_ticketpe(max_events=2)
    rows = [_with_common_fields(raw, status="aprovado", cadastro_via="scraper") for raw in loaded]
    if rows:
        store.replace_all(rows)
    else:
        logger.warning("Nenhum evento inicial carregado do TicketPE.")


def _suggest_from_filename(filename: Optional[str]) -> Dict[str, Any]:
    stem = Path(filename or "flyer-evento").stem.replace("_", " ").replace("-", " ").strip()
    title = " ".join(part.capitalize() for part in stem.split()) or "Evento enviado por flyer"
    return {
        "titulo": title,
        "descricao": "Evento enviado via flyer pelo produtor.",
        "categoria": None,
        "bairro": None,
        "local": "",
        "inicio_iso": None,
        "preco": None,
        "gratuito": False,
        "observacoes_flyer": "Preencha os dados manualmente a partir do flyer enviado.",
    }


_seed()


class ClassificarBody(BaseModel):
    texto: str = Field(min_length=1)


class EventCreate(BaseModel):
    titulo: str = Field(min_length=3, max_length=200)
    descricao: str = Field(default="", max_length=4000)
    categoria: Optional[str] = None
    bairro: Optional[str] = None
    local: str = Field(default="", max_length=300)
    lat: Optional[float] = None
    lng: Optional[float] = None
    inicio_iso: Optional[str] = None
    preco: Optional[float] = None
    gratuito: Optional[bool] = None
    organizador: str = Field(min_length=2, max_length=200)
    email_contato: str = Field(min_length=5, max_length=200)
    source: Optional[str] = None
    link_compra: Optional[str] = None
    flyer_path: Optional[str] = None
    observacoes_flyer: Optional[str] = None


class FlyerSubmitBody(EventCreate):
    flyer_path: str = Field(min_length=5, max_length=300)


class ModerationRejectBody(BaseModel):
    motivo: str = Field(min_length=3, max_length=300)


class ChatBody(BaseModel):
    mensagem: str = Field(min_length=2, max_length=500)
    historico: list[dict[str, Any]] = Field(default_factory=list)


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.get("/")
def read_root() -> Dict[str, str]:
    return {"message": "Onde Acontece Recife API", "docs": "/docs"}


@app.get("/events")
def list_events(
    categoria: Optional[str] = Query(None, description="Filtro parcial por categoria"),
    preco: Optional[str] = Query(None, description="gratuito | ate50 | 50a100 | acima100"),
    bairro: Optional[str] = Query(None, description="Filtro parcial por bairro"),
    data: Optional[str] = Query(None, description="hoje | amanha | fds | semana"),
    agora: bool = Query(False, description="Apenas eventos nas próximas 3h"),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
) -> Dict[str, Any]:
    now = datetime.now()
    results = list(_list_public_events())

    if categoria:
        cat_low = categoria.lower()
        results = [e for e in results if cat_low in (e.get("categoria") or "").lower()]
    if preco:

        def _preco_ok(e):
            p = e.get("preco")
            gratis = e.get("gratuito") or p == 0
            if preco == "gratuito":
                return gratis
            if p is None:
                return False
            if preco == "ate50":
                return not gratis and p <= 50
            if preco == "50a100":
                return 50 < p <= 100
            if preco == "acima100":
                return p > 100
            return True

        results = [e for e in results if _preco_ok(e)]

    if bairro:
        b_low = bairro.lower()
        results = [e for e in results if b_low in (e.get("bairro") or "").lower()]

    if data:
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)

        def _data_ok(e):
            dt = _parse_iso(e.get("inicio_iso"))
            if not dt:
                return False
            if data == "hoje":
                return dt.date() == today.date()
            if data == "amanha":
                from datetime import timedelta

                amanha = (today + timedelta(days=1)).date()
                return dt.date() == amanha
            if data == "fds":
                return dt.weekday() in (5, 6)
            if data == "semana":
                from datetime import timedelta

                return today <= dt <= today + timedelta(days=7)
            return True

        results = [e for e in results if _data_ok(e)]

    if agora:
        from datetime import timedelta

        limite = now + timedelta(hours=3)

        def _agora_ok(e):
            dt = _parse_iso(e.get("inicio_iso"))
            return dt and now <= dt <= limite

        results = [e for e in results if _agora_ok(e)]

    total = len(results)
    start = (page - 1) * per_page
    paginated = results[start : start + per_page]
    return {"total": total, "page": page, "per_page": per_page, "results": paginated}


def _event_matches_slug(ev: Dict[str, Any], slug: str) -> bool:
    if ev.get("slug") and ev.get("slug") == slug:
        return True
    return _slug(ev.get("titulo", "")) == slug


@app.get("/events/{slug}")
def get_event(slug: str) -> Dict[str, Any]:
    for ev in _list_public_events():
        if _event_matches_slug(ev, slug):
            return ev
    raise HTTPException(status_code=404, detail="Evento não encontrado.")


@app.post("/events", status_code=201)
def create_event(body: EventCreate) -> Dict[str, Any]:
    raw = body.model_dump()
    row = _with_common_fields(raw, status="pendente", cadastro_via="manual", flyer_path=raw.get("flyer_path"))
    return store.insert(row)


@app.post("/events/flyer/preview")
async def flyer_preview(file: UploadFile = File(...)) -> Dict[str, Any]:
    if file.content_type not in {"image/jpeg", "image/png", "image/webp"}:
        raise HTTPException(status_code=400, detail="Envie uma imagem JPG, PNG ou WEBP.")
    content = await file.read()
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Imagem maior que 5MB.")

    suffix = Path(file.filename or "flyer.jpg").suffix or ".jpg"
    safe_name = f"{datetime.now().strftime('%Y%m%d%H%M%S%f')}{suffix.lower()}"
    save_path = UPLOADS_DIR / safe_name
    save_path.write_bytes(content)

    flyer_path = f"/uploads/{safe_name}"
    return {
        "flyer_url": flyer_path,
        "flyer_path": flyer_path,
        "campos_sugeridos": _suggest_from_filename(file.filename),
    }


@app.post("/events/flyer/submit", status_code=201)
def flyer_submit(body: FlyerSubmitBody) -> Dict[str, Any]:
    raw = body.model_dump()
    row = _with_common_fields(raw, status="pendente", cadastro_via="flyer", flyer_path=raw.get("flyer_path"))
    return store.insert(row)


@app.get("/moderacao/pendentes")
def moderation_pending(x_moderator_key: Optional[str] = Header(default=None)) -> List[Dict[str, Any]]:
    _require_moderator_key(x_moderator_key)
    return [event for event in _list_all_events() if event.get("status_moderacao") == "pendente"]


@app.patch("/moderacao/{event_id}/aprovar")
def moderation_approve(event_id: str, x_moderator_key: Optional[str] = Header(default=None)) -> Dict[str, Any]:
    _require_moderator_key(x_moderator_key)
    row = store.update(event_id, {"status_moderacao": "aprovado", "motivo_rejeicao": None})
    if not row:
        raise HTTPException(status_code=404, detail="Evento não encontrado.")
    return row


@app.patch("/moderacao/{event_id}/rejeitar")
def moderation_reject(
    event_id: str,
    body: ModerationRejectBody,
    x_moderator_key: Optional[str] = Header(default=None),
) -> Dict[str, Any]:
    _require_moderator_key(x_moderator_key)
    row = store.update(
        event_id,
        {"status_moderacao": "rejeitado", "motivo_rejeicao": body.motivo},
    )
    if not row:
        raise HTTPException(status_code=404, detail="Evento não encontrado.")
    return row


@app.post("/chat")
def chat(body: ChatBody) -> Dict[str, Any]:
    events = retrieve_events(body.mensagem, _list_public_events(), limit=3)
    return build_chat_response(body.mensagem, events)


@app.get("/meta/bairros")
def get_bairros() -> List[str]:
    seen = set()
    result = []
    for ev in _list_public_events():
        b = ev.get("bairro")
        if b and b not in seen:
            seen.add(b)
            result.append(b)
    return sorted(result)


@app.get("/meta/categorias")
def get_categorias() -> List[str]:
    seen = set()
    result = []
    for ev in _list_public_events():
        c = ev.get("categoria")
        if c and c not in seen:
            seen.add(c)
            result.append(c)
    return sorted(result)


@app.post("/ml/classificar")
def classificar(body: ClassificarBody) -> Dict[str, Any]:
    return predict_gratuito_pago(body.texto)


@app.post("/scraper/run")
def scraper_run(max_por_fonte: int = 2) -> Dict[str, Any]:
    existing = [event for event in _list_all_events() if event.get("cadastro_via") != "scraper"]
    result = _run_scrapers(max_per_source=max_por_fonte)
    raw_events: list[Dict[str, Any]] = result.get("events", [])
    scraped = [_with_common_fields(raw, status="aprovado", cadastro_via="scraper") for raw in raw_events]
    store.replace_all(existing + scraped)
    return {
        "adicionados": len(raw_events),
        "ignorados_duplicados": 0,
        "por_fonte": result.get("por_fonte", {}),
        "erros": result.get("erros", []),
        "total_em_memoria": len(_list_all_events()),
    }


@app.post("/pipeline/preview")
def pipeline_preview(body: EventCreate) -> Dict[str, Any]:
    return process_event_dict(body.model_dump())


@app.get("/dashboard/data")
def dashboard_data() -> Dict[str, Any]:
    return load_dashboard_data()
