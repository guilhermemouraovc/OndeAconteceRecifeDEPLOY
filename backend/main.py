from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from unicodedata import normalize

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from ml.classifier import predict_gratuito_pago
from pipeline import process_event_dict
from scrapers import run_all as _run_scrapers

app = FastAPI(title="Onde Acontece Recife", version="0.3.0")

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
            "descricao": "Sessão gratuita com exibição de curtas pernambucanos. Entrada franca para toda a família.",
            "categoria": "Cinema",
            "bairro": "boa vista",
            "local": "Praça do Arsenal da Marinha",
            "lat": -8.0631,
            "lng": -34.8710,
            "inicio_iso": "2026-06-15T19:00",
            "preco": 0,
            "gratuito": True,
            "organizador": "Fundação do Patrimônio Histórico",
            "email_contato": "contato@exemplo.org",
            "source": "manual",
            "link_compra": None,
        },
        {
            "titulo": "Festival Música na Praça",
            "descricao": "Grandes nomes do forró e axé music em um festival ao ar livre. Ingressos a partir de R$ 30 na bilheteria digital.",
            "categoria": "Música ao vivo",
            "bairro": "boa viagem",
            "local": "Parque Dona Lindu",
            "lat": -8.1225,
            "lng": -34.9003,
            "inicio_iso": "2026-07-20T18:00",
            "preco": 30,
            "gratuito": False,
            "organizador": "Secretaria de Cultura",
            "email_contato": "cultura@exemplo.org",
            "source": "manual",
            "link_compra": "https://www.ticketpe.com.br",
        },
        {
            "titulo": "Sarau Poético Casa Amarela",
            "descricao": "Noite de poesia, música e literatura independente. Evento gratuito e aberto a todos.",
            "categoria": "Literatura",
            "bairro": "casa amarela",
            "local": "Espaço Cultural do Recife",
            "lat": -8.0340,
            "lng": -34.9190,
            "inicio_iso": "2026-06-06T20:00",
            "preco": 0,
            "gratuito": True,
            "organizador": "Coletivo Palavra Viva",
            "email_contato": "palavraviva@exemplo.org",
            "source": "manual",
            "link_compra": None,
        },
        {
            "titulo": "Exposição Olhares do Sertão",
            "descricao": "Fotografia documental sobre o cotidiano do sertão pernambucano. Acesso livre.",
            "categoria": "Exposição",
            "bairro": "boa vista",
            "local": "Museu do Estado de Pernambuco",
            "lat": -8.0570,
            "lng": -34.8990,
            "inicio_iso": "2026-06-10T10:00",
            "preco": 0,
            "gratuito": True,
            "organizador": "MEPE",
            "email_contato": "mepe@exemplo.org",
            "source": "manual",
            "link_compra": None,
        },
        {
            "titulo": "Espetáculo de Dança Contemporânea",
            "descricao": "Companhia pernambucana apresenta novo espetáculo. Ingressos: R$ 40 inteira, R$ 20 meia.",
            "categoria": "Dança",
            "bairro": "derby",
            "local": "Teatro do Parque",
            "lat": -8.0530,
            "lng": -34.8950,
            "inicio_iso": "2026-06-21T19:30",
            "preco": 40,
            "gratuito": False,
            "organizador": "Cia de Dança Recife",
            "email_contato": "cia@exemplo.org",
            "source": "manual",
            "link_compra": "https://www.ticketpe.com.br",
        },
        {
            "titulo": "Feira de Artesanato Pernambucano",
            "descricao": "Feira com artesãos locais, gastronomia típica e apresentações musicais. Gratuita.",
            "categoria": "Feira cultural",
            "bairro": "boa viagem",
            "local": "Calçadão de Boa Viagem",
            "lat": -8.1195,
            "lng": -34.8997,
            "inicio_iso": "2026-06-14T09:00",
            "preco": 0,
            "gratuito": True,
            "organizador": "SEBRAE-PE",
            "email_contato": "sebrae@exemplo.org",
            "source": "manual",
            "link_compra": None,
        },
        {
            "titulo": "Oficina de Produção Musical",
            "descricao": "Aprenda técnicas de produção musical com instrumentos regionais. Vagas limitadas.",
            "categoria": "Oficina",
            "bairro": "santo amaro",
            "local": "Conservatório Pernambucano de Música",
            "lat": -8.0620,
            "lng": -34.8870,
            "inicio_iso": "2026-06-18T14:00",
            "preco": 50,
            "gratuito": False,
            "organizador": "CPM",
            "email_contato": "cpm@exemplo.org",
            "source": "manual",
            "link_compra": None,
        },
        {
            "titulo": "Noite de Teatro de Rua",
            "descricao": "Grupo de teatro apresenta peça sobre a história de Recife nas ruas do bairro. Acesso livre.",
            "categoria": "Teatro",
            "bairro": "recife antigo",
            "local": "Praça do Marco Zero",
            "lat": -8.0631,
            "lng": -34.8711,
            "inicio_iso": "2026-06-20T18:00",
            "preco": 0,
            "gratuito": True,
            "organizador": "Grupo Teatro de Rua",
            "email_contato": "teatro@exemplo.org",
            "source": "manual",
            "link_compra": None,
        },
        {
            "titulo": "Frevo nas Ruas do Recife Antigo",
            "descricao": "Apresentação de frevo com guarda-sóis coloridos e passistas na rua mais animada do bairro histórico.",
            "categoria": "Música ao vivo",
            "bairro": "recife antigo",
            "local": "Rua do Bom Jesus",
            "lat": -8.0608,
            "lng": -34.8718,
            "inicio_iso": "2026-06-07T17:00",
            "preco": 0,
            "gratuito": True,
            "organizador": "Prefeitura do Recife",
            "email_contato": "cultura@recife.pe.gov.br",
            "source": "prefeitura",
            "link_compra": None,
        },
        {
            "titulo": "Show de Forró no Pátio de São Pedro",
            "descricao": "Uma das praças mais bonitas do Recife recebe grandes nomes do forró pé-de-serra. Ingressos limitados.",
            "categoria": "Música ao vivo",
            "bairro": "são josé",
            "local": "Pátio de São Pedro",
            "lat": -8.0650,
            "lng": -34.8770,
            "inicio_iso": "2026-06-13T19:00",
            "preco": 25,
            "gratuito": False,
            "organizador": "Associação Cultural São Pedro",
            "email_contato": "saopedro@exemplo.org",
            "source": "ticketpe",
            "link_compra": "https://www.ticketpe.com.br",
        },
        {
            "titulo": "Feira Gastronômica Sabores de Pernambuco",
            "descricao": "Chefs e cozinheiras tradicionais apresentam a culinária pernambucana em um evento ao ar livre.",
            "categoria": "Gastronomia",
            "bairro": "graças",
            "local": "Parque Jaqueira",
            "lat": -8.0430,
            "lng": -34.9020,
            "inicio_iso": "2026-06-22T11:00",
            "preco": 0,
            "gratuito": True,
            "organizador": "Associação de Gastronomia PE",
            "email_contato": "gastro@exemplo.org",
            "source": "manual",
            "link_compra": None,
        },
        {
            "titulo": "Noite de Jazz no Cais do Sertão",
            "descricao": "Quarteto de jazz fusionado com ritmos nordestinos. Vista para o Rio Capibaribe.",
            "categoria": "Música ao vivo",
            "bairro": "recife antigo",
            "local": "Cais do Sertão",
            "lat": -8.0645,
            "lng": -34.8700,
            "inicio_iso": "2026-06-27T20:00",
            "preco": 35,
            "gratuito": False,
            "organizador": "Cais do Sertão Museu",
            "email_contato": "cais@exemplo.org",
            "source": "ticketpe",
            "link_compra": "https://www.ticketpe.com.br",
        },
        {
            "titulo": "Exposição de Arte Contemporânea Nordestina",
            "descricao": "Coletivo de artistas plásticos pernambucanos expõe obras que dialogam com a identidade do Nordeste.",
            "categoria": "Exposição",
            "bairro": "boa viagem",
            "local": "Galeria Ignácio Ferreira",
            "lat": -8.1170,
            "lng": -34.9015,
            "inicio_iso": "2026-06-05T10:00",
            "preco": 0,
            "gratuito": True,
            "organizador": "Coletivo Arte Nordeste",
            "email_contato": "artenordeste@exemplo.org",
            "source": "manual",
            "link_compra": None,
        },
        {
            "titulo": "Peça Infantil: A Lenda do Bumba-meu-boi",
            "descricao": "Espetáculo teatral para crianças baseado na tradicional lenda nordestina com figurinos coloridos e muita animação.",
            "categoria": "Teatro",
            "bairro": "boa vista",
            "local": "Teatro do SESC Capibaribe",
            "lat": -8.0555,
            "lng": -34.9005,
            "inicio_iso": "2026-06-08T15:00",
            "preco": 20,
            "gratuito": False,
            "organizador": "SESC Pernambuco",
            "email_contato": "sesc@exemplo.org",
            "source": "sympla",
            "link_compra": "https://www.sympla.com.br",
        },
        {
            "titulo": "Corrida Noturna Orla de Boa Viagem",
            "descricao": "5km e 10km com saída na Praça de Boa Viagem. Inscrição inclui camiseta e kit do corredor.",
            "categoria": "Esportes",
            "bairro": "boa viagem",
            "local": "Praça de Boa Viagem",
            "lat": -8.1260,
            "lng": -34.9010,
            "inicio_iso": "2026-06-12T19:30",
            "preco": 60,
            "gratuito": False,
            "organizador": "Recife Runners",
            "email_contato": "runners@exemplo.org",
            "source": "sympla",
            "link_compra": "https://www.sympla.com.br",
        },
        {
            "titulo": "Workshop de Xilogravura",
            "descricao": "Aprenda a técnica da xilogravura com um mestre gravurista do cordel pernambucano. Material incluso.",
            "categoria": "Oficina",
            "bairro": "olinda",
            "local": "Espaço Cultural Cariri",
            "lat": -7.9983,
            "lng": -34.8455,
            "inicio_iso": "2026-06-17T09:00",
            "preco": 80,
            "gratuito": False,
            "organizador": "Mestre Xilogravura PE",
            "email_contato": "xilope@exemplo.org",
            "source": "manual",
            "link_compra": None,
        },
        {
            "titulo": "Roda de Capoeira Mestre Pastinha",
            "descricao": "Roda aberta de capoeira angola em homenagem ao Mestre Pastinha. Todos os níveis bem-vindos.",
            "categoria": "Cultura popular",
            "bairro": "afogados",
            "local": "Centro Comunitário Afogados",
            "lat": -8.0880,
            "lng": -34.9120,
            "inicio_iso": "2026-06-21T10:00",
            "preco": 0,
            "gratuito": True,
            "organizador": "Grupo de Capoeira Raízes",
            "email_contato": "capoeira@exemplo.org",
            "source": "manual",
            "link_compra": None,
        },
        {
            "titulo": "Mostra de Cinema Pernambucano",
            "descricao": "Seleção de curtas e médias-metragens produzidos no estado nos últimos dois anos. Sessões com debate.",
            "categoria": "Cinema",
            "bairro": "derby",
            "local": "Cinema São Luiz",
            "lat": -8.0542,
            "lng": -34.8975,
            "inicio_iso": "2026-06-19T18:30",
            "preco": 15,
            "gratuito": False,
            "organizador": "Associação Pernambucana de Cinema",
            "email_contato": "cinepe@exemplo.org",
            "source": "sympla",
            "link_compra": "https://www.sympla.com.br",
        },
        {
            "titulo": "Festival de Literatura de Cordel",
            "descricao": "Repentistas, cordelistas e poetas populares se encontram na maior festa da literatura de cordel do Recife.",
            "categoria": "Literatura",
            "bairro": "são josé",
            "local": "Mercado de São José",
            "lat": -8.0668,
            "lng": -34.8795,
            "inicio_iso": "2026-06-28T09:00",
            "preco": 0,
            "gratuito": True,
            "organizador": "Liga dos Cordelistas de PE",
            "email_contato": "cordel@exemplo.org",
            "source": "prefeitura",
            "link_compra": None,
        },
        {
            "titulo": "Baile de Coco Recifense",
            "descricao": "Dança e música do coco de roda com grupos tradicionais de Pernambuco. Animação garantida para toda a família.",
            "categoria": "Cultura popular",
            "bairro": "casa amarela",
            "local": "Praça do Entroncamento",
            "lat": -8.0310,
            "lng": -34.9250,
            "inicio_iso": "2026-06-26T17:00",
            "preco": 0,
            "gratuito": True,
            "organizador": "Movimento Cultural Casa Amarela",
            "email_contato": "casaamarela@exemplo.org",
            "source": "manual",
            "link_compra": None,
        },
        {
            "titulo": "Encontro de DJs Eletrônicos de Recife",
            "descricao": "Noite de música eletrônica com DJs locais que misturam ritmos nordestinos a house e techno.",
            "categoria": "Música ao vivo",
            "bairro": "boa viagem",
            "local": "Espaço Parque",
            "lat": -8.1140,
            "lng": -34.9030,
            "inicio_iso": "2026-06-28T22:00",
            "preco": 45,
            "gratuito": False,
            "organizador": "Coletivo Manguetronic",
            "email_contato": "manguetronic@exemplo.org",
            "source": "ticketpe",
            "link_compra": "https://www.ticketpe.com.br",
        },
        {
            "titulo": "Palestra: Empreendedorismo Cultural em Pernambuco",
            "descricao": "Debate com produtores culturais locais sobre financiamento, editais e sustentabilidade de projetos culturais.",
            "categoria": "Palestras",
            "bairro": "graças",
            "local": "Auditório SEBRAE Recife",
            "lat": -8.0468,
            "lng": -34.9012,
            "inicio_iso": "2026-06-11T14:00",
            "preco": 0,
            "gratuito": True,
            "organizador": "SEBRAE-PE",
            "email_contato": "sebrae@exemplo.org",
            "source": "sympla",
            "link_compra": "https://www.sympla.com.br",
        },
    ]
    for raw in base:
        row = process_event_dict(raw)
        for extra_key in ("lat", "lng", "source", "link_compra"):
            if extra_key in raw:
                row[extra_key] = raw[extra_key]
        texto = f"{row.get('titulo', '')} {row.get('descricao', '')}"
        row["classificacao_texto"] = predict_gratuito_pago(texto)
        _EVENTS.append(row)


