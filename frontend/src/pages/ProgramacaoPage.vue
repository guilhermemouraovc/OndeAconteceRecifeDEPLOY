<template>
  <q-page class="bg-landing">
    <div class="main-container page-content">
      <PageHeader title="Programação completa" />

      <div v-if="searchLabel" class="search-info" role="status">
        <q-icon name="search" class="q-mr-sm" />
        <span>{{ store.eventCards.length }} resultado(s) para "{{ searchLabel }}"</span>
        <q-btn flat dense no-caps label="Limpar" color="accent" class="q-ml-md" @click="clearSearch" />
      </div>

      <div v-if="store.hasActiveFilters" class="active-filters">
        <q-chip
          v-if="store.filterCategoria"
          removable
          color="primary"
          text-color="white"
          @remove="store.filterCategoria = ''"
        >
          {{ store.filterCategoria }}
        </q-chip>
        <q-chip
          v-if="store.filterPreco"
          removable
          color="teal"
          text-color="white"
          @remove="store.filterPreco = ''"
        >
          {{ precoLabel(store.filterPreco) }}
        </q-chip>
        <q-chip
          v-if="store.filterBairro"
          removable
          color="accent"
          text-color="dark"
          @remove="store.filterBairro = ''"
        >
          {{ store.filterBairro }}
        </q-chip>
        <q-btn flat dense no-caps label="Limpar tudo" color="grey-5" @click="store.clearFilters()" />
      </div>

      <SkeletonLoader v-if="store.loading" variant="list" :count="6" />

      <EmptyState
        v-else-if="!store.eventCards.length"
        title="Nenhum evento encontrado"
        message="Tente ajustar os filtros ou buscar por outro termo."
        button-label="Limpar filtros"
        @button-click="store.clearFilters()"
      />

      <div v-else class="cards-grid" role="list">
        <EventCard
          v-for="card in store.eventCards"
          :key="card.id"
          :event="card"
          variant="grid"
          @click="goToEvent(card)"
        />
      </div>
    </div>
  </q-page>
</template>

<script setup>
import { computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useEventsStore } from 'src/stores/events'
import PageHeader from 'components/PageHeader.vue'
import EventCard from 'components/EventCard.vue'
import SkeletonLoader from 'components/SkeletonLoader.vue'
import EmptyState from 'components/EmptyState.vue'

const store = useEventsStore()
const route = useRoute()
const router = useRouter()

const searchLabel = computed(() => route.query.q || store.searchQuery)

function precoLabel(v) {
  const map = {
    gratuito: 'Gratuito',
    ate50: 'Até R$ 50',
    '50a100': 'R$ 50–100',
    acima100: 'Acima de R$ 100',
  }
  return map[v] || v
}

function goToEvent(card) {
  if (card?.link) router.push(card.link)
}

function clearSearch() {
  store.searchQuery = ''
  router.replace({ query: {} })
}

function syncRouteQuery() {
  if (route.query.q) store.searchQuery = String(route.query.q)
  if (route.query.categoria) store.filterCategoria = String(route.query.categoria)
}

onMounted(() => {
  syncRouteQuery()
  store.fetchEvents()
})

watch(() => route.query, syncRouteQuery)
</script>

<style scoped>
.page-content {
  padding-top: 16px;
  padding-bottom: 48px;
}

.search-info,
.active-filters {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
  margin: 16px 0;
  color: var(--oa-muted);
}
</style>
