<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { useEventsStore } from '@/stores/events.js'
import FilterBar from '@/components/FilterBar.vue'
import EventCard from '@/components/EventCard.vue'
import EmptyState from '@/components/EmptyState.vue'

const store = useEventsStore()

onMounted(() => store.fetchEvents())

// auto-refresh enquanto filterAgora estiver ativo
let interval = null
const watchAgora = () => {
  clearInterval(interval)
  if (store.filterAgora) {
    interval = setInterval(() => store.fetchEvents(true), 5 * 60 * 1000)
  }
}
const stopWatchAgora = store.$subscribe(() => watchAgora())
onUnmounted(() => { clearInterval(interval); stopWatchAgora() })

const destaque = computed(() => store.allEvents[0] || null)

function badgePreco(ev) {
  if (ev?.gratuito || ev?.preco === 0) return 'Gratuito'
  if (ev?.preco != null) return `R$ ${Number(ev.preco).toFixed(0)}`
  return 'Consulte'
}

function formatMeta(ev) {
  const parts = []
  if (ev?.bairro) parts.push(ev.bairro)
  if (ev?.inicio_iso) parts.push(ev.inicio_iso.replace('T', ' · '))
  return parts.join(' · ')
}

const favCount = computed(() => store.favoritos.length)
</script>

<template>
  <div class="home">
    <!-- ── topo ─────────────────────────────────────────────────────────── -->
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
        <RouterLink to="/favoritos" class="nav-link-fav">
          ♥ Salvos
          <span v-if="favCount > 0" class="fav-badge">{{ favCount }}</span>
        </RouterLink>
        <RouterLink to="/scraper">⚙️ Coleta</RouterLink>
        <RouterLink class="nav-cta" to="/cadastro">Cadastrar evento</RouterLink>
      </nav>
    </header>

    <!-- ── hero ──────────────────────────────────────────────────────────── -->
    <section class="hero" aria-labelledby="hero-title">
      <div class="hero-inner">
        <p class="kicker">Cultura viva na capital do Nordeste</p>
        <h1 id="hero-title" class="hero-title">
          Descubra o que a <em>prefeitura</em>, produtoras e coletivos fazem hoje no Recife
        </h1>
        <p class="hero-lead">
          Feed centralizado com filtros por categoria, preço, bairro e horário — tudo em um só lugar.
        </p>
        <div class="hero-actions">
          <RouterLink class="btn btn-primary" to="/cadastro">Sou produtor(a) cultural</RouterLink>
          <RouterLink class="btn btn-ghost" to="/mapa">Ver no mapa</RouterLink>
        </div>
      </div>
      <div v-if="destaque" class="hero-card" role="article" :aria-label="destaque.titulo">
        <p class="hero-card-kicker">Em destaque</p>
        <h2 class="hero-card-title">{{ destaque.titulo }}</h2>
        <p class="hero-card-meta">{{ formatMeta(destaque) }}</p>
        <span class="pill">{{ badgePreco(destaque) }}</span>
      </div>
    </section>

    <!-- ── agenda ────────────────────────────────────────────────────────── -->
    <section id="agenda" class="agenda" aria-labelledby="agenda-title">
      <div class="section-head">
        <h2 id="agenda-title">Agenda cultural</h2>
      </div>

      <!-- filtros -->
      <FilterBar />

      <!-- estados -->
      <div v-if="store.loading" class="grid" aria-label="Carregando eventos" aria-busy="true">
        <div v-for="i in 6" :key="i" class="skeleton" aria-hidden="true">
          <div class="skeleton__stripe" />
          <div class="skeleton__body">
            <div class="skeleton__line skeleton__line--short" />
            <div class="skeleton__line skeleton__line--title" />
            <div class="skeleton__line" />
            <div class="skeleton__line skeleton__line--short" />
          </div>
        </div>
      </div>

      <p v-else-if="store.error" class="state state-error" role="alert">{{ store.error }}</p>

      <template v-else>
        <!-- contador modo agora -->
        <div v-if="store.filterAgora" class="agora-counter" role="status" aria-live="polite">
          <span class="agora-dot" />
          {{ store.filteredEvents.length }} evento{{ store.filteredEvents.length !== 1 ? 's' : '' }} rolando agora perto de você
        </div>

        <ul class="grid">
          <li
            v-for="(ev, idx) in store.filteredEvents"
            :key="ev.titulo + (ev.inicio_iso || '')"
            class="grid__item"
            :style="{ animationDelay: `${idx * 0.04}s` }"
          >
            <EventCard :ev="ev" :destacado="idx === 0 && !store.hasActiveFilters" />
          </li>
          <li v-if="store.filteredEvents.length === 0">
            <EmptyState :agora="store.filterAgora" />
          </li>
        </ul>
      </template>
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