_seed()



def _slug(text: str) -> str:
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



class ClassificarBody(BaseModel):
    texto: str = Field(min_length=1)


class EventCreate(BaseModel):
    titulo: str = Field(min_length=3, max_length=200)
    descricao: str = Field(default="", max_length=4000)
    categoria: Optional[str] = None
    bairro: Optional[str] = None
    local: str = Field(default="", max_length=300)
    lat: Optional[float] = None
    lng: Optional[float] = None
    inicio_iso: Optional[str] = None
    preco: Optional[float] = None
    gratuito: Optional[bool] = None
    organizador: str = Field(min_length=2, max_length=200)
    email_contato: str = Field(min_length=5, max_length=200)
    source: Optional[str] = None      
    link_compra: Optional[str] = None    


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.get("/")
def read_root() -> Dict[str, str]:
    return {"message": "Onde Acontece Recife API v0.3", "docs": "/docs"}


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

    if categoria:
        cat_low = categoria.lower()
        results = [e for e in results if cat_low in (e.get("categoria") or "").lower()]
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

    if bairro:
        b_low = bairro.lower()
        results = [e for e in results if b_low in (e.get("bairro") or "").lower()]

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

    if agora:
        from datetime import timedelta
        limite = now + timedelta(hours=3)
        def _agora_ok(e):
            dt = _parse_iso(e.get("inicio_iso"))
            return dt and now <= dt <= limite
        results = [e for e in results if _agora_ok(e)]

    total = len(results)
    start = (page - 1) * per_page
    paginated = results[start: start + per_page]

    return {
        "total": total,
        "page": page,
        "per_page": per_page,
        "results": paginated,
    }


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
    for extra_key in ("lat", "lng", "source", "link_compra"):
        if raw.get(extra_key) is not None:
            row[extra_key] = raw[extra_key]
    texto = f"{row.get('titulo', '')} {row.get('descricao', '')}"
    row["classificacao_texto"] = predict_gratuito_pago(texto)
    _EVENTS.insert(0, row)
    return row


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


