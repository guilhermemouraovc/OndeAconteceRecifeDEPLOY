from __future__ import annotations

import json
import unicodedata
from functools import lru_cache
from pathlib import Path

_DATA = Path(__file__).resolve().parent.parent / "data"


def _normalize_key(value: str | None) -> str:
    if not value:
        return ""
    text = unicodedata.normalize("NFD", str(value).strip().lower())
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    return " ".join(text.split())


@lru_cache
def _locais_recife() -> dict:
    path = _DATA / "locais_recife.json"
    if not path.exists():
        return {"venues": {}, "bairros": {}}
    return json.loads(path.read_text(encoding="utf-8"))


def _lookup(mapping: dict[str, dict], *candidates: str | None) -> dict[str, float] | None:
    for candidate in candidates:
        key = _normalize_key(candidate)
        if key and key in mapping:
            point = mapping[key]
            return {"lat": float(point["lat"]), "lng": float(point["lng"])}

    for candidate in candidates:
        key = _normalize_key(candidate)
        if not key:
            continue
        for known, point in mapping.items():
            if known in key or key in known:
                return {"lat": float(point["lat"]), "lng": float(point["lng"])}
    return None


def resolve_coordinates(record: dict) -> dict:
    """Preenche lat/lng ausentes com base em local ou bairro conhecidos de Recife."""
    out = dict(record)
    if out.get("lat") is not None and out.get("lng") is not None:
        return out

    data = _locais_recife()
    point = _lookup(
        data.get("venues", {}),
        out.get("local"),
        out.get("titulo"),
    ) or _lookup(
        data.get("bairros", {}),
        out.get("bairro"),
        out.get("local"),
    )

    if point:
        out.setdefault("lat", point["lat"])
        out.setdefault("lng", point["lng"])

    return out
