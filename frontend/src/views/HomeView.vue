<script setup>
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { useApi } from '@/composables/useApi.js'

const { getJson } = useApi()
const events = ref([])
const loading = ref(true)
const error = ref('')

const categorias = [
  'Música ao vivo',
  'Teatro',
  'Cinema',
  'Festival',
  'Patrimônio e memória',
  'Oficina',
]

const destaque = computed(() => events.value[0] || null)

onMounted(async () => {
  try {
    events.value = await getJson('/events')
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Não foi possível carregar os eventos.'
  } finally {
    loading.value = false
  }
})

function formatMeta(ev) {
  const parts = []
  if (ev?.bairro) parts.push(ev.bairro)
  if (ev?.inicio_iso) parts.push(ev.inicio_iso.replace('T', ' · '))
  return parts.join(' · ')
}

function badgePagamento(ev) {
  if (ev?.gratuito || ev?.preco === 0) return 'Gratuito'
  if (ev?.preco != null) return `R$ ${Number(ev.preco).toFixed(0)}`
  const p = ev?.classificacao_texto?.pago
  if (p === 0) return 'Gratuito (estimado)'
  if (p === 1) return 'Pago (estimado)'
  return 'Consulte'
}
</script>

<template>
  <div class="home">
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
        <RouterLink class="nav-cta" to="/cadastro">Cadastrar evento</RouterLink>
      </nav>
    </header>

    <section class="hero" aria-labelledby="hero-title">
      <div class="hero-inner">
        <p class="kicker">Cultura viva na capital do Nordeste</p>
        <h1 id="hero-title" class="hero-title">
          Descubra o que a <em>prefeitura</em>, produtoras e coletivos fazem hoje no Recife
        </h1>
        <p class="hero-lead">
          Uma vitrine inspirada em experiências de landing de eventos, com identidade pernambucana
          e foco em acesso à programação cultural municipal e independente.
        </p>
        <div class="hero-actions">
          <RouterLink class="btn btn-primary" to="/cadastro">Sou produtor(a) cultural</RouterLink>
          <a class="btn btn-ghost" href="#agenda">Ver agenda</a>
        </div>
      </div>
      <div v-if="destaque" class="hero-card" role="article" :aria-label="destaque.titulo">
        <p class="hero-card-kicker">Em destaque</p>
        <h2 class="hero-card-title">{{ destaque.titulo }}</h2>
        <p class="hero-card-meta">{{ formatMeta(destaque) }}</p>
        <span class="pill">{{ badgePagamento(destaque) }}</span>
      </div>
    </section>

    <section class="cats" aria-label="Categorias">
      <div class="cats-inner">
        <span v-for="c in categorias" :key="c" class="chip">{{ c }}</span>
      </div>
    </section>

    <section id="agenda" class="agenda" aria-labelledby="agenda-title">
      <div class="section-head">
        <h2 id="agenda-title">Agenda cultural</h2>
        <p class="section-desc">Dados passam pelo pipeline de normalização e classificação de texto no backend.</p>
      </div>

      <p v-if="loading" class="state">Carregando eventos…</p>
      <p v-else-if="error" class="state state-error">{{ error }}</p>

      <ul v-else class="grid">
        <li v-for="ev in events" :key="ev.titulo + (ev.inicio_iso || '')" class="card">
          <div class="card-top">
            <span class="pill pill-soft">{{ ev.categoria || 'Cultura' }}</span>
            <span class="pill">{{ badgePagamento(ev) }}</span>
          </div>
          <h3 class="card-title">{{ ev.titulo }}</h3>
          <p class="card-desc">{{ ev.descricao }}</p>
          <dl class="meta">
            <div>
              <dt>Bairro</dt>
              <dd>{{ ev.bairro || '—' }}</dd>
            </div>
            <div>
              <dt>Quando</dt>
              <dd>{{ ev.inicio_iso?.replace('T', ' ') || '—' }}</dd>
            </div>
            <div v-if="ev.faixa_preco">
              <dt>Faixa</dt>
              <dd>{{ ev.faixa_preco }}</dd>
            </div>
            <div v-if="ev.periodo_dia">
              <dt>Período</dt>
              <dd>{{ ev.periodo_dia }}</dd>
            </div>
          </dl>
        </li>
      </ul>
    </section>

    <footer class="foot">
      <p>Projeto acadêmico — Onde Acontece Recife · dados de exemplo e API FastAPI.</p>
    </footer>
  </div>
</template>

<style scoped>
.home {
  max-width: 1120px;
  margin: 0 auto;
  padding: 1.25rem 1.25rem 3rem;
}

.top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding-bottom: 1.25rem;
  border-bottom: 1px solid rgba(148, 163, 184, 0.25);
}

.brand {
  display: flex;
  align-items: center;
  gap: 0.65rem;
}

.brand-mark {
  width: 38px;
  height: 38px;
  border-radius: 10px;
  background: conic-gradient(from 210deg, var(--oa-gold), var(--oa-teal), var(--oa-coral), var(--oa-gold));
  box-shadow: var(--shadow);
}