/* ── topo ──────────────────────────────────────────────────────────────────── */
.top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding-bottom: 1.25rem;
  border-bottom: 1px solid rgba(148, 163, 184, 0.25);
  flex-wrap: wrap;
}

.brand { display: flex; align-items: center; gap: 0.65rem; }
.brand-mark {
  width: 38px; height: 38px; border-radius: 10px;
  background: conic-gradient(from 210deg, var(--oa-gold), var(--oa-teal), var(--oa-coral), var(--oa-gold));
  box-shadow: var(--shadow);
}
.brand-text { display: flex; flex-direction: column; line-height: 1.1; }
.brand-title { font-family: 'Fraunces', Georgia, serif; font-weight: 700; font-size: 1.05rem; }
.brand-sub { font-size: 0.8rem; letter-spacing: 0.14em; text-transform: uppercase; color: var(--oa-muted); }

.nav { display: flex; align-items: center; gap: 1rem; font-weight: 600; flex-wrap: wrap; }
.nav a { opacity: 0.9; transition: opacity 0.15s; }
.nav a:hover { opacity: 1; }
.nav-cta {
  padding: 0.45rem 0.9rem; border-radius: 999px;
  background: rgba(15, 118, 110, 0.35); border: 1px solid rgba(45, 212, 191, 0.45);
}
.nav-link-fav { position: relative; }
.fav-badge {
  position: absolute; top: -6px; right: -10px;
  background: #ef4444; color: white; font-size: 0.65rem;
  font-weight: 800; border-radius: 999px; padding: 0.05rem 0.35rem;
  min-width: 1.1rem; text-align: center; line-height: 1.4;
}

/* ── hero ──────────────────────────────────────────────────────────────────── */
.hero {
  display: grid; grid-template-columns: 1.15fr 0.85fr;
  gap: 2rem; padding: 2.5rem 0 2rem; align-items: start;
}
@media (max-width: 880px) { .hero { grid-template-columns: 1fr; } }

