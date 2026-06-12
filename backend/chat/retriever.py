from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from unicodedata import normalize


def _normalize(text: Optional[str]) -> str:
    raw = normalize("NFD", text or "")
    cleaned = "".join(c for c in raw if not (0x0300 <= ord(c) <= 0x036F))
    return cleaned.lower().strip()


def _tokens(text: Optional[str]) -> List[str]:
    return [token for token in _normalize(text).replace("/", " ").split() if len(token) > 2]


def _parse_dt(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        text = value.strip()
        if "T" not in text:
            text += "T00:00:00"
        return datetime.fromisoformat(text)
    except ValueError:
        return None


def _matches_date(query: str, event: Dict[str, Any], now: datetime) -> bool:
    dt = _parse_dt(event.get("inicio_iso"))
    if not dt:
        return "hoje" not in query and "amanha" not in query and "fim de semana" not in query

    if "hoje" in query:
        return dt.date() == now.date()
    if "amanha" in query:
        return dt.date() == (now + timedelta(days=1)).date()
    if "fim de semana" in query or "fds" in query:
        return dt.weekday() in (5, 6)
    return True


def _matches_price(query: str, event: Dict[str, Any]) -> bool:
    if not any(term in query for term in ("gratis", "gratuito", "gratuita", "de graca")):
        return True
    return bool(event.get("gratuito")) or event.get("preco") == 0


def score_event(query: str, event: Dict[str, Any], now: Optional[datetime] = None) -> int:
    now = now or datetime.now()
    normalized_query = _normalize(query)
    if not _matches_price(normalized_query, event):
        return -1
    if not _matches_date(normalized_query, event, now):
        return -1

    haystack = _normalize(
        " ".join(
            [
                event.get("titulo", ""),
                event.get("descricao", ""),
                event.get("categoria", ""),
                event.get("bairro", ""),
                event.get("local", ""),
            ]
        )
    )
    tokens = _tokens(query)
    score = sum(3 if token in _normalize(event.get("titulo")) else 1 for token in tokens if token in haystack)

    if any(term in normalized_query for term in ("show", "musica", "música")) and "mus" in _normalize(event.get("categoria")):
        score += 2
    if "teatro" in normalized_query and "teatro" in _normalize(event.get("categoria")):
        score += 2
    if any(term in normalized_query for term in ("gratis", "gratuito", "gratuita", "de graca")) and (
        event.get("gratuito") or event.get("preco") == 0
    ):
        score += 2
    return score


def retrieve_events(query: str, events: List[Dict[str, Any]], limit: int = 3) -> List[Dict[str, Any]]:
    scored: List[Tuple[int, Dict[str, Any]]] = []
    for event in events:
        score = score_event(query, event)
        if score >= 0:
            scored.append((score, event))

    scored.sort(
        key=lambda item: (
            item[0],
            item[1].get("inicio_iso") or "",
            item[1].get("titulo") or "",
        ),
        reverse=True,
    )
    return [event for score, event in scored if score > 0][:limit]
