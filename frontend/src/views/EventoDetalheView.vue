<script setup>
import { computed, onMounted } from 'vue'
import { useRoute, useRouter, RouterLink } from 'vue-router'
import { useEventsStore } from '@/stores/events.js'

const route = useRoute()
const router = useRouter()
const store = useEventsStore()

onMounted(async () => {
  await store.fetchEvents()
  if (!evento.value) router.replace({ name: 'home' })
})

const evento = computed(() => store.getEventoBySlug(route.params.slug))
const favorito = computed(() => evento.value ? store.isFavorito(evento.value.titulo) : false)

function toggleFav() {
  if (evento.value) store.toggleFavorito(evento.value.titulo)
}

const badgePreco = computed(() => {
  const ev = evento.value
  if (!ev) return null
  if (ev.gratuito || ev.preco === 0) return { label: 'Gratuito', tipo: 'free' }
  if (ev.preco != null) return { label: `R$ ${Number(ev.preco).toFixed(2)}`, tipo: 'paid' }
  const p = ev.classificacao_texto?.pago
  if (p === 0) return { label: 'Gratuito (estimado por IA)', tipo: 'free' }
  if (p === 1) return { label: 'Pago (estimado por IA)', tipo: 'paid' }
  return { label: 'Consulte o organizador', tipo: 'unknown' }
})

const dataCompleta = computed(() => {
  if (!evento.value?.inicio_iso) return null
  const d = new Date(evento.value.inicio_iso.includes('T')
    ? evento.value.inicio_iso
    : evento.value.inicio_iso + 'T00:00')
  return d.toLocaleDateString('pt-BR', {
    weekday: 'long', day: 'numeric', month: 'long', year: 'numeric',
  }) + ' às ' + d.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })
})

function abrirMaps() {
  const q = encodeURIComponent([evento.value.local, evento.value.bairro, 'Recife PE'].filter(Boolean).join(', '))
  window.open(`https://www.google.com/maps/search/?api=1&query=${q}`, '_blank')
}

function compartilhar() {
  const url = window.location.href
  if (navigator.share) {
    navigator.share({ title: evento.value.titulo, url })
  } else {
    navigator.clipboard.writeText(url).then(() => alert('Link copiado!'))
  }
}

const corCategoria = computed(() => {
  const mapa = {
    'música': '#5eead4', 'música ao vivo': '#5eead4',
    teatro: '#f9a8d4', dança: '#c4b5fd', cinema: '#93c5fd',
    exposição: '#fcd34d', literatura: '#86efac', oficina: '#fdba74',
    festival: '#fb923c', feira: '#a3e635', outros: '#94a3b8',
  }
  const k = (evento.value?.categoria || '').toLowerCase()
  for (const [key, cor] of Object.entries(mapa)) {
    if (k.includes(key)) return cor
  }
  return '#94a3b8'
})
</script>

