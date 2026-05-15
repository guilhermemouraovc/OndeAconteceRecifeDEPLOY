# Onde Acontece Recife

Plataforma web progressiva (PWA) para descoberta de eventos culturais em Recife. Agrega eventos da Prefeitura, produtores independentes e plataformas como TicketPE em um feed centralizado com filtros inteligentes.


## Tecnologias

- **Frontend:** Vue.js 3 + Vite + Pinia + Vue Router
- **Backend:** FastAPI + Python 3.11+
- **ML/Pipeline:** scikit-learn, pandas, joblib

## Como rodar

### Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m ml.train_free_paid
uvicorn main:app --reload
```

API disponível em `http://localhost:8000` — documentação automática em `http://localhost:8000/docs`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

App disponível em `http://localhost:5173`.

Opcional: crie `frontend/.env.development` com `VITE_API_BASE_URL=http://127.0.0.1:8000` se a API não estiver na porta padrão.

## Funcionalidades implementadas

- Feed de eventos com filtros por categoria, preço, bairro e data
- Modo "O que tá rolando agora?" com auto-refresh a cada 5 minutos
- Página de detalhe do evento com dados do pipeline de ML
- Favoritos persistidos em localStorage
- Cadastro autônomo de eventos por produtores culturais
- Classificador automático gratuito/pago por texto (heurística + modelo treinado)
- Pipeline de normalização de bairros, categorias e variáveis derivadas

## Backlog coberto no código

| Ticket | Arquivo |
|---|---|
| SCRUM-12 | `frontend/src/views/HomeView.vue`, `frontend/src/components/FilterBar.vue`, `frontend/src/stores/events.js` |
| SCRUM-14 | `frontend/src/views/CadastroProdutorView.vue`, `POST /events` |
| SCRUM-20 | `backend/pipeline/normalize.py`, `backend/data/` |
| SCRUM-21 | `backend/pipeline/clean.py` |
| SCRUM-22 | `backend/pipeline/features.py` |
| SCRUM-33 | `backend/ml/` (treino + inferência) |
