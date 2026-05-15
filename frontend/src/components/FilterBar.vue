<script setup>
import { computed } from 'vue'
import { useEventsStore } from '@/stores/events.js'

const store = useEventsStore()

const categorias = [
  { value: '', label: 'Tudo' },
  { value: 'música', label: '🎵 Música' },
  { value: 'teatro', label: '🎭 Teatro' },
  { value: 'cinema', label: '🎬 Cinema' },
  { value: 'dança', label: '💃 Dança' },
  { value: 'exposição', label: '🖼️ Exposição' },
  { value: 'literatura', label: '📚 Literatura' },
  { value: 'oficina', label: '🛠️ Oficina' },
  { value: 'festival', label: '🎪 Festival' },
  { value: 'feira', label: '🏪 Feira' },
]

const opcoesDatas = [
  { value: '', label: 'Qualquer data' },
  { value: 'hoje', label: 'Hoje' },
  { value: 'amanha', label: 'Amanhã' },
  { value: 'fds', label: 'Fim de semana' },
  { value: 'semana', label: 'Esta semana' },
]

const opcoesPreco = [
  { value: '', label: 'Qualquer preço' },
  { value: 'gratuito', label: 'Gratuito' },
  { value: 'ate50', label: 'Até R$ 50' },
  { value: '50a100', label: 'R$ 50–100' },
  { value: 'acima100', label: 'Acima de R$ 100' },
]

const totalFiltrado = computed(() => store.filteredEvents.length)
const totalGeral = computed(() => store.allEvents.length)
</script>

<template>
  <div class="filterbar" role="search" aria-label="Filtros de eventos">

    <!-- toggle agora em destaque -->
    <button
      class="agora-btn"
      :class="{ 'agora-btn--ativo': store.filterAgora }"
      @click="store.filterAgora = !store.filterAgora"
      :aria-pressed="store.filterAgora"
    >
      <span class="agora-dot" />
      {{ store.filterAgora ? 'Rolando agora' : 'O que tá rolando agora?' }}
    </button>

    <div class="filters">
      <!-- categoria: chips horizontais -->
      <div class="filter-group filter-group--chips" role="group" aria-label="Categoria">
        <button
          v-for="cat in categorias"
          :key="cat.value"
          class="fchip"
          :class="{ 'fchip--ativo': store.filterCategoria === cat.value }"
          @click="store.filterCategoria = cat.value"
          :aria-pressed="store.filterCategoria === cat.value"
        >
          {{ cat.label }}
        </button>
      </div>

      <div class="filter-row">
        <!-- preço -->
        <div class="filter-group">
          <label class="filter-label" for="filtro-preco">Preço</label>
          <select id="filtro-preco" v-model="store.filterPreco" class="fselect">
            <option v-for="op in opcoesPreco" :key="op.value" :value="op.value">
              {{ op.label }}
            </option>
          </select>
        </div>

        <!-- bairro -->
        <div class="filter-group">
          <label class="filter-label" for="filtro-bairro">Bairro</label>
          <select id="filtro-bairro" v-model="store.filterBairro" class="fselect">
            <option value="">Todos os bairros</option>
            <option v-for="b in store.bairrosDisponiveis" :key="b" :value="b">{{ b }}</option>
          </select>
        </div>

        <!-- data -->
        <div class="filter-group">
          <label class="filter-label" for="filtro-data">Quando</label>
          <select id="filtro-data" v-model="store.filterData" class="fselect">
            <option v-for="op in opcoesDatas" :key="op.value" :value="op.value">
              {{ op.label }}
            </option>
          </select>
        </div>

        <!-- limpar -->
        <button
          v-if="store.hasActiveFilters"
          class="clear-btn"
          @click="store.clearFilters()"
          aria-label="Limpar todos os filtros"
        >
          ✕ Limpar
        </button>
      </div>
    </div>

    <!-- contador de resultados -->
    <p class="resultado-count" role="status" aria-live="polite">
      <template v-if="store.hasActiveFilters || store.filterAgora">
        <strong>{{ totalFiltrado }}</strong> evento{{ totalFiltrado !== 1 ? 's' : '' }} encontrado{{ totalFiltrado !== 1 ? 's' : '' }}
        <span class="muted">de {{ totalGeral }} no total</span>
      </template>
      <template v-else>
        <strong>{{ totalGeral }}</strong> evento{{ totalGeral !== 1 ? 's' : '' }} na agenda
      </template>
    </p>
  </div>
