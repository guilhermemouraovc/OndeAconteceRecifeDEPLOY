<script setup>
import { ref } from 'vue'
import { RouterLink } from 'vue-router'
import { useApi } from '@/composables/useApi.js'
import { useEventsStore } from '@/stores/events.js'

const { postJson } = useApi()
const store = useEventsStore()

const loading = ref(false)
const resultado = ref(null)
const erro = ref('')

async function executarScraper() {
  loading.value = true
  erro.value = ''
  resultado.value = null
  try {
    const data = await postJson('/scraper/run')
    resultado.value = data
    // atualiza o feed automaticamente após ingestão
    await store.fetchEvents(true)
  } catch (e) {
    erro.value = e instanceof Error ? e.message : 'Erro ao executar scraper.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="scraper-page">

    <!-- ── topo ────────────────────────────────────────────────────────── -->
    <header class="top">
      <RouterLink to="/" class="brand">
        <span class="brand-mark" aria-hidden="true" />
        <span class="brand-text">
          <span class="brand-title">Onde Acontece</span>
          <span class="brand-sub">Recife</span>
        </span>
      </RouterLink>
      <nav class="nav" aria-label="Principal">
        <RouterLink to="/">Agenda</RouterLink>
        <RouterLink to="/mapa">🗺️ Mapa</RouterLink>
        <RouterLink to="/favoritos">♥ Salvos</RouterLink>
        <RouterLink class="nav-cta" to="/cadastro">Cadastrar evento</RouterLink>
      </nav>
    </header>

    <!-- ── conteúdo ─────────────────────────────────────────────────────── -->
    <main class="main">
      <div class="card">

        <div class="card-header">
          <span class="icon" aria-hidden="true">🔄</span>
          <div>
            <h1 class="title">Coleta de Eventos</h1>
            <p class="subtitle">
              Dispara os scrapers da Prefeitura do Recife e da Sympla,
              processa os dados pelo pipeline de limpeza e injeta os novos
              eventos no feed automaticamente.
            </p>
          </div>
        </div>

        <!-- fontes -->
        <ul class="fontes" aria-label="Fontes configuradas">
          <li class="fonte">
            <span class="fonte-dot dot-prefeitura" aria-hidden="true" />
            <div>
              <strong>Prefeitura do Recife</strong>
              <span class="fonte-url">conectarecife.recife.pe.gov.br</span>
            </div>
          </li>
          <li class="fonte">
            <span class="fonte-dot dot-sympla" aria-hidden="true" />
            <div>
              <strong>Sympla</strong>
              <span class="fonte-url">sympla.com.br/eventos/recife-pe</span>
            </div>
          </li>
        </ul>

        <!-- botão -->
        <button
          class="btn-run"
          :disabled="loading"
          :aria-busy="loading"
          @click="executarScraper"
        >
          <span v-if="loading" class="spinner" aria-hidden="true" />
          {{ loading ? 'Coletando eventos…' : 'Executar coleta agora' }}
        </button>

        <!-- erro -->
        <div v-if="erro" class="alert alert-erro" role="alert">
          <strong>Erro:</strong> {{ erro }}
        </div>

        <!-- resultado -->
        <div v-if="resultado" class="resultado" role="status">
          <div class="resultado-header">
            <span class="check" aria-hidden="true">✅</span>
            <strong>Coleta concluída</strong>
          </div>

          <div class="stats">
            <div class="stat">
              <span class="stat-valor">{{ resultado.adicionados }}</span>
              <span class="stat-label">novos eventos adicionados</span>
            </div>
            <div class="stat">
              <span class="stat-valor">{{ resultado.ignorados_duplicados }}</span>
              <span class="stat-label">duplicatas ignoradas</span>
            </div>
            <div class="stat">
              <span class="stat-valor">{{ resultado.total_em_memoria }}</span>
              <span class="stat-label">total em memória</span>
            </div>
          </div>

          <!-- por fonte -->
          <div class="por-fonte">
            <h3 class="por-fonte-title">Por fonte</h3>
            <ul class="fonte-list">
              <li
                v-for="(qtd, fonte) in resultado.por_fonte"
                :key="fonte"
                class="fonte-item"
              >
                <span class="fonte-name">{{ fonte }}</span>
                <span class="fonte-badge">{{ qtd }} eventos</span>
              </li>
            </ul>
          </div>

          <!-- erros de scraping (não críticos) -->
          <div v-if="resultado.erros?.length" class="alert alert-warn">
            <strong>Avisos (fontes com fallback):</strong>
            <ul class="erros-list">
              <li v-for="(e, i) in resultado.erros" :key="i">{{ e }}</li>
            </ul>
          </div>

          <RouterLink to="/" class="btn-feed">
            Ver feed atualizado →
          </RouterLink>
        </div>

      </div>
    </main>
  </div>
</template>

<style scoped>
/* ── layout ──────────────────────────────────────────────────────────────── */
.scraper-page { min-height: 100vh; display: flex; flex-direction: column; }

.top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 2rem;
  border-bottom: 1px solid rgba(255,255,255,.08);
  flex-wrap: wrap;
  gap: .75rem;
}
.brand { display: flex; align-items: center; gap: .6rem; }
.brand-mark {
  width: 32px; height: 32px; border-radius: 8px;
  background: linear-gradient(135deg, var(--oa-teal), var(--oa-mid));
}
.brand-title { font-family: 'Fraunces', serif; font-size: 1.1rem; display: block; }
.brand-sub { font-size: .7rem; color: var(--oa-muted); letter-spacing: .08em; text-transform: uppercase; }
.nav { display: flex; align-items: center; gap: 1.25rem; font-size: .9rem; }
.nav a { color: var(--oa-muted); transition: color .15s; }
.nav a:hover, .nav a.router-link-active { color: var(--oa-text); }
.nav-cta {
  background: var(--oa-teal); color: #fff !important;
  padding: .4rem .9rem; border-radius: 8px; font-weight: 600;
}

.main {
  flex: 1;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding: 3rem 1.5rem;
}

/* ── card ────────────────────────────────────────────────────────────────── */
.card {
  width: 100%;
  max-width: 640px;
  background: var(--oa-card);
  border: 1px solid rgba(255,255,255,.1);
  border-radius: var(--radius);
  padding: 2rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.card-header { display: flex; gap: 1rem; align-items: flex-start; }
.icon { font-size: 2rem; line-height: 1; }
.title { font-family: 'Fraunces', serif; font-size: 1.5rem; margin: 0 0 .35rem; }
.subtitle { color: var(--oa-muted); font-size: .9rem; margin: 0; line-height: 1.5; }

/* ── fontes ──────────────────────────────────────────────────────────────── */
.fontes { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: .75rem; }
.fonte { display: flex; align-items: center; gap: .75rem; }
.fonte-dot {
  width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0;
}
.dot-prefeitura { background: var(--oa-teal); }
.dot-sympla     { background: var(--oa-gold); }
.fonte strong   { display: block; font-size: .95rem; }
.fonte-url      { font-size: .78rem; color: var(--oa-muted); }

/* ── botão principal ─────────────────────────────────────────────────────── */
.btn-run {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: .6rem;
  width: 100%;
  padding: .85rem;
  background: var(--oa-teal);
  color: #fff;
  border: none;
  border-radius: 10px;
  font-size: 1rem;
  font-weight: 700;
  cursor: pointer;
  transition: opacity .15s, transform .1s;
}
.btn-run:hover:not(:disabled) { opacity: .88; transform: translateY(-1px); }
.btn-run:disabled { opacity: .5; cursor: not-allowed; }

.spinner {
  width: 16px; height: 16px;
  border: 2px solid rgba(255,255,255,.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin .7s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* ── alertas ─────────────────────────────────────────────────────────────── */
.alert {
  padding: .85rem 1rem;
  border-radius: 10px;
  font-size: .88rem;
  line-height: 1.5;
}
.alert-erro { background: rgba(220,38,38,.15); border: 1px solid rgba(220,38,38,.3); color: #fca5a5; }
.alert-warn { background: rgba(234,179,8,.1);  border: 1px solid rgba(234,179,8,.25); color: #fde68a; }
.erros-list { margin: .4rem 0 0 1rem; padding: 0; }

/* ── resultado ───────────────────────────────────────────────────────────── */
.resultado {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  animation: fadeIn .3s ease;
}
@keyframes fadeIn { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; } }

.resultado-header { display: flex; align-items: center; gap: .5rem; font-size: 1.05rem; }
.check { font-size: 1.2rem; }

.stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: .75rem;
}
.stat {
  background: rgba(255,255,255,.05);
  border-radius: 10px;
  padding: .85rem;
  text-align: center;
  display: flex;
  flex-direction: column;
  gap: .2rem;
}
.stat-valor { font-size: 1.6rem; font-weight: 700; color: var(--oa-teal); font-family: 'Fraunces', serif; }
.stat-label { font-size: .72rem; color: var(--oa-muted); line-height: 1.3; }

.por-fonte-title { font-size: .8rem; text-transform: uppercase; letter-spacing: .07em; color: var(--oa-muted); margin: 0 0 .5rem; }
.fonte-list { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: .4rem; }
.fonte-item {
  display: flex; justify-content: space-between; align-items: center;
  background: rgba(255,255,255,.05); border-radius: 8px; padding: .5rem .75rem;
  font-size: .88rem;
}
.fonte-name { text-transform: capitalize; }
.fonte-badge {
  background: rgba(15,118,110,.2); color: var(--oa-teal);
  padding: .15rem .5rem; border-radius: 20px; font-size: .75rem; font-weight: 600;
}

.btn-feed {
  display: inline-block;
  background: rgba(255,255,255,.07);
  border: 1px solid rgba(255,255,255,.12);
  border-radius: 10px;
  padding: .65rem 1.1rem;
  font-size: .9rem;
  font-weight: 600;
  text-align: center;
  transition: background .15s;
}
.btn-feed:hover { background: rgba(255,255,255,.12); }

/* ── responsivo ──────────────────────────────────────────────────────────── */
@media (max-width: 480px) {
  .top { padding: .75rem 1rem; }
  .card { padding: 1.25rem; }
  .stats { grid-template-columns: 1fr 1fr; }
  .stat:last-child { grid-column: span 2; }
}
</style>
