from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from unicodedata import normalize

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from ml.classifier import predict_gratuito_pago
from pipeline import process_event_dict

app = FastAPI(title="Onde Acontece Recife", version="0.2.0")

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


# ── seed ─────────────────────────────────────────────────────────────────────

def _seed() -> None:
    if _EVENTS:
        return
    base = [
        {
            "titulo": "Cinema ao ar livre na Praça do Arsenal",
            "descricao": "Sessão gratuita com exibição de curtas pernambucanos. Entrada franca para toda a família.",
            "categoria": "Cinema",
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
            "descricao": "Grandes nomes do forró e axé music em um festival ao ar livre. Ingressos a partir de R$ 30 na bilheteria digital.",
            "categoria": "Música ao vivo",
            "bairro": "boaviagem",
            "local": "Parque Dona Lindu",
            "inicio_iso": "2026-07-20T18:00",
            "preco": 30,
            "gratuito": False,
            "organizador": "Secretaria de Cultura",
            "email_contato": "cultura@exemplo.org",
        },
        {
            "titulo": "Sarau Poético Casa Amarela",
            "descricao": "Noite de poesia, música e literatura independente. Evento gratuito e aberto a todos.",
            "categoria": "Literatura",
            "bairro": "casa amarela",
            "local": "Espaço Cultural do Recife",
            "inicio_iso": "2026-06-06T20:00",
            "preco": 0,
            "gratuito": True,
            "organizador": "Coletivo Palavra Viva",
            "email_contato": "palavraviva@exemplo.org",
        },
        {
            "titulo": "Exposição Olhares do Sertão",
            "descricao": "Fotografia documental sobre o cotidiano do sertão pernambucano. Acesso livre.",
            "categoria": "Exposição",
            "bairro": "boa vista",
            "local": "Museu do Estado de Pernambuco",
            "inicio_iso": "2026-06-10T10:00",
            "preco": 0,
            "gratuito": True,
            "organizador": "MEPE",
            "email_contato": "mepe@exemplo.org",
        },
        {
            "titulo": "Espetáculo de Dança Contemporânea",
            "descricao": "Companhia pernambucana apresenta novo espetáculo. Ingressos: R$ 40 inteira, R$ 20 meia.",
            "categoria": "Dança",
            "bairro": "derby",
            "local": "Teatro do Parque",
            "inicio_iso": "2026-06-21T19:30",
            "preco": 40,
            "gratuito": False,
            "organizador": "Cia de Dança Recife",
            "email_contato": "cia@exemplo.org",
        },
        {
            "titulo": "Feira de Artesanato Pernambucano",
            "descricao": "Feira com artesãos locais, gastronomia típica e apresentações musicais. Gratuita.",
            "categoria": "Feira cultural",
            "bairro": "boa viagem",
            "local": "Calçadão de Boa Viagem",
            "inicio_iso": "2026-06-14T09:00",
            "preco": 0,
            "gratuito": True,
            "organizador": "SEBRAE-PE",
            "email_contato": "sebrae@exemplo.org",
        },
        {
            "titulo": "Oficina de Produção Musical",
            "descricao": "Aprenda técnicas de produção musical com instrumentos regionais. Vagas limitadas.",
            "categoria": "Oficina",
            "bairro": "santo amaro",
            "local": "Conservatório Pernambucano de Música",
            "inicio_iso": "2026-06-18T14:00",
            "preco": 50,
            "gratuito": False,
            "organizador": "CPM",
            "email_contato": "cpm@exemplo.org",
        },
        {
            "titulo": "Noite de Teatro de Rua",
            "descricao": "Grupo de teatro apresenta peça sobre a história de Recife nas ruas do bairro. Acesso livre.",
            "categoria": "Teatro",
            "bairro": "recife antigo",
            "local": "Praça do Marco Zero",
            "inicio_iso": "2026-06-20T18:00",
            "preco": 0,
            "gratuito": True,
            "organizador": "Grupo Teatro de Rua",
            "email_contato": "teatro@exemplo.org",
        },
    ]
    for raw in base:
        row = process_event_dict(raw)
        texto = f"{row.get('titulo', '')} {row.get('descricao', '')}"
        row["classificacao_texto"] = predict_gratuito_pago(texto)
        _EVENTS.append(row)


_seed()


# ── helpers ───────────────────────────────────────────────────────────────────

def _slug(text: str) -> str:
    """Gera slug URL-safe a partir de texto (igual ao frontend)."""
    s = normalize("NFD", text or "")
    s = "".join(c for c in s if not (0x0300 <= ord(c) <= 0x036F))
    s = s.lower()
    import re
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def _parse_iso(value: str | None):
    if not value:
        return None
    try:
        s = value.strip()
        if "T" not in s:
            s += "T00:00:00"
        return datetime.fromisoformat(s)
    except ValueError:
        return None


