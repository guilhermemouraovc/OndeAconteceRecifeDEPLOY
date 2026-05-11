from typing import Any, Dict, List, Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from ml.classifier import predict_gratuito_pago
from pipeline import process_event_dict

app = FastAPI(title="Onde Acontece Recife", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_EVENTS: List[Dict[str, Any]] = []


def _seed() -> None:
    if _EVENTS:
        return
    base = [
        {
            "titulo": "Cinema ao ar livre na Praça do Arsenal",
            "descricao": "Sessão gratuita com exibição de curtas pernambucanos.",
            "categoria": "cinema",
            "bairro": "boa vista",
            "local": "Praça do Arsenal da Marinha",
            "inicio_iso": "2026-06-15T19:00",
            "preco": 0,
            "gratuito": True,
            "organizador": "Fundação do Patrimônio Histórico",
            "email_contato": "contato@exemplo.org",
        },
        {
            "titulo": "Festival Música na Praça",
            "descricao": "Ingressos a partir de R$ 30 na bilheteria digital.",
            "categoria": "musica",
            "bairro": "boaviagem",
            "local": "Parque Dona Lindu",
            "inicio_iso": "2026-07-20T18:00",
            "preco": 30,
            "gratuito": False,
            "organizador": "Secretaria de Cultura",
            "email_contato": "cultura@exemplo.org",
        },
    ]
    for raw in base:
        row = process_event_dict(raw)
        texto = f"{row.get('titulo', '')} {row.get('descricao', '')}"
        row["classificacao_texto"] = predict_gratuito_pago(texto)
        _EVENTS.append(row)


_seed()


class ClassificarBody(BaseModel):
    texto: str = Field(min_length=1)


class EventCreate(BaseModel):
    titulo: str = Field(min_length=3, max_length=200)
    descricao: str = Field(default="", max_length=4000)
    categoria: Optional[str] = None
    bairro: Optional[str] = None
    local: str = Field(default="", max_length=300)
    inicio_iso: Optional[str] = None
    preco: Optional[float] = None
    gratuito: Optional[bool] = None
    organizador: str = Field(min_length=2, max_length=200)
    email_contato: str = Field(min_length=5, max_length=200)


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.get("/events")
def list_events() -> List[Dict[str, Any]]:
    return list(_EVENTS)


@app.post("/events", status_code=201)
def create_event(body: EventCreate) -> Dict[str, Any]:
    raw = body.model_dump()
    row = process_event_dict(raw)
    texto = f"{row.get('titulo', '')} {row.get('descricao', '')}"
    row["classificacao_texto"] = predict_gratuito_pago(texto)
    _EVENTS.insert(0, row)
    return row


@app.post("/ml/classificar")
def classificar(body: ClassificarBody) -> Dict[str, Any]:
    return predict_gratuito_pago(body.texto)


@app.post("/pipeline/preview")
def pipeline_preview(body: EventCreate) -> Dict[str, Any]:
    """Pré-visualiza o registro após normalização e variáveis derivadas (sem persistir)."""
    return process_event_dict(body.model_dump())


@app.get("/")
def read_root() -> Dict[str, str]:
    return {"message": "Onde Acontece Recife API", "docs": "/docs"}
