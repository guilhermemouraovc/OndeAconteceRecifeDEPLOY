from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from difflib import get_close_matches

_DATA = Path(__file__).resolve().parent.parent / "data"


@lru_cache
def _bairros_aliases() -> dict[str, str]:
    path = _DATA / "bairros_aliases.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


@lru_cache
def _categorias_padrao() -> list[str]:
    path = _DATA / "categorias_padrao.json"
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_bairro(raw: str | None) -> str | None:
    """SCRUM-20: padroniza nome de bairro com mapa + aproximação leve."""
    if raw is None:
        return None
    s = " ".join(str(raw).strip().lower().split())
    if not s:
        return None
    aliases = _bairros_aliases()
    if s in aliases:
        return aliases[s]
    close = get_close_matches(s, list(aliases.keys()), n=1, cutoff=0.82)
    if close:
        return aliases[close[0]]
    return raw.strip().title()


def normalize_categoria(raw: str | None) -> str | None:
    """SCRUM-20: encaixa categoria livre na lista municipal/projeto."""
    if raw is None:
        return None
    s = str(raw).strip()
    if not s:
        return None
    canon = _categorias_padrao()
    low = s.lower()
    for c in canon:
        if c.lower() == low:
            return c
    close = get_close_matches(s, canon, n=1, cutoff=0.55)
    if close:
        return close[0]
    return "Outros"