# ── models ────────────────────────────────────────────────────────────────────

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


# ── endpoints ─────────────────────────────────────────────────────────────────

@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.get("/")
def read_root() -> Dict[str, str]:
    return {"message": "Onde Acontece Recife API v0.2", "docs": "/docs"}


# E2-US04 / E2-US05: feed com filtros
@app.get("/events")
def list_events(
    categoria: Optional[str] = Query(None, description="Filtro parcial por categoria"),
    preco: Optional[str] = Query(None, description="gratuito | ate50 | 50a100 | acima100"),
    bairro: Optional[str] = Query(None, description="Filtro parcial por bairro"),
    data: Optional[str] = Query(None, description="hoje | amanha | fds | semana"),
    agora: bool = Query(False, description="Apenas eventos nas próximas 3h"),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
) -> Dict[str, Any]:
    now = datetime.now()
    results = list(_EVENTS)

    # filtro categoria
    if categoria:
        cat_low = categoria.lower()
        results = [e for e in results if cat_low in (e.get("categoria") or "").lower()]

    # filtro preço
    if preco:
        def _preco_ok(e):
            p = e.get("preco")
            gratis = e.get("gratuito") or p == 0
            if preco == "gratuito":
                return gratis
            if p is None:
                return False
            if preco == "ate50":
                return not gratis and p <= 50
            if preco == "50a100":
                return 50 < p <= 100
            if preco == "acima100":
                return p > 100
            return True
        results = [e for e in results if _preco_ok(e)]

    # filtro bairro
    if bairro:
        b_low = bairro.lower()
        results = [e for e in results if b_low in (e.get("bairro") or "").lower()]

    # filtro data
    if data:
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        def _data_ok(e):
            dt = _parse_iso(e.get("inicio_iso"))
            if not dt:
                return False
            if data == "hoje":
                return dt.date() == today.date()
            if data == "amanha":
                from datetime import timedelta
                amanha = (today + timedelta(days=1)).date()
                return dt.date() == amanha
            if data == "fds":
                return dt.weekday() in (5, 6)
            if data == "semana":
                from datetime import timedelta
                return today <= dt <= today + timedelta(days=7)
            return True
        results = [e for e in results if _data_ok(e)]

    # filtro agora (próximas 3h)
    if agora:
        from datetime import timedelta
        limite = now + timedelta(hours=3)
        def _agora_ok(e):
            dt = _parse_iso(e.get("inicio_iso"))
            return dt and now <= dt <= limite
        results = [e for e in results if _agora_ok(e)]

    # paginação
    total = len(results)
    start = (page - 1) * per_page
    paginated = results[start: start + per_page]

    return {
        "total": total,
        "page": page,
        "per_page": per_page,
        "results": paginated,
    }


# E2-US08: detalhe do evento por slug
@app.get("/events/{slug}")
def get_event(slug: str) -> Dict[str, Any]:
    for ev in _EVENTS:
        if _slug(ev.get("titulo", "")) == slug:
            return ev
    raise HTTPException(status_code=404, detail="Evento não encontrado.")


@app.post("/events", status_code=201)
def create_event(body: EventCreate) -> Dict[str, Any]:
    raw = body.model_dump()
    row = process_event_dict(raw)
    texto = f"{row.get('titulo', '')} {row.get('descricao', '')}"
    row["classificacao_texto"] = predict_gratuito_pago(texto)
    _EVENTS.insert(0, row)
    return row


# E2-US04: bairros disponíveis para popular o filtro
@app.get("/meta/bairros")
def get_bairros() -> List[str]:
    seen = set()
    result = []
    for ev in _EVENTS:
        b = ev.get("bairro")
        if b and b not in seen:
            seen.add(b)
            result.append(b)
    return sorted(result)


# E2-US04: categorias disponíveis
@app.get("/meta/categorias")
def get_categorias() -> List[str]:
    seen = set()
    result = []
    for ev in _EVENTS:
        c = ev.get("categoria")
        if c and c not in seen:
            seen.add(c)
            result.append(c)
    return sorted(result)


@app.post("/ml/classificar")
def classificar(body: ClassificarBody) -> Dict[str, Any]:
    return predict_gratuito_pago(body.texto)


@app.post("/pipeline/preview")
def pipeline_preview(body: EventCreate) -> Dict[str, Any]:
    """Pré-visualiza o registro após normalização e variáveis derivadas (sem persistir)."""
    return process_event_dict(body.model_dump())