</template>

<style scoped>
.filterbar {
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
  padding: 1.1rem 1.25rem;
  background: rgba(15, 23, 42, 0.5);
  border: 1px solid rgba(148, 163, 184, 0.18);
  border-radius: var(--radius);
  backdrop-filter: blur(8px);
}

/* ── botão agora ───────────────────────────────────────────────────────────── */
.agora-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  align-self: flex-start;
  padding: 0.45rem 0.9rem;
  border-radius: 999px;
  border: 1px solid rgba(148, 163, 184, 0.3);
  background: rgba(2, 6, 23, 0.4);
  color: var(--oa-muted);
  font-weight: 700;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.2s;
}

.agora-btn:hover {
  border-color: rgba(94, 234, 212, 0.4);
  color: #5eead4;
}

.agora-btn--ativo {
  background: rgba(15, 118, 110, 0.25);
  border-color: rgba(94, 234, 212, 0.55);
  color: #5eead4;
}

.agora-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #94a3b8;
  transition: background 0.2s;
  flex-shrink: 0;
}

.agora-btn--ativo .agora-dot {
  background: #5eead4;
  box-shadow: 0 0 6px #5eead4;
  animation: pulsa 1.5s infinite;
}

@keyframes pulsa {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}

/* ── filtros ───────────────────────────────────────────────────────────────── */
.filters {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.filter-group--chips {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
}

.fchip {
  padding: 0.3rem 0.7rem;
  border-radius: 999px;
  border: 1px solid rgba(148, 163, 184, 0.28);
  background: rgba(2, 6, 23, 0.35);
  color: var(--oa-muted);
  font-size: 0.82rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s;
  white-space: nowrap;
}

.fchip:hover {
  border-color: rgba(148, 163, 184, 0.5);
  color: var(--oa-text);
}

.fchip--ativo {
  background: rgba(15, 118, 110, 0.3);
  border-color: rgba(94, 234, 212, 0.5);
  color: #5eead4;
}

.filter-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.65rem;
  align-items: flex-end;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  min-width: 140px;
  flex: 1;
}

.filter-label {
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--oa-muted);
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.fselect {
  font: inherit;
  padding: 0.45rem 0.6rem;
  border-radius: 10px;
  border: 1px solid rgba(148, 163, 184, 0.28);
  background: rgba(2, 6, 23, 0.5);
  color: var(--oa-text);
  font-size: 0.88rem;
  cursor: pointer;
  appearance: auto;
}

.fselect:focus {
  outline: 2px solid rgba(94, 234, 212, 0.5);
  outline-offset: 1px;
}

.clear-btn {
  padding: 0.45rem 0.85rem;
  border-radius: 10px;
  border: 1px dashed rgba(148, 163, 184, 0.35);
  background: transparent;
  color: var(--oa-muted);
  font-size: 0.82rem;
  font-weight: 700;
  cursor: pointer;
  align-self: flex-end;
  transition: all 0.15s;
  white-space: nowrap;
}

.clear-btn:hover {
  border-color: rgba(248, 113, 113, 0.5);
  color: #fca5a5;
  background: rgba(239, 68, 68, 0.08);
}

/* ── contador ──────────────────────────────────────────────────────────────── */
.resultado-count {
  margin: 0;
  font-size: 0.82rem;
  color: var(--oa-muted);
}

.resultado-count strong {
  color: var(--oa-text);
}

.muted {
  opacity: 0.6;
}
</style>
