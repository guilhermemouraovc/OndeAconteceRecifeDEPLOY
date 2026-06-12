from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional


def _format_date(value: Optional[str]) -> str:
    if not value:
        return "data a definir"
    try:
        text = value if "T" in value else f"{value}T00:00:00"
        return datetime.fromisoformat(text).strftime("%d/%m %H:%M")
    except ValueError:
        return value


def _format_price(event: Dict[str, Any]) -> str:
    if event.get("gratuito") or event.get("preco") == 0:
        return "gratuito"
    if event.get("preco") is None:
        return "preço não informado"
    return f"R$ {float(event['preco']):.2f}".replace(".", ",")


def build_chat_response(message: str, events: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not events:
        return {
            "resposta": (
                "Nao encontrei eventos aprovados que combinem com sua busca. "
                "Tente perguntar por categoria, bairro ou preco."
            ),
            "eventos_citados": [],
            "fonte": "retrieval",
        }

    lines = ["Encontrei estes eventos aprovados:"]
    for event in events:
        slug = event.get("slug", "")
        lines.append(
            f"- {event.get('titulo')} | {_format_date(event.get('inicio_iso'))} | "
            f"{event.get('local') or event.get('bairro') or 'local a definir'} | "
            f"{_format_price(event)} | /evento/{slug}"
        )

    return {
        "resposta": "\n".join(lines),
        "eventos_citados": events,
        "fonte": "retrieval",
    }
