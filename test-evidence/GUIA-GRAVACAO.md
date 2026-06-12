# Guia de gravação — Onde Acontece Recife

Roteiro de **5 a 8 minutos** cobrindo **US20 → US21 → US23**.

---

## Antes de gravar

### 1. Limpar dados

```bash
cd test-evidence
npm run reset
```

Deixa só 2 eventos no feed (Samba + Mostra de Teatro) e zera a fila de moderação.

### 2. Subir backend e frontend

**Terminal 1 — API:**

```bash
cd backend
source venv/bin/activate
MODERATOR_KEY=demo-moderador uvicorn main:app --host 127.0.0.1 --port 8010 --reload
```

**Terminal 2 — App:**

```bash
cd frontend
npm run dev -- --port 9300
```

Abrir: **http://localhost:9300**

### 3. Preparar gravação

- Fechar abas e notificações
- Navegador em tela cheia ou ~1440px
- Zoom em **100%**
- Flyer pronto: `test-evidence/teatro-no-recife-boa-viagem.png`

### 4. Gravar no Mac

- **Cmd + Shift + 5** → gravar tela ou janela
- Ou QuickTime → Nova gravação de tela
- Grave só o navegador, não o terminal

---

## Dados mock (copiar na hora)

### Chave de moderador

```
demo-moderador
```

### Evento manual (sem flyer)

| Campo | Valor |
|-------|-------|
| Título | Show Teste Sem Flyer US20 |
| Descrição | Evento de teste cadastrado sem flyer para moderacao. |
| Bairro | Boa Viagem |
| Local | Teatro Boa Viagem |
| Data/hora | 2026-06-20T20:00 |
| Organizador | Produtor Teste US20 |
| E-mail | teste.us20@example.com |

### Evento com flyer

| Campo | Valor |
|-------|-------|
| Arquivo | teatro-no-recife-boa-viagem.png |
| Título (sugerido) | Teatro No Recife Boa Viagem |
| Bairro | Boa Viagem |
| Local | Centro Cultural Boa Viagem |
| Data/hora | 2026-06-22T19:30 |
| Categoria | Teatro |
| Organizador | Produtor Flyer US20 |
| E-mail | flyer.us20@example.com |
| Gratuito | ligado |

### Motivo de rejeição

```
Flyer ausente e dados incompletos para teste US21
```

### Perguntas do chatbot

1. `eventos gratuitos`
2. `o que tem em boa viagem?`
3. `teatro no recife`

---

## Roteiro passo a passo

### Abertura (~30s)

1. Abrir `http://localhost:9300/`
2. Mostrar feed com eventos aprovados
3. Falar: *"Feed público só mostra eventos aprovados."*

---

### US20 — Cadastro (~2 min)

#### A) Cadastro manual

1. Menu **Cadastrar**
2. Preencher tabela "Evento manual" acima
3. **Enviar para moderacao**
4. Mostrar banner verde
5. Falar: *"Entra como pendente, não aparece no feed."*

#### B) Cadastro com flyer

1. Voltar em **Cadastrar**
2. Selecionar flyer → **Preparar flyer**
3. Mostrar preview + título sugerido
4. Completar tabela "Evento com flyer"
5. **Enviar para moderacao**

#### C) Provar que pendente não vai pro feed

1. Ir em **Agenda** (`/`)
2. Mostrar que os 2 novos eventos **não** aparecem

---

### US21 — Moderação (~2 min)

1. Abrir **Moderação** (`/moderacao`)
2. Chave: `demo-moderador`
3. **Carregar pendentes**
4. Mostrar fila com 2 eventos
5. Clicar **Teatro No Recife Boa Viagem**
6. Mostrar flyer + dados
7. **Aprovar**
8. Clicar **Show Teste Sem Flyer US20**
9. Motivo de rejeição (texto acima)
10. **Rejeitar**
11. Mostrar fila vazia
12. Falar: *"Aprovação publica; rejeição impede o feed."*

---

### US23 — Chatbot (~1,5 min)

1. Voltar em **Agenda**
2. Mostrar **Teatro No Recife Boa Viagem** no feed
3. Botão amarelo do chatbot (canto inferior direito)
4. Fazer as 3 perguntas (uma por vez)
5. Mostrar respostas com links `/evento/...`
6. Falar: *"Busca só eventos aprovados."*

---

### API — opcional (~30s)

1. Abrir `http://127.0.0.1:8010/docs`
2. Mostrar `POST /chat`, `GET /moderacao/pendentes`, `POST /events`

---

### Encerramento (~15s)

1. Voltar ao feed
2. Abrir página de um evento aprovado
3. Falar: *"Produtor cadastra → moderador aprova → público vê no feed e no chatbot."*

---

## Ordem rápida (cola)

```
1. Feed inicial
2. /cadastro → manual → enviar
3. /cadastro → flyer → enviar
4. / → feed SEM os novos
5. /moderacao → aprovar teatro → rejeitar show
6. / → feed COM teatro aprovado
7. Chatbot → 3 perguntas
8. (opcional) /docs
```

---

## Checklist final

- [ ] `npm run reset` rodou
- [ ] Backend 8010 + Frontend 9300 no ar
- [ ] Cadastro manual gravado
- [ ] Cadastro com flyer gravado
- [ ] Feed sem pendentes mostrado
- [ ] Aprovar + rejeitar na moderação
- [ ] Chatbot com 3 perguntas legíveis
- [ ] Evento aprovado no feed no final

---

## Se der problema

| Problema | Solução |
|----------|---------|
| Fila com lixo antigo | `cd test-evidence && npm run reset` |
| Chatbot sem resposta | Backend rodando na 8010? |
| Flyer não carrega | Usar `test-evidence/teatro-no-recife-boa-viagem.png` |
| Moderador não entra | Chave: `demo-moderador` (exata) |
| App não abre | `npm run dev -- --port 9300` no frontend |

---

## Dicas

- Uma ação por vez, pause 1–2s após cliques importantes
- Mouse devagar
- Errou? Para, `npm run reset`, recomeça do cadastro
- 5–8 min é o ideal

---

*CESAR School · Onde Acontece Recife · Ciclo 3*
