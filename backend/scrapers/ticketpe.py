from __future__ import annotations

import logging
import os
import re
from datetime import datetime
from typing import Any

import requests

logger = logging.getLogger(__name__)

_TIMEOUT = 15
_HEADERS = {
    "Accept": "application/json",
    "User-Agent": "OndeAconteceRecife/1.0 (+https://github.com/cesar-school/onde-acontece-recife)",
}


def _base_url() -> str:
    url = os.environ.get("TICKET_API_BASE_URL", "http://127.0.0.1:8090").strip().rstrip("/")
    if url and not url.startswith(("http://", "https://")):
        url = f"https://{url}"
    return url


def _public_url() -> str:
    return os.environ.get("TICKET_PUBLIC_URL", "https://www.ticketpe.com.br").rstrip("/")


def _parse_start_date(value: str | None) -> str | None:
    if not value:
        return None
    raw = str(value).strip()[:19]
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M", "%Y-%m-%d"):
        try:
            dt = datetime.strptime(raw, fmt)
            return dt.strftime("%Y-%m-%dT%H:%M")
        except ValueError:
            continue
    return None


def _parse_ticket_event(raw: dict[str, Any]) -> dict[str, Any] | None:
    titulo = (raw.get("title") or "").strip()
    if not titulo:
        return None

    slug = (raw.get("slug") or "").strip()
    descricao = (raw.get("description") or raw.get("highlight") or "").strip()
    descricao = re.sub(r"<[^>]+>", " ", descricao)[:4000]

    price = raw.get("price")
    preco: float | None = None
    gratuito = False
    if price is not None:
        try:
            preco = float(price)
            gratuito = preco == 0
        except (TypeError, ValueError):
            pass
    else:
        gratuito = True

    tags = raw.get("tags") or []
    categoria = "Outros"
    if isinstance(tags, list) and tags:
        first = tags[0]
        if isinstance(first, dict) and first.get("name"):
            categoria = str(first["name"])

    city = (raw.get("city") or "Recife").strip()
    location = (raw.get("location") or city).strip()

    link = f"{_public_url()}/{slug}" if slug else _public_url()

    return {
        "titulo": titulo[:200],
        "descricao": descricao,
        "categoria": categoria,
        "bairro": city.lower(),
        "local": location[:300],
        "lat": None,
        "lng": None,
        "inicio_iso": _parse_start_date(raw.get("start_date")),
        "preco": preco,
        "gratuito": gratuito,
        "organizador": "TicketPE",
        "email_contato": "contato@ticketpe.com.br",
        "source": "ticketpe",
        "link_compra": link,
        "slug": slug or None,
        "external_id": raw.get("id"),
        "image_url": raw.get("image_url"),
    }


def scrape(max_events: int = 2, city: str | None = None) -> list[dict[str, Any]]:
    limit = int(os.environ.get("TICKET_FETCH_LIMIT", max_events))
    city = os.environ.get("TICKET_CITY", city)
    params: dict[str, Any] = {"limit": limit}
    if city:
        params["city"] = city

    url = f"{_base_url()}/api/v1/events"
    try:
        resp = requests.get(url, params=params, headers=_HEADERS, timeout=_TIMEOUT)
        resp.raise_for_status()
        payload = resp.json()
    except requests.RequestException as exc:
        logger.warning("ticketpe: falha ao buscar %s — %s", url, exc)
        return []

    items = payload.get("data") if isinstance(payload, dict) else payload
    if not isinstance(items, list):
        logger.warning("ticketpe: resposta inesperada de %s", url)
        return []

    events: list[dict[str, Any]] = []
    for raw in items[:limit]:
        if not isinstance(raw, dict):
            continue
        parsed = _parse_ticket_event(raw)
        if parsed:
            events.append(parsed)

    logger.info("ticketpe: %d evento(s) de %s", len(events), url)
    return events
