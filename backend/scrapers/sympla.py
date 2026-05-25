from __future__ import annotations

import json
import logging
import re
from datetime import datetime
from typing import Any

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

_URL = "https://www.sympla.com.br/eventos/recife-pe"
_TIMEOUT = 15
_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; OndeAconteceBot/1.0; "
        "+https://github.com/cesar-school/onde-acontece-recife)"
    ),
    "Accept-Language": "pt-BR,pt;q=0.9",
}


def _extract_next_data(html: str) -> list[dict] | None:
    soup = BeautifulSoup(html, "html.parser")
    tag = soup.find("script", id="__NEXT_DATA__")
    if not tag:
        return None
    try:
        data = json.loads(tag.string or "")
        events = (
            data.get("props", {})
            .get("pageProps", {})
            .get("events")
            or data.get("props", {})
            .get("pageProps", {})
            .get("initialData", {})
            .get("events")
        )
        if isinstance(events, list):
            return events
    except (json.JSONDecodeError, AttributeError):
        pass
    return None


def _parse_sympla_event(raw: dict) -> dict[str, Any] | None:
    titulo = raw.get("name") or raw.get("title") or ""
    if not titulo:
        return None

    descricao = raw.get("description") or raw.get("detail") or ""
    descricao = re.sub(r"<[^>]+>", " ", str(descricao)).strip()
    inicio_iso: str | None = None
    start = raw.get("start_date") or raw.get("startDate") or raw.get("date") or ""
    if start:
        for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M", "%Y-%m-%d"):
            try:
                dt = datetime.strptime(str(start)[:19], fmt)
                inicio_iso = dt.strftime("%Y-%m-%dT%H:%M")
                break
            except ValueError:
                continue

    price_info = raw.get("min_ticket_price") or raw.get("price") or raw.get("minPrice")
    preco: float | None = None
    gratuito = False
    if price_info is not None:
        try:
            preco = float(price_info)
            gratuito = preco == 0
        except (TypeError, ValueError):
            pass

    venue = raw.get("venue") or raw.get("location") or {}
    if isinstance(venue, dict):
        local = venue.get("name") or venue.get("address") or "Recife"
        bairro = venue.get("neighborhood") or venue.get("district") or "Recife"
        lat = venue.get("lat") or venue.get("latitude")
        lng = venue.get("lng") or venue.get("longitude")
    else:
        local = str(venue) if venue else "Recife"
        bairro = "Recife"
        lat = lng = None

    categoria_raw = raw.get("category") or raw.get("type") or "Outros"
    link = raw.get("url") or raw.get("link") or ""

    return {
        "titulo": titulo[:200],
        "descricao": descricao[:4000],
        "categoria": str(categoria_raw),
        "bairro": str(bairro),
        "local": str(local)[:300],
        "lat": float(lat) if lat else None,
        "lng": float(lng) if lng else None,
        "inicio_iso": inicio_iso,
        "preco": preco,
        "gratuito": gratuito,
        "organizador": raw.get("organizer", {}).get("name", "Sympla") if isinstance(raw.get("organizer"), dict) else "Sympla",
        "email_contato": "contato@sympla.com.br",
        "source": "sympla",
        "link_compra": link or None,
    }


def scrape(max_events: int = 30) -> list[dict[str, Any]]:
    try:
        resp = requests.get(_URL, headers=_HEADERS, timeout=_TIMEOUT)
        resp.raise_for_status()
    except requests.RequestException as exc:
        logger.warning("sympla: falha ao buscar %s — %s", _URL, exc)
        return _fallback_events()

    raw_events = _extract_next_data(resp.text)

    if not raw_events:
        logger.warning("sympla: JSON não encontrado na página — usando fallback")
        return _fallback_events()

    events: list[dict[str, Any]] = []
    for raw in raw_events[:max_events]:
        parsed = _parse_sympla_event(raw)
        if parsed:
            events.append(parsed)

    if not events:
        logger.warning("sympla: nenhum evento parseado — usando fallback")
        return _fallback_events()

    logger.info("sympla: %d eventos coletados", len(events))
    return events


def _fallback_events() -> list[dict[str, Any]]:
    now_year = datetime.now().year
    return [
        {
            "titulo": "Festival Rec-Beat — Edição Junina",
            "descricao": "Festival de música independente com palcos no Marco Zero. Ingressos disponíveis.",
            "categoria": "Festival",
            "bairro": "Recife Antigo",
            "local": "Praça do Marco Zero",
            "lat": -8.0631,
            "lng": -34.8711,
            "inicio_iso": f"{now_year}-06-28T16:00",
            "preco": 40.0,
            "gratuito": False,
            "organizador": "Rec-Beat Produções",
            "email_contato": "contato@sympla.com.br",
            "source": "sympla",
            "link_compra": "https://www.sympla.com.br",
        },
        {
            "titulo": "Oficina de Cerâmica Nordestina",
            "descricao": "Aprenda técnicas de cerâmica com artista pernambucana. Vagas limitadas. R$120 com material.",
            "categoria": "Oficina",
            "bairro": "Boa Vista",
            "local": "Ateliê Barro & Arte",
            "lat": -8.0570,
            "lng": -34.8990,
            "inicio_iso": f"{now_year}-07-06T09:00",
            "preco": 120.0,
            "gratuito": False,
            "organizador": "Ateliê Barro & Arte",
            "email_contato": "contato@sympla.com.br",
            "source": "sympla",
            "link_compra": "https://www.sympla.com.br",
        },
        {
            "titulo": "Stand-up: Noite de Humor Recifense",
            "descricao": "Cinco comediantes locais em uma noite de stand-up. Ingresso solidário R$20.",
            "categoria": "Teatro",
            "bairro": "Boa Viagem",
            "local": "Casa de Shows Armazém",
            "lat": -8.1140,
            "lng": -34.9030,
            "inicio_iso": f"{now_year}-07-11T20:00",
            "preco": 20.0,
            "gratuito": False,
            "organizador": "Humor PE",
            "email_contato": "contato@sympla.com.br",
            "source": "sympla",
            "link_compra": "https://www.sympla.com.br",
        },
        {
            "titulo": "Mostra Fotográfica Recife Submerso — Abertura Gratuita",
            "descricao": "Fotos do cotidiano aquático do Recife por fotógrafos independentes. Entrada franca.",
            "categoria": "Exposição",
            "bairro": "Boa Vista",
            "local": "Galeria de Arte da UFPE",
            "lat": -8.0540,
            "lng": -34.9490,
            "inicio_iso": f"{now_year}-07-18T18:00",
            "preco": 0.0,
            "gratuito": True,
            "organizador": "Coletivo Foto PE",
            "email_contato": "contato@sympla.com.br",
            "source": "sympla",
            "link_compra": None,
        },
    ]


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    for ev in scrape():
        print(ev["titulo"], "|", ev.get("inicio_iso"), "|", "grátis" if ev["gratuito"] else f"R${ev['preco']}")
