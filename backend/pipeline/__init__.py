from .clean import clean_record
from .features import add_derived_fields
from .normalize import normalize_bairro, normalize_categoria

__all__ = [
    "normalize_bairro",
    "normalize_categoria",
    "clean_record",
    "add_derived_fields",
    "process_event_dict",
]


def process_event_dict(record: dict) -> dict:
    """SCRUM-20/21/22: normaliza, limpa e enriquece um registro de evento."""
    out = clean_record(record)
    out = add_derived_fields(out)
    return out