@app.post("/scraper/run")
def scraper_run(max_por_fonte: int = 30) -> Dict[str, Any]:
    result = _run_scrapers(max_per_source=max_por_fonte)
    raw_events: list[Dict[str, Any]] = result.get("events", [])

    titulos_existentes = {ev.get("titulo", "").lower() for ev in _EVENTS}
    adicionados = 0

    for raw in raw_events:
        titulo_key = (raw.get("titulo") or "").lower()
        if titulo_key in titulos_existentes:
            continue  # deduplicação simples por título
        row = process_event_dict(raw)
        for extra_key in ("lat", "lng", "source", "link_compra"):
            if raw.get(extra_key) is not None:
                row[extra_key] = raw[extra_key]
        texto = f"{row.get('titulo', '')} {row.get('descricao', '')}"
        row["classificacao_texto"] = predict_gratuito_pago(texto)
        _EVENTS.append(row)
        titulos_existentes.add(titulo_key)
        adicionados += 1

    return {
        "adicionados": adicionados,
        "ignorados_duplicados": len(raw_events) - adicionados,
        "por_fonte": result.get("por_fonte", {}),
        "erros": result.get("erros", []),
        "total_em_memoria": len(_EVENTS),
    }


@app.post("/pipeline/preview")
def pipeline_preview(body: EventCreate) -> Dict[str, Any]:
    return process_event_dict(body.model_dump())