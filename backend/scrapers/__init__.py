from __future__ import annotations

import logging
from typing import Any

from .prefeitura import scrape as scrape_prefeitura
from .sympla import scrape as scrape_sympla
from .ticketpe import scrape as scrape_ticketpe

logger = logging.getLogger(__name__)

# Branch feat/ticketpe-2-eventos: apenas integração TicketPE (máx. 2 eventos).
_SOURCES = [
    ("ticketpe", scrape_ticketpe),
]


def run_all(max_per_source: int = 30) -> dict[str, Any]:
    all_events: list[dict] = []
    por_fonte: dict[str, int] = {}
    erros: list[str] = []

    for name, scrape_fn in _SOURCES:
        try:
            events = scrape_fn(max_events=max_per_source)
            all_events.extend(events)
            por_fonte[name] = len(events)
            logger.info("scrapers.run_all: %s → %d eventos", name, len(events))
        except Exception as exc:  # noqa: BLE001
            msg = f"{name}: {exc}"
            erros.append(msg)
            logger.error("scrapers.run_all: erro em %s — %s", name, exc)
            por_fonte[name] = 0

    return {
        "total": len(all_events),
        "por_fonte": por_fonte,
        "events": all_events,
        "erros": erros,
    }


__all__ = ["run_all", "scrape_prefeitura", "scrape_sympla", "scrape_ticketpe"]