<template>
  <div class="detalhe-page">
    <!-- topo -->
    <header class="top">
      <RouterLink to="/" class="back">← Voltar à agenda</RouterLink>
      <nav class="top-actions">
        <RouterLink to="/favoritos" class="top-link">♥ Salvos</RouterLink>
      </nav>
    </header>

    <!-- loading -->
    <div v-if="store.loading" class="loading" aria-busy="true">
      <div class="loading__bar" />
    </div>

    <!-- conteúdo -->
    <template v-else-if="evento">
      <!-- faixa colorida de categoria -->
      <div class="stripe" :style="{ background: `linear-gradient(90deg, ${corCategoria}33, transparent)`, borderColor: corCategoria + '44' }" />

      <article class="content">
        <!-- cabeçalho do evento -->
        <header class="ev-header">
          <div class="ev-header__chips">
            <span class="chip chip--cat" :style="{ color: corCategoria, borderColor: corCategoria + '55' }">
              {{ evento.categoria || 'Cultura' }}
            </span>
            <span v-if="badgePreco" class="chip" :class="`chip--${badgePreco.tipo}`">
              {{ badgePreco.label }}
            </span>
          </div>

          <h1 class="ev-titulo">{{ evento.titulo }}</h1>

          <div class="ev-actions">
            <button
              class="btn-fav"
              :class="{ 'btn-fav--ativo': favorito }"
              @click="toggleFav"
              :aria-label="favorito ? 'Remover dos favoritos' : 'Salvar nos favoritos'"
            >
              {{ favorito ? '♥ Salvo' : '♡ Salvar' }}
            </button>
            <button class="btn-share" @click="compartilhar" aria-label="Compartilhar evento">
              ↗ Compartilhar
            </button>
          </div>
        </header>

        <!-- grid de infos + descrição -->
        <div class="ev-body">
          <!-- coluna: infos -->
          <aside class="ev-info">
            <dl class="info-list">
              <div v-if="dataCompleta" class="info-item">
                <dt>🕐 Quando</dt>
                <dd>{{ dataCompleta }}</dd>
              </div>
              <div v-if="evento.dia_semana" class="info-item">
                <dt>📅 Dia</dt>
                <dd>{{ evento.dia_semana }}</dd>
              </div>
              <div v-if="evento.periodo_dia" class="info-item">
                <dt>☀️ Período</dt>
                <dd>{{ evento.periodo_dia }}</dd>
              </div>
              <div v-if="evento.local || evento.bairro" class="info-item">
                <dt>📍 Local</dt>
                <dd>
                  <span v-if="evento.local">{{ evento.local }}</span>
                  <span v-if="evento.bairro" class="bairro-tag">{{ evento.bairro }}</span>
                </dd>
              </div>
              <div v-if="evento.faixa_preco" class="info-item">
                <dt>🎟️ Faixa de preço</dt>
                <dd>{{ evento.faixa_preco }}</dd>
              </div>
              <div v-if="evento.organizador" class="info-item">
                <dt>👤 Organizador</dt>
                <dd>{{ evento.organizador }}</dd>
              </div>
              <div v-if="evento.email_contato" class="info-item">
                <dt>✉️ Contato</dt>
                <dd>
                  <a :href="`mailto:${evento.email_contato}`" class="link-email">
                    {{ evento.email_contato }}
                  </a>
                </dd>
              </div>
            </dl>

            <!-- botões de ação -->
            <div class="cta-group">
              <button
                v-if="evento.local || evento.bairro"
                class="cta-btn cta-btn--maps"
                @click="abrirMaps"
              >
                🗺️ Como chegar
              </button>
            </div>

            <!-- classificação IA -->
            <div v-if="evento.classificacao_texto" class="ia-badge">
              <span class="ia-badge__label">🤖 Classificação por IA</span>
              <span class="ia-badge__val">
                {{ evento.classificacao_texto.pago === 0 ? 'Gratuito' : 'Pago' }}
                ({{ Math.round((evento.classificacao_texto.probabilidade_pago ?? 0.5) * 100) }}% pago)
              </span>
              <span class="ia-badge__fonte">via {{ evento.classificacao_texto.fonte }}</span>
            </div>
          </aside>

          <!-- coluna: descrição -->
          <section class="ev-desc" aria-label="Descrição do evento">
            <h2 class="ev-desc__titulo">Sobre o evento</h2>
            <p v-if="evento.descricao" class="ev-desc__texto">{{ evento.descricao }}</p>
            <p v-else class="ev-desc__vazio">Sem descrição disponível para este evento.</p>
          </section>
        </div>

        <!-- dados derivados pelo pipeline -->
        <details class="pipeline-data">
          <summary>🔧 Dados gerados pelo pipeline de ML</summary>
          <pre>{{ JSON.stringify({
            bairro_normalizado: evento.bairro,
            categoria_normalizada: evento.categoria,
            mes: evento.mes,
            dia_semana: evento.dia_semana,
            periodo_dia: evento.periodo_dia,
            faixa_preco: evento.faixa_preco,
            classificacao_texto: evento.classificacao_texto,
          }, null, 2) }}</pre>
        </details>
      </article>
    </template>
  </div>
</template>

<style scoped>
.detalhe-page {
  max-width: 960px;
  margin: 0 auto;
  padding: 1.25rem 1.25rem 3rem;
}

.top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-bottom: 1rem;
  border-bottom: 1px solid rgba(148, 163, 184, 0.2);
  margin-bottom: 1.5rem;
}

.back, .top-link {
  color: var(--oa-muted);
  font-weight: 600;
  font-size: 0.92rem;
  transition: color 0.15s;
}
.back:hover, .top-link:hover { color: var(--oa-text); }

