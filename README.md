# Onde Acontece Recife

PWA para descoberta de eventos culturais em Recife. Agrega conteúdo da Prefeitura do Recife, produtores independentes e plataformas como TicketPE e Sympla em um feed centralizado com filtros inteligentes, mapa interativo e chatbot por IA.

---

## Sumário

- [Tecnologias](#tecnologias)
- [Como rodar](#como-rodar)
- [Variáveis de ambiente](#variáveis-de-ambiente)
- [Funcionalidades](#funcionalidades)
- [Estrutura do projeto](#estrutura-do-projeto)
- [Modelo de evento](#modelo-de-evento)
- [Rotas do frontend](#rotas-do-frontend)
- [Endpoints da API](#endpoints-da-api)
- [Backlog coberto](#backlog-coberto)

---

## Tecnologias

| Camada | Stack |
|---|---|
| Frontend | Vue.js 3 + Quasar + Pinia + Vue Router |
| Backend | FastAPI + Python 3.11+ |
| ML / Pipeline | scikit-learn, pandas, joblib |
| Mapa | Mapbox GL JS v3 (CDN, token obrigatório) |
| Scrapers | httpx + BeautifulSoup4 (Prefeitura, Sympla, TicketPE) |
| Chatbot | Integração via `chat/` com retriever semântico de eventos |

---

## Como rodar

### Pré-requisitos

- Python 3.11+
- Node.js 18+
- npm

### Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m ml.train_free_paid    # treina o classificador gratuito/pago
uvicorn main:app --reload
```

API disponível em `http://localhost:8000`  
Documentação interativa (Swagger): `http://localhost:8000/docs`

### Frontend

```bash
cd frontend
npm install
npm run dev
```

App disponível em `http://localhost:9000`

### Mock TicketPE (opcional)

O projeto inclui um servidor mock local para simular a API do TicketPE durante o desenvolvimento:

```bash
cd mock-ticketpe
pip install -r requirements.txt
bash run.sh
```

---

## Variáveis de ambiente

Crie o arquivo `frontend/.env` a partir do exemplo:

```bash
cp frontend/.env.example frontend/.env
```

| Variável | Obrigatório | Descrição |
|---|---|---|
| `VITE_API_BASE_URL` | Não | URL da API (padrão: `http://localhost:8000`) |
| `VITE_MAPBOX_TOKEN` | Sim (para `/mapa`) | Token público Mapbox — começa com `pk.eyJ1...` |

> Sem o `VITE_MAPBOX_TOKEN`, a rota `/mapa` exibe mensagem de erro amigável. O restante do app funciona normalmente.

Para o backend, copie também:

```bash
cp backend/.env.example backend/.env
```

---

## Funcionalidades

### Feed e filtros
- Feed paginado de eventos com filtros combinados por categoria, preço, bairro e data
- Modo **"O que tá rolando agora?"** com auto-refresh a cada 5 minutos
- Skeleton loading, estado vazio e tratamento de erro

### Mapa interativo
- Rota `/mapa` com mapa Mapbox GL JS em dark mode centrado em Recife
- Marcadores coloridos por categoria com popup de detalhes
- Botão "Usar minha localização" com animação fly-to
- Link direto do popup para a página de detalhe do evento
- Legenda de categorias

### Detalhe do evento
- Página dedicada por slug com todas as informações do evento
- Botão "Comprar ingresso" (exibido automaticamente quando `link_compra` está preenchido)
- Badge de fonte: **via TicketPE**, **via Sympla**, **via Prefeitura do Recife**
- Botão "Como chegar" — abre Google Maps com endereço pré-preenchido
- Compartilhamento via Web Share API ou cópia de link
- Badge de confiança da classificação por IA

### Dados e ML
- 22 eventos no seed com coordenadas geográficas reais
- Classificador automático gratuito/pago por texto (heurística + modelo treinado com scikit-learn)
- Pipeline de normalização de bairros, categorias e variáveis derivadas
- Endpoint `/pipeline/preview` para pré-visualizar normalização sem persistir

### Scrapers
- Scrapers para **TicketPE**, **Sympla** e **Prefeitura do Recife**
- Endpoint `POST /scraper/run` para disparar scraping via interface web
- Página `/scraper` no frontend com feedback de execução

### Chatbot
- Widget flutuante com chatbot baseado em IA
- Retriever semântico de eventos para respostas contextualizadas

### Produtores e favoritos
- Formulário de cadastro autônomo de eventos por produtores culturais (com upload de flyer)
- Fila de moderação de eventos enviados por produtores (`/moderacao`)
- Favoritos persistidos em localStorage com contador no nav

---

## Estrutura do projeto

```
OndeAconteceRecife/
├── backend/
│   ├── chat/               # Chatbot: retriever semântico + responder
│   ├── data/               # Seed de eventos, aliases de bairros, categorias
│   ├── ml/                 # Classificador gratuito/pago (scikit-learn)
│   ├── pipeline/           # Normalização: clean → features → normalize
│   ├── scrapers/           # Scrapers: prefeitura, sympla, ticketpe
│   ├── storage/            # EventsStore (persistência em JSON)
│   ├── uploads/            # Flyers enviados por produtores
│   ├── main.py             # FastAPI app + todos os endpoints
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── components/     # EventCard, SkeletonLoader, PageHeader, etc.
│       ├── composables/    # useApi, useEventsApi, useChatbot, etc.
│       ├── constants/      # config.js (URLs, constantes)
│       ├── layouts/        # MainLayout.vue (nav + chatbot widget)
│       ├── pages/          # Uma view por rota
│       ├── router/         # Vue Router
│       ├── stores/         # Pinia: events.js
│       └── utils/          # eventMapper, eventSorting, stringUtils
├── mock-ticketpe/          # Servidor mock da API TicketPE
└── test-evidence/          # Screenshots, relatório de ciclo e scripts de evidência
```

---

## Modelo de evento

| Campo | Tipo | Descrição |
|---|---|---|
| `titulo` | string | Nome do evento |
| `descricao` | string | Descrição completa |
| `categoria` | string | Ex: `"Música ao vivo"`, `"Teatro"`, `"Exposição"` |
| `bairro` | string | Bairro normalizado pelo pipeline |
| `local` | string | Nome do espaço ou endereço |
| `lat` / `lng` | float | Coordenadas geográficas (usadas pelo mapa) |
| `inicio_iso` | string | Data e hora no formato ISO 8601 |
| `preco` | float | Valor em reais (0 = gratuito) |
| `gratuito` | bool | Flag explícita de gratuidade |
| `organizador` | string | Nome do organizador ou produtora |
| `email_contato` | string | E-mail de contato |
| `source` | string | Origem: `ticketpe`, `sympla`, `prefeitura`, `manual` |
| `link_compra` | string \| null | URL externa de compra de ingressos |

---

## Rotas do frontend

| Rota | View | Descrição |
|---|---|---|
| `/` | `IndexPage` | Feed com filtros e hero |
| `/programacao` | `ProgramacaoPage` | Programação completa |
| `/mapa` | `MapaPage` | Mapa interativo Mapbox |
| `/evento/:slug` | `EventDetailPage` | Detalhe do evento |
| `/cadastro` | `CadastroProdutorPage` | Formulário para produtores |
| `/favoritos` | `FavoritosPage` | Eventos salvos |
| `/moderacao` | `ModeracaoPage` | Fila de moderação |
| `/scraper` | `ScraperPage` | Painel de execução dos scrapers |

---

## Endpoints da API

| Método | Rota | Descrição |
|---|---|---|
| `GET` | `/events` | Feed com filtros e paginação |
| `GET` | `/events/{slug}` | Detalhe de um evento |
| `POST` | `/events` | Cadastro de novo evento (com upload de flyer) |
| `GET` | `/meta/bairros` | Lista de bairros disponíveis |
| `GET` | `/meta/categorias` | Lista de categorias disponíveis |
| `POST` | `/ml/classificar` | Classifica texto como gratuito/pago |
| `POST` | `/pipeline/preview` | Pré-visualiza normalização sem persistir |
| `POST` | `/scraper/run` | Dispara scraping de todas as fontes |
| `POST` | `/chat` | Envia mensagem ao chatbot |

**Parâmetros de `/events`:**

| Parâmetro | Valores aceitos |
|---|---|
| `categoria` | string livre |
| `preco` | `gratuito` \| `ate50` \| `50a100` \| `acima100` |
| `bairro` | string livre |
| `data` | `hoje` \| `amanha` \| `fds` \| `semana` |
| `agora` | `true` (filtra eventos em andamento agora) |
| `page` / `per_page` | inteiros (paginação) |

---

## Backlog coberto

| Ticket | Épico | Arquivo principal |
|---|---|---|
| E1-US01 | Setup & Infraestrutura | `backend/main.py`, `frontend/src/` |
| E2-US04 / US05 | Feed + filtros | `IndexPage.vue`, `stores/events.js` |
| E2-US06 | Mapa interativo | `MapaPage.vue` |
| E2-US07 | Modo "Agora" | `IndexPage.vue`, `stores/events.js` |
| E2-US08 | Detalhe do evento | `EventDetailPage.vue`, `GET /events/{slug}` |
| E2-US10 | Favoritos | `FavoritosPage.vue`, `stores/events.js` |
| E3-US11 | Scrapers Sympla + Prefeitura + TicketPE | `backend/scrapers/` |
| E3-US12 | Cadastro por produtores | `CadastroProdutorPage.vue`, `POST /events` |
| E3-US13 | Pipeline de limpeza | `backend/pipeline/` |
| E4-US17 | Classificador gratuito/pago | `backend/ml/` |
| E5-US20 | Moderação de eventos | `ModeracaoPage.vue` |
| E5-US21 | Chatbot de eventos | `MainLayout.vue`, `backend/chat/` |