.brand-text {
  display: flex;
  flex-direction: column;
  line-height: 1.1;
}

.brand-title {
  font-family: 'Fraunces', Georgia, serif;
  font-weight: 700;
  font-size: 1.05rem;
}

.brand-sub {
  font-size: 0.8rem;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--oa-muted);
}

.nav {
  display: flex;
  align-items: center;
  gap: 1rem;
  font-weight: 600;
}

.nav a {
  opacity: 0.9;
}

.nav a:hover {
  opacity: 1;
}

.nav-cta {
  padding: 0.45rem 0.9rem;
  border-radius: 999px;
  background: rgba(15, 118, 110, 0.35);
  border: 1px solid rgba(45, 212, 191, 0.45);
}

.hero {
  display: grid;
  grid-template-columns: 1.15fr 0.85fr;
  gap: 2rem;
  padding: 2.5rem 0 2rem;
  align-items: start;
}

@media (max-width: 880px) {
  .hero {
    grid-template-columns: 1fr;
  }
}

.hero-inner {
  padding-top: 0.5rem;
}

.kicker {
  text-transform: uppercase;
  letter-spacing: 0.12em;
  font-size: 0.72rem;
  color: var(--oa-muted);
  margin: 0 0 0.75rem;
}

.hero-title {
  font-family: 'Fraunces', Georgia, serif;
  font-size: clamp(1.85rem, 4vw, 2.65rem);
  line-height: 1.12;
  margin: 0 0 1rem;
  font-weight: 700;
}

.hero-title em {
  font-style: normal;
  color: #5eead4;
}

.hero-lead {
  margin: 0 0 1.5rem;
  color: var(--oa-muted);
  font-size: 1.05rem;
  max-width: 34rem;
}

.hero-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.65rem 1.1rem;
  border-radius: 999px;
  font-weight: 700;
  border: 1px solid transparent;
  cursor: pointer;
  font-size: 0.95rem;
}

.btn-primary {
  background: linear-gradient(120deg, var(--oa-teal), #0ea5e9);
  color: #042f2e;
  box-shadow: var(--shadow);
}

.btn-ghost {
  border-color: rgba(148, 163, 184, 0.45);
  color: var(--oa-text);
  background: rgba(15, 23, 42, 0.35);
}

.hero-card {
  background: var(--oa-card);
  border: 1px solid rgba(148, 163, 184, 0.25);
  border-radius: var(--radius);
  padding: 1.25rem 1.35rem;
  box-shadow: var(--shadow);
  backdrop-filter: blur(10px);
}

.hero-card-kicker {
  margin: 0 0 0.35rem;
  font-size: 0.75rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--oa-muted);
}

.hero-card-title {
  margin: 0 0 0.5rem;
  font-size: 1.2rem;
  line-height: 1.25;
}

.hero-card-meta {
  margin: 0 0 0.75rem;
  color: var(--oa-muted);
  font-size: 0.92rem;
}

.cats {
  margin: 0.5rem 0 2rem;
}

.cats-inner {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.chip {
  padding: 0.35rem 0.75rem;
  border-radius: 999px;
  border: 1px solid rgba(148, 163, 184, 0.35);
  font-size: 0.85rem;
  color: var(--oa-muted);
}

.agenda {
  padding-top: 0.5rem;
}

.section-head {
  margin-bottom: 1.25rem;
}

.section-head h2 {
  font-family: 'Fraunces', Georgia, serif;
  margin: 0 0 0.35rem;
  font-size: 1.65rem;
}

.section-desc {
  margin: 0;
  color: var(--oa-muted);
}

.state {
  color: var(--oa-muted);
}

.state-error {
  color: #fecaca;
}

.grid {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1rem;
}

.card {
  background: rgba(15, 23, 42, 0.55);
  border: 1px solid rgba(148, 163, 184, 0.22);
  border-radius: var(--radius);
  padding: 1.1rem 1.15rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.card-top {
  display: flex;
  justify-content: space-between;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.pill {
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  padding: 0.25rem 0.55rem;
  border-radius: 999px;
  background: rgba(234, 179, 8, 0.18);
  color: #fde68a;
  border: 1px solid rgba(234, 179, 8, 0.35);
  width: fit-content;
}

.pill-soft {
  background: rgba(14, 165, 233, 0.15);
  color: #bae6fd;
  border-color: rgba(14, 165, 233, 0.35);
}

.card-title {
  margin: 0;
  font-size: 1.1rem;
  line-height: 1.25;
}

.card-desc {
  margin: 0;
  color: var(--oa-muted);
  font-size: 0.92rem;
  flex: 1;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.meta {
  margin: 0.25rem 0 0;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.5rem 0.75rem;
  font-size: 0.82rem;
}

.meta dt {
  color: var(--oa-muted);
  font-weight: 600;
}

.meta dd {
  margin: 0.1rem 0 0;
}

.foot {
  margin-top: 3rem;
  padding-top: 1.5rem;
  border-top: 1px solid rgba(148, 163, 184, 0.2);
  color: var(--oa-muted);
  font-size: 0.85rem;
}
</style>