/* ── loading ───────────────────────────────────────────────────────────────── */
.loading { padding: 4rem; display: flex; justify-content: center; }
.loading__bar {
  width: 48px; height: 48px; border-radius: 50%;
  border: 3px solid rgba(148,163,184,0.15);
  border-top-color: #5eead4;
  animation: spin 0.9s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* ── faixa de cor ──────────────────────────────────────────────────────────── */
.stripe {
  height: 4px;
  border-radius: 999px;
  border: none;
  margin-bottom: 1.5rem;
}

/* ── content ───────────────────────────────────────────────────────────────── */
.content {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* ── header ────────────────────────────────────────────────────────────────── */
.ev-header { display: flex; flex-direction: column; gap: 0.65rem; }

.ev-header__chips { display: flex; gap: 0.5rem; flex-wrap: wrap; }

.chip {
  font-size: 0.7rem; font-weight: 700; text-transform: uppercase;
  letter-spacing: 0.07em; padding: 0.22rem 0.55rem;
  border-radius: 999px; border: 1px solid transparent;
}
.chip--cat { background: transparent; }
.chip--free { background: rgba(34,197,94,0.15); color: #86efac; border-color: rgba(34,197,94,0.3); }
.chip--paid { background: rgba(234,179,8,0.15); color: #fde68a; border-color: rgba(234,179,8,0.3); }
.chip--unknown { background: rgba(148,163,184,0.12); color: #94a3b8; border-color: rgba(148,163,184,0.25); }

.ev-titulo {
  font-family: 'Fraunces', Georgia, serif;
  font-size: clamp(1.6rem, 3.5vw, 2.2rem);
  line-height: 1.15;
  margin: 0;
}

.ev-actions { display: flex; gap: 0.65rem; flex-wrap: wrap; }

.btn-fav, .btn-share {
  padding: 0.5rem 1rem; border-radius: 999px;
  font-weight: 700; font-size: 0.88rem; cursor: pointer;
  transition: all 0.15s;
}
.btn-fav {
  background: rgba(2,6,23,0.45); border: 1px solid rgba(148,163,184,0.3); color: var(--oa-muted);
}
.btn-fav:hover { border-color: rgba(239,68,68,0.45); color: #fca5a5; background: rgba(239,68,68,0.1); }
.btn-fav--ativo { color: #f87171; border-color: rgba(239,68,68,0.4); background: rgba(239,68,68,0.12); }

.btn-share {
  background: rgba(2,6,23,0.45); border: 1px solid rgba(148,163,184,0.3); color: var(--oa-muted);
}
.btn-share:hover { border-color: rgba(94,234,212,0.4); color: #5eead4; background: rgba(15,118,110,0.1); }

/* ── body ──────────────────────────────────────────────────────────────────── */
.ev-body {
  display: grid;
  grid-template-columns: 300px 1fr;
  gap: 1.5rem;
  align-items: start;
}
@media (max-width: 700px) { .ev-body { grid-template-columns: 1fr; } }

/* ── info aside ────────────────────────────────────────────────────────────── */
.ev-info {
  background: rgba(15, 23, 42, 0.55);
  border: 1px solid rgba(148, 163, 184, 0.18);
  border-radius: var(--radius);
  padding: 1.1rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.info-list { margin: 0; display: flex; flex-direction: column; gap: 0.75rem; }

.info-item { display: flex; flex-direction: column; gap: 0.18rem; }
.info-item dt { font-size: 0.78rem; font-weight: 700; color: var(--oa-muted); }
.info-item dd { margin: 0; font-size: 0.92rem; line-height: 1.4; }

.bairro-tag {
  display: inline-block; margin-left: 0.4rem;
  background: rgba(94,234,212,0.1); color: #5eead4;
  border: 1px solid rgba(94,234,212,0.25); border-radius: 999px;
  padding: 0.1rem 0.45rem; font-size: 0.75rem;
}

.link-email { color: #93c5fd; text-decoration: underline; font-size: 0.88rem; }
.link-email:hover { color: #bfdbfe; }

.cta-group { display: flex; flex-direction: column; gap: 0.5rem; }

.cta-btn {
  padding: 0.6rem 1rem; border-radius: 10px; border: 1px solid;
  font-weight: 700; font-size: 0.88rem; cursor: pointer; text-align: left;
  transition: all 0.15s;
}
.cta-btn--maps {
  background: rgba(15,118,110,0.2); border-color: rgba(94,234,212,0.35); color: #5eead4;
}
.cta-btn--maps:hover { background: rgba(15,118,110,0.35); }

.ia-badge {
  display: flex; flex-direction: column; gap: 0.15rem;
  background: rgba(2,6,23,0.5); border: 1px dashed rgba(148,163,184,0.25);
  border-radius: 10px; padding: 0.65rem 0.75rem;
}
.ia-badge__label { font-size: 0.72rem; font-weight: 700; color: var(--oa-muted); text-transform: uppercase; }
.ia-badge__val { font-size: 0.88rem; color: var(--oa-text); }
.ia-badge__fonte { font-size: 0.72rem; color: var(--oa-muted); }

/* ── descrição ─────────────────────────────────────────────────────────────── */
.ev-desc {
  background: rgba(15, 23, 42, 0.4);
  border: 1px solid rgba(148, 163, 184, 0.14);
  border-radius: var(--radius);
  padding: 1.25rem 1.35rem;
}
.ev-desc__titulo { font-family: 'Fraunces', Georgia, serif; margin: 0 0 0.85rem; font-size: 1.15rem; }
.ev-desc__texto { margin: 0; line-height: 1.65; color: #cbd5e1; font-size: 1rem; }
.ev-desc__vazio { margin: 0; color: var(--oa-muted); font-style: italic; }

/* ── pipeline data ─────────────────────────────────────────────────────────── */
.pipeline-data {
  background: rgba(2, 6, 23, 0.5);
  border: 1px solid rgba(148, 163, 184, 0.18);
  border-radius: var(--radius);
  padding: 0.75rem 1rem;
  font-size: 0.82rem;
}
.pipeline-data summary { cursor: pointer; color: var(--oa-muted); font-weight: 600; user-select: none; }
.pipeline-data pre {
  margin: 0.75rem 0 0; font-size: 0.75rem; line-height: 1.45;
  color: #94a3b8; overflow: auto;
}
</style>
