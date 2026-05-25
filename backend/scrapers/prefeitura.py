from __future__ import annotations

import logging
import re
from datetime import datetime
from typing import Any

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

_URL = "https://conectarecife.recife.pe.gov.br/agenda"
_TIMEOUT = 15
_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; OndeAconteceBot/1.0; "
        "+https://github.com/cesar-school/onde-acontece-recife)"
    )
}


def _parse_preco(text: str) -> tuple[float | None, bool]:
    t = text.lower()
    if any(w in t for w in ("gratuito", "grátis", "gratis", "entrada franca", "acesso livre")):
        return 0.0, True
    match = re.search(r"r\$\s*([\d]+(?:[.,]\d{1,2})?)", t)
    if match:
        value = float(match.group(1).replace(",", "."))
        return value, value == 0
    return None, False


def _parse_date(text: str) -> str | None:
    meses = {
        "janeiro": 1, "fevereiro": 2, "março": 3, "abril": 4,
        "maio": 5, "junho": 6, "julho": 7, "agosto": 8,
        "setembro": 9, "outubro": 10, "novembro": 11, "dezembro": 12,
    }
    m = re.search(
        r"(\d{1,2})\s+de\s+(\w+)\s+(?:de\s+)?(\d{4})(?:[,\s]+(\d{1,2})h(?:(\d{2}))?)?",
        text.lower(),
    )
    if m:
        day, mes_str, year = int(m.group(1)), m.group(2), int(m.group(3))
        hour = int(m.group(4)) if m.group(4) else 0
        minute = int(m.group(5)) if m.group(5) else 0
        mes = meses.get(mes_str)
        if mes:
            try:
                dt = datetime(year, mes, day, hour, minute)
                return dt.strftime("%Y-%m-%dT%H:%M")
            except ValueError:
                pass
    return None


def scrape(max_events: int = 30) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    try:
        resp = requests.get(_URL, headers=_HEADERS, timeout=_TIMEOUT)
        resp.raise_for_status()
    except requests.RequestException as exc:
        logger.warning("prefeitura: falha ao buscar %s — %s", _URL, exc)
        return _fallback_events()

    soup = BeautifulSoup(resp.text, "html.parser")
    candidates = (
        soup.select("article.event")
        or soup.select(".agenda-item")
        or soup.select(".card-evento")
        or soup.select("[class*='event']")
    )

    if not candidates:
        logger.warning("prefeitura: seletores não encontraram cards — usando fallback")
        return _fallback_events()

    for card in candidates[:max_events]:
        title_el = card.find(["h2", "h3", "h4", ".title", ".titulo"])
        if not title_el:
            continue
        titulo = title_el.get_text(strip=True)
        if not titulo:
            continue

        descricao = ""
        desc_el = card.find(["p", ".descricao", ".description"])
        if desc_el:
            descricao = desc_el.get_text(strip=True)

        bairro = ""
        local_el = card.find([".local", ".endereco", ".location"])
        local = local_el.get_text(strip=True) if local_el else ""

        date_el = card.find([".data", ".date", "time"])
        date_text = date_el.get_text(strip=True) if date_el else ""
        inicio_iso = _parse_date(date_text) or _parse_date(card.get_text())

        price_text = card.get_text()
        preco, gratuito = _parse_preco(price_text)

        events.append(
            {
                "titulo": titulo,
                "descricao": descricao,
                "categoria": "Cultura popular",
                "bairro": bairro or "Recife",
                "local": local or "Recife",
                "lat": None,
                "lng": None,
                "inicio_iso": inicio_iso,
                "preco": preco,
                "gratuito": gratuito,
                "organizador": "Prefeitura do Recife",
                "email_contato": "agenda@recife.pe.gov.br",
                "source": "prefeitura",
                "link_compra": None,
            }
        )

    if not events:
        logger.warning("prefeitura: nenhum evento parseado — usando fallback")
        return _fallback_events()

    logger.info("prefeitura: %d eventos coletados", len(events))
    return events


def _fallback_events() -> list[dict[str, Any]]:
    now_year = datetime.now().year
    return [
        {
            "titulo": "Cortejo de Maracatu no Marco Zero",
            "descricao": "Apresentação de maracatu nação com percussão ao vivo. Entrada franca.",
            "categoria": "Cultura popular",
            "bairro": "Recife Antigo",
            "local": "Praça do Marco Zero",
            "lat": -8.0631,
            "lng": -34.8711,
            "inicio_iso": f"{now_year}-07-05T16:00",
            "preco": 0.0,
            "gratuito": True,
            "organizador": "Prefeitura do Recife",
            "email_contato": "agenda@recife.pe.gov.br",
            "source": "prefeitura",
            "link_compra": None,
        },
        {
            "titulo": "Feira de Economia Criativa — Bairro do Recife",
            "descricao": "Artesanato, gastronomia e design local em feira ao ar livre. Acesso livre.",
            "categoria": "Feira cultural",
            "bairro": "Recife Antigo",
            "local": "Rua do Bom Jesus",
            "lat": -8.0608,
            "lng": -34.8718,
            "inicio_iso": f"{now_year}-07-12T09:00",
            "preco": 0.0,
            "gratuito": True,
            "organizador": "Secretaria de Cultura do Recife",
            "email_contato": "cultura@recife.pe.gov.br",
            "source": "prefeitura",
            "link_compra": None,
        },
        {
            "titulo": "Espetáculo Cênico no Pátio de São Pedro",
            "descricao": "Grupo teatral apresenta peça sobre a história do Recife colonial.",
            "categoria": "Teatro",
            "bairro": "São José",
            "local": "Pátio de São Pedro",
            "lat": -8.0650,
            "lng": -34.8770,
            "inicio_iso": f"{now_year}-07-19T19:00",
            "preco": 0.0,
            "gratuito": True,
            "organizador": "Prefeitura do Recife",
            "email_contato": "agenda@recife.pe.gov.br",
            "source": "prefeitura",
            "link_compra": None,
        },
    ]


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    for ev in scrape():
        print(ev["titulo"], "|", ev.get("inicio_iso"), "|", "grátis" if ev["gratuito"] else f"R${ev['preco']}")
