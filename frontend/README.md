# Onde Acontece Recife — Frontend

SPA em **Vue 3 + Quasar** com visual inspirado no ttpe-webapp e identidade própria (paleta teal/gold, Fraunces).

## Rodar

```bash
npm install
npm run dev
```

App em `http://localhost:9000` (Quasar dev server).

## Build

```bash
npm run build
```

Saída em `dist/spa/`.

## Variáveis de ambiente

Copie `.env.example` para `.env`:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
VITE_MAPBOX_TOKEN=pk.eyJ1...
```

## Estrutura

- `src/layouts/MainLayout.vue` — shell com nav, busca e filtros
- `src/pages/` — rotas da aplicação
- `src/stores/events.js` — feed, filtros e favoritos (Pinia)
- `src/utils/eventMapper.js` — adapta API FastAPI → modelo dos cards
