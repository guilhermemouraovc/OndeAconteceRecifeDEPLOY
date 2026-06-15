from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

DATA_PATH = Path(__file__).parent / "data" / "events.json"

app = FastAPI(title="TicketPE Mock API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def _load_events() -> list[dict[str, Any]]:
    return json.loads(DATA_PATH.read_text(encoding="utf-8"))


@app.get("/")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "ticketpe-mock"}


@app.get("/api/v1/events")
def list_events(
    city: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=100),
) -> dict[str, Any]:
    events = _load_events()

    if city:
        city_norm = city.strip().lower()
        events = [e for e in events if str(e.get("city", "")).lower() == city_norm]

    return {"data": events[:limit]}


@app.get("/api/v1/events/{slug}")
def get_event(slug: str) -> dict[str, Any]:
    for event in _load_events():
        if event.get("slug") == slug:
            return {"data": event}
    return {"data": None, "message": "Evento não encontrado"}