.hero-inner { padding-top: 0.5rem; }
.kicker { text-transform: uppercase; letter-spacing: 0.12em; font-size: 0.72rem; color: var(--oa-muted); margin: 0 0 0.75rem; }
.hero-title {
  font-family: 'Fraunces', Georgia, serif;
  font-size: clamp(1.85rem, 4vw, 2.65rem);
  line-height: 1.12; margin: 0 0 1rem; font-weight: 700;
}
.hero-title em { font-style: normal; color: #5eead4; }
.hero-lead { margin: 0 0 1.5rem; color: var(--oa-muted); font-size: 1.05rem; max-width: 34rem; }
.hero-actions { display: flex; flex-wrap: wrap; gap: 0.75rem; }

.btn {
  display: inline-flex; align-items: center; justify-content: center;
  padding: 0.65rem 1.1rem; border-radius: 999px; font-weight: 700;
  border: 1px solid transparent; cursor: pointer; font-size: 0.95rem;
}
.btn-primary { background: linear-gradient(120deg, var(--oa-teal), #0ea5e9); color: #042f2e; box-shadow: var(--shadow); }
.btn-ghost { border-color: rgba(148, 163, 184, 0.45); color: var(--oa-text); background: rgba(15, 23, 42, 0.35); }

.hero-card {
  background: var(--oa-card); border: 1px solid rgba(148, 163, 184, 0.25);
  border-radius: var(--radius); padding: 1.25rem 1.35rem; box-shadow: var(--shadow); backdrop-filter: blur(10px);
}
.hero-card-kicker { margin: 0 0 0.35rem; font-size: 0.75rem; letter-spacing: 0.08em; text-transform: uppercase; color: var(--oa-muted); }
.hero-card-title { margin: 0 0 0.5rem; font-size: 1.2rem; line-height: 1.25; }
.hero-card-meta { margin: 0 0 0.75rem; color: var(--oa-muted); font-size: 0.92rem; }
.pill {
  font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em;
  padding: 0.25rem 0.55rem; border-radius: 999px;
  background: rgba(234, 179, 8, 0.18); color: #fde68a; border: 1px solid rgba(234, 179, 8, 0.35);
}

/* ── agenda ────────────────────────────────────────────────────────────────── */
.agenda { padding-top: 0.5rem; }
.section-head { margin-bottom: 1rem; }
.section-head h2 { font-family: 'Fraunces', Georgia, serif; margin: 0; font-size: 1.65rem; }

.agora-counter {
  display: flex; align-items: center; gap: 0.5rem;
  font-size: 0.85rem; font-weight: 700; color: #5eead4;
  margin: 0.75rem 0 0.25rem;
}
.agora-dot {
  width: 8px; height: 8px; border-radius: 50%; background: #5eead4; flex-shrink: 0;
  box-shadow: 0 0 6px #5eead4;
  animation: pulsa 1.5s infinite;
}
@keyframes pulsa { 0%,100%{opacity:1}50%{opacity:0.35} }

.state { color: var(--oa-muted); margin-top: 1rem; }
.state-error { color: #fecaca; }

/* ── grid ──────────────────────────────────────────────────────────────────── */
.grid {
  list-style: none; padding: 0; margin: 0.75rem 0 0;
  display: grid; grid-template-columns: repeat(auto-fill, minmax(290px, 1fr)); gap: 1rem;
}

.grid__item {
  animation: fadeUp 0.3s ease both;
}

@keyframes fadeUp {
  from { opacity: 0; transform: translateY(12px); }
  to   { opacity: 1; transform: translateY(0); }
}

/* ── skeleton ──────────────────────────────────────────────────────────────── */
.skeleton {
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid rgba(148, 163, 184, 0.12);
  border-radius: var(--radius); overflow: hidden;
  display: flex; flex-direction: column;
  min-height: 160px;
}
.skeleton__stripe {
  height: 3px;
  background: linear-gradient(90deg, rgba(148,163,184,0.1) 0%, rgba(148,163,184,0.25) 50%, rgba(148,163,184,0.1) 100%);
  background-size: 200% 100%;
  animation: shimmer 1.4s infinite;
}
.skeleton__body { padding: 1rem; display: flex; flex-direction: column; gap: 0.55rem; }
.skeleton__line {
  height: 12px; border-radius: 6px;
  background: linear-gradient(90deg, rgba(148,163,184,0.08) 0%, rgba(148,163,184,0.18) 50%, rgba(148,163,184,0.08) 100%);
  background-size: 200% 100%;
  animation: shimmer 1.4s infinite;
}
.skeleton__line--short { width: 40%; }
.skeleton__line--title { height: 18px; width: 80%; }
@keyframes shimmer { 0%{background-position:200% 0} 100%{background-position:-200% 0} }

/* ── footer ────────────────────────────────────────────────────────────────── */
.foot {
  margin-top: 3rem; padding-top: 1.5rem;
  border-top: 1px solid rgba(148, 163, 184, 0.2);
  color: var(--oa-muted); font-size: 0.85rem;
}
</style>