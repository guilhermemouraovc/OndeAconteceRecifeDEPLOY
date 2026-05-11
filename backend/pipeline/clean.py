from __future__ import annotations

from .normalize import normalize_bairro, normalize_categoria


def _strip_empty_strings(d: dict) -> dict:
    return {k: v for k, v in d.items() if not (isinstance(v, str) and v.strip() == "")}


def clean_record(record: dict) -> dict:
    """
    SCRUM-21: limpeza básica, normalização de chaves conhecidas e valores ausentes.
    """
    out = dict(record)
    for key in ("titulo", "descricao", "local", "organizador"):
        if key in out and out[key] is not None:
            out[key] = str(out[key]).strip()

    if "bairro" in out:
        out["bairro"] = normalize_bairro(out.get("bairro"))
    if "categoria" in out:
        out["categoria"] = normalize_categoria(out.get("categoria"))

    if out.get("preco") in ("", None):
        out["preco"] = None
    else:
        try:
            out["preco"] = float(out["preco"])
        except (TypeError, ValueError):
            out["preco"] = None

    if out.get("gratuito") is None and out.get("preco") is not None:
        out["gratuito"] = out["preco"] == 0

    out = _strip_empty_strings(out)
    return out
