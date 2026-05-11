# Onde Acontece Recife

## Tecnologias
- Frontend: Vue.js + Vite
- Backend: FastAPI

## Como rodar

### Backend
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m ml.train_free_paid
uvicorn main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

Opcional: crie `frontend/.env.development` com `VITE_API_BASE_URL=http://127.0.0.1:8000` se a API não estiver na porta padrão.

## Backlog coberto no código
- **SCRUM-20:** `backend/pipeline/normalize.py` + `backend/data/*`
- **SCRUM-21:** `backend/pipeline/clean.py`
- **SCRUM-22:** `backend/pipeline/features.py`
- **SCRUM-14:** `frontend/src/views/CadastroProdutorView.vue` + `POST /events`
- **SCRUM-33:** `backend/ml/` (treino + inferência) + uso em `main.py`