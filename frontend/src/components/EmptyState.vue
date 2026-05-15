<script setup>
import { useEventsStore } from '@/stores/events.js'

const store = useEventsStore()

defineProps({
  agora: { type: Boolean, default: false },
})
</script>

<template>
  <div class="empty" role="status">
    <span class="empty__icon">{{ agora ? '🌙' : '🔍' }}</span>
    <p class="empty__titulo">
      {{ agora ? 'Nada rolando agora perto de você' : 'Nenhum evento encontrado' }}
    </p>
    <p class="empty__desc">
      {{ agora
        ? 'Tente ampliar o horário ou desative o filtro "Agora".'
        : 'Tente ajustar os filtros ou limpar a busca para ver mais eventos.' }}
    </p>
    <button v-if="store.hasActiveFilters || store.filterAgora" class="empty__btn" @click="store.clearFilters()">
      Limpar filtros
    </button>
  </div>
</template>

<style scoped>
.empty {
  grid-column: 1 / -1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  padding: 3.5rem 1rem;
  text-align: center;
}

.empty__icon {
  font-size: 2.5rem;
  line-height: 1;
}

.empty__titulo {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 700;
  font-family: 'Fraunces', Georgia, serif;
}

.empty__desc {
  margin: 0;
  color: var(--oa-muted);
  font-size: 0.92rem;
  max-width: 28rem;
}

.empty__btn {
  margin-top: 0.5rem;
  padding: 0.5rem 1.1rem;
  border-radius: 999px;
  border: 1px solid rgba(148, 163, 184, 0.35);
  background: rgba(2, 6, 23, 0.4);
  color: var(--oa-text);
  font-weight: 700;
  font-size: 0.88rem;
  cursor: pointer;
  transition: border-color 0.15s, background 0.15s;
}

.empty__btn:hover {
  border-color: rgba(94, 234, 212, 0.45);
  background: rgba(15, 118, 110, 0.15);
}
</style>
