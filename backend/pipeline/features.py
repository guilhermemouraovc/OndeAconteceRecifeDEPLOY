from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo


RECIFE_TZ = ZoneInfo("America/Recife")

_DIAS_PT = (
    "segunda-feira",
    "terça-feira",
    "quarta-feira",
    "quinta-feira",
    "sexta-feira",
    "sábado",
    "domingo",
)


def _parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            dt = datetime.strptime(value.strip(), fmt)
            if fmt == "%Y-%m-%d":
                return dt.replace(hour=12, minute=0, tzinfo=RECIFE_TZ)
            return dt.replace(tzinfo=RECIFE_TZ)
        except ValueError:
            continue
    return None


def _faixa_preco(preco: float | None) -> str | None:
    if preco is None:
        return None
    if preco <= 0:
        return "Gratuito"
    if preco <= 30:
        return "Até R$ 30"
    if preco <= 80:
        return "R$ 31–80"
    if preco <= 150:
        return "R$ 81–150"
    return "Acima de R$ 150"


def _periodo_dia(hour: int) -> str:
    if hour < 6:
        return "Madrugada"
    if hour < 12:
        return "Manhã"
    if hour < 18:
        return "Tarde"
    return "Noite"


def add_derived_fields(record: dict) -> dict:
    """
    SCRUM-22: variáveis derivadas (mês, dia da semana, período, faixa de preço).
    """
    out = dict(record)
    inicio = _parse_dt(out.get("inicio_iso") or out.get("inicio"))
    if inicio:
        out["mes"] = inicio.month
        out["dia_semana"] = _DIAS_PT[inicio.weekday()]
        out["periodo_dia"] = _periodo_dia(inicio.hour)
    else:
        out["mes"] = None
        out["dia_semana"] = None
        out["periodo_dia"] = None

    out["faixa_preco"] = _faixa_preco(out.get("preco"))
    return out
