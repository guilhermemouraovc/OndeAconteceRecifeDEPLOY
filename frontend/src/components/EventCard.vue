<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useEventsStore } from '@/stores/events.js'

const props = defineProps({
  ev: { type: Object, required: true },
  destacado: { type: Boolean, default: false },
})

const router = useRouter()
const store = useEventsStore()

const favorito = computed(() => store.isFavorito(props.ev.titulo))

function toSlug(str) {
  return (str || '')
    .normalize('NFD').replace(/[\u0300-\u036f]/g, '')
    .toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '')
}

function abrirDetalhe() {
  router.push({ name: 'evento', params: { slug: toSlug(props.ev.titulo) } })
}

function toggleFav(e) {
  e.stopPropagation()
  store.toggleFavorito(props.ev.titulo)
}

const badgePreco = computed(() => {
  const ev = props.ev
  if (ev.gratuito || ev.preco === 0) return { label: 'Gratuito', tipo: 'free' }
  if (ev.preco != null) return { label: `R$ ${Number(ev.preco).toFixed(0)}`, tipo: 'paid' }
  const p = ev.classificacao_texto?.pago
  if (p === 0) return { label: 'Gratuito*', tipo: 'free' }
  if (p === 1) return { label: 'Pago*', tipo: 'paid' }
  return { label: 'Consulte', tipo: 'unknown' }
})

const dataFormatada = computed(() => {
  if (!props.ev.inicio_iso) return null
  const d = new Date(props.ev.inicio_iso.includes('T') ? props.ev.inicio_iso : props.ev.inicio_iso + 'T00:00')
  const dia = d.toLocaleDateString('pt-BR', { weekday: 'short', day: 'numeric', month: 'short' })
  const hora = d.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })
  return `${dia} · ${hora}`
})

const corCategoria = computed(() => {
  const mapa = {
    música: '#5eead4', 'música ao vivo': '#5eead4',
    teatro: '#f9a8d4', dança: '#c4b5fd',
    cinema: '#93c5fd', exposição: '#fcd34d',
    literatura: '#86efac', oficina: '#fdba74',
    festival: '#fb923c', feira: '#a3e635',
    outros: '#94a3b8',
  }
  const k = (props.ev.categoria || '').toLowerCase()
  for (const [key, cor] of Object.entries(mapa)) {
    if (k.includes(key)) return cor
  }
  return '#94a3b8'
})
</script>

<template>
  <article
    class="card"
    :class="{ 'card--destacado': destacado }"
    @click="abrirDetalhe"
    role="button"
    tabindex="0"
    @keydown.enter="abrirDetalhe"
    :aria-label="`Ver detalhes: ${ev.titulo}`"
  >
    <!-- faixa de cor da categoria -->
    <div class="card__stripe" :style="{ background: corCategoria }" />

    <div class="card__body">
      <div class="card__top">
        <span class="chip chip--cat" :style="{ color: corCategoria, borderColor: corCategoria + '55' }">
          {{ ev.categoria || 'Cultura' }}
        </span>
        <span class="chip" :class="`chip--${badgePreco.tipo}`">{{ badgePreco.label }}</span>
      </div>

      <h3 class="card__titulo">{{ ev.titulo }}</h3>
      <p class="card__desc">{{ ev.descricao }}</p>

      <dl class="card__meta">
        <div v-if="ev.bairro">
          <dt>📍</dt>
          <dd>{{ ev.bairro }}</dd>
        </div>
        <div v-if="dataFormatada">
          <dt>🕐</dt>
          <dd>{{ dataFormatada }}</dd>
        </div>
        <div v-if="ev.periodo_dia">
          <dt>☀️</dt>
          <dd>{{ ev.periodo_dia }}</dd>
        </div>
        <div v-if="ev.faixa_preco">
          <dt>🎟️</dt>
          <dd>{{ ev.faixa_preco }}</dd>
        </div>
      </dl>
    </div>

    <button
      class="card__fav"
      :class="{ 'card__fav--ativo': favorito }"
      @click="toggleFav"
      :aria-label="favorito ? 'Remover dos favoritos' : 'Adicionar aos favoritos'"
      :title="favorito ? 'Remover dos favoritos' : 'Salvar evento'"
    >
      {{ favorito ? '♥' : '♡' }}
    </button>
  </article>
</template>

<style scoped>
.card {
  position: relative;
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid rgba(148, 163, 184, 0.18);
  border-radius: var(--radius);
  overflow: hidden;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  transition: transform 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease;
  outline: none;
}

.card:hover,
.card:focus-visible {
  transform: translateY(-3px);
  box-shadow: 0 20px 50px rgba(0,0,0,0.4);
  border-color: rgba(148, 163, 184, 0.38);
}

.card--destacado {
  border-color: rgba(94, 234, 212, 0.35);
  background: rgba(15, 40, 55, 0.7);
}

.card__stripe {
  height: 3px;
  width: 100%;
  flex-shrink: 0;
  opacity: 0.85;
}

.card__body {
  padding: 1rem 1.1rem 1.1rem;
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
  flex: 1;
}

.card__top {
  display: flex;
  gap: 0.4rem;
  flex-wrap: wrap;
  align-items: center;
}

.chip {
  font-size: 0.68rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.07em;
  padding: 0.2rem 0.5rem;
  border-radius: 999px;
  border: 1px solid transparent;
  line-height: 1.4;
}

.chip--cat {
  background: transparent;
}

.chip--free {
  background: rgba(34, 197, 94, 0.15);
  color: #86efac;
  border-color: rgba(34, 197, 94, 0.3);
}

.chip--paid {
  background: rgba(234, 179, 8, 0.15);
  color: #fde68a;
  border-color: rgba(234, 179, 8, 0.3);
}

.chip--unknown {
  background: rgba(148, 163, 184, 0.12);
  color: #94a3b8;
  border-color: rgba(148, 163, 184, 0.25);
}

.card__titulo {
  margin: 0;
  font-size: 1.05rem;
  line-height: 1.3;
  font-family: 'Fraunces', Georgia, serif;
}

.card__desc {
  margin: 0;
  color: var(--oa-muted);
  font-size: 0.88rem;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  flex: 1;
}

.card__meta {
  margin: 0.25rem 0 0;
  display: flex;
  flex-direction: column;
  gap: 0.22rem;
  font-size: 0.8rem;
}

.card__meta > div {
  display: flex;
  gap: 0.35rem;
  align-items: baseline;
}

.card__meta dt {
  flex-shrink: 0;
  font-style: normal;
}

.card__meta dd {
  margin: 0;
  color: #cbd5e1;
}

.card__fav {
  position: absolute;
  top: 0.65rem;
  right: 0.65rem;
  background: rgba(2, 6, 23, 0.6);
  border: 1px solid rgba(148, 163, 184, 0.2);
  border-radius: 50%;
  width: 2rem;
  height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.95rem;
  cursor: pointer;
  color: #94a3b8;
  transition: color 0.15s, background 0.15s, transform 0.15s;
  line-height: 1;
}

.card__fav:hover {
  background: rgba(239, 68, 68, 0.15);
  border-color: rgba(239, 68, 68, 0.3);
  color: #fca5a5;
  transform: scale(1.12);
}

.card__fav--ativo {
  color: #f87171;
  background: rgba(239, 68, 68, 0.12);
  border-color: rgba(239, 68, 68, 0.3);
}
</style>
