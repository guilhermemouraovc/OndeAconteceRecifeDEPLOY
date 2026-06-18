from .clean import clean_record
from .features import add_derived_fields
from .geocode import resolve_coordinates
from .normalize import normalize_bairro, normalize_categoria

__all__ = [
    "normalize_bairro",
    "normalize_categoria",
    "clean_record",
    "add_derived_fields",
    "resolve_coordinates",
    "process_event_dict",
]


def process_event_dict(record: dict) -> dict:
    """SCRUM-20/21/22: normaliza, limpa e enriquece um registro de evento."""
    out = clean_record(record)
    out = add_derived_fields(out)
    out = resolve_coordinates(out)
    return out
