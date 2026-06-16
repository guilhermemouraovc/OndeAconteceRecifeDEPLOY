<template>
  <q-page class="bg-landing">
    <div class="main-container page-content">
      <PageHeader title="Programação completa" />

      <!-- Barra de controles: ordenação + contagem -->
      <div class="controls-bar">
        <span class="controls-bar__count">
          <template v-if="!store.loading">
            {{ store.totalFilteredCount }}
            {{ store.totalFilteredCount === 1 ? 'evento' : 'eventos' }}
            <template v-if="store.hasActiveFilters"> encontrados</template>
          </template>
        </span>

        <div class="controls-bar__sort">
          <span class="sort-label">Ordenar:</span>
          <button
            v-for="opt in sortOptions"
            :key="opt.value"
            class="sort-chip"
            :class="{ 'sort-chip--active': store.sortOrder === opt.value }"
            type="button"
            @click="setSort(opt.value)"
          >
            {{ opt.label }}
          </button>
        </div>
      </div>

      <!-- Filtros ativos -->
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
        <q-chip
          v-if="store.filterData"
          removable
          color="secondary"
          text-color="white"
          @remove="store.filterData = ''"
        >
          {{ dataLabel(store.filterData) }}
        </q-chip>
        <q-chip
          v-if="store.filterAgora"
          removable
          color="positive"
          text-color="white"
          @remove="store.filterAgora = false"
        >
          Rolando agora
        </q-chip>
        <q-chip
          v-if="searchLabel"
          removable
          color="grey-7"
          text-color="white"
          @remove="clearSearch"
        >
          "{{ searchLabel }}"
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

      <template v-else>
        <div class="cards-grid" role="list">
          <EventCard
            v-for="card in store.eventCards"
            :key="card.id"
            :event="card"
            variant="grid"
            @click="goToEvent(card)"
          />
        </div>

        <!-- Ver mais -->
        <div v-if="store.hasMore" class="ver-mais">
          <button class="ver-mais-btn" type="button" @click="store.loadMore()">
            <q-icon name="expand_more" size="18px" />
            Ver mais eventos
            <span class="ver-mais-btn__count">
              ({{ store.totalFilteredCount - store.eventCards.length }} restantes)
            </span>
          </button>
        </div>
      </template>
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

const sortOptions = [
  { label: 'Data', value: 'data' },
  { label: 'Menor preço', value: 'preco_asc' },
  { label: 'Maior preço', value: 'preco_desc' },
]

const searchLabel = computed(() => route.query.q || store.searchQuery || '')

function precoLabel(v) {
  const map = { gratuito: 'Gratuito', ate50: 'Até R$ 50', '50a100': 'R$ 50–100', acima100: 'Acima de R$ 100' }
  return map[v] || v
}

function dataLabel(v) {
  const map = { hoje: 'Hoje', amanha: 'Amanhã', fds: 'Fim de semana', semana: 'Esta semana' }
  return map[v] || v
}

function goToEvent(card) {
  if (card?.link) router.push(card.link)
}

function clearSearch() {
  store.searchQuery = ''
  router.replace({ query: { ...route.query, q: undefined } })
}

function setSort(value) {
  store.sortOrder = value
  store.resetPagination()
}

// Lê URL → store
function syncRouteQuery() {
  if (route.query.q) store.searchQuery = String(route.query.q)
  if (route.query.categoria) store.filterCategoria = String(route.query.categoria)
  if (route.query.preco) store.filterPreco = String(route.query.preco)
  if (route.query.bairro) store.filterBairro = String(route.query.bairro)
  if (route.query.data) store.filterData = String(route.query.data)
  if (route.query.agora === '1') store.filterAgora = true
  if (route.query.ordem) store.sortOrder = String(route.query.ordem)
}

// Escreve store → URL
function pushFiltersToUrl() {
  const q = {}
  if (store.searchQuery) q.q = store.searchQuery
  if (store.filterCategoria) q.categoria = store.filterCategoria
  if (store.filterPreco) q.preco = store.filterPreco
  if (store.filterBairro) q.bairro = store.filterBairro
  if (store.filterData) q.data = store.filterData
  if (store.filterAgora) q.agora = '1'
  if (store.sortOrder !== 'data') q.ordem = store.sortOrder
  router.replace({ query: q })
}

onMounted(() => {
  syncRouteQuery()
  store.fetchEvents()
})

watch(() => route.query, syncRouteQuery)

watch(
  () => [
    store.filterCategoria,
    store.filterPreco,
    store.filterBairro,
    store.filterData,
    store.filterAgora,
    store.searchQuery,
    store.sortOrder,
  ],
  pushFiltersToUrl,
)
</script>

<style scoped lang="scss">
.page-content {
  padding-top: 16px;
  padding-bottom: 48px;
}

/* ---- Barra de controles ---- */
.controls-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
  margin-bottom: 16px;
}

.controls-bar__count {
  font-size: 0.88rem;
  color: var(--oa-muted);
  min-width: 80px;
}

.controls-bar__sort {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.sort-label {
  font-size: 0.82rem;
  color: var(--oa-muted);
  font-weight: 600;
}

.sort-chip {
  font-family: inherit;
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--oa-muted);
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 999px;
  padding: 4px 12px;
  cursor: pointer;
  transition: all 0.18s ease;

  &:hover {
    color: #fff;
    border-color: rgba(255, 255, 255, 0.25);
  }

  &--active {
    color: #fff;
    background: rgba(94, 234, 212, 0.12);
    border-color: var(--oa-accent);
  }
}

/* ---- Filtros ativos ---- */
.active-filters {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 16px;
  color: var(--oa-muted);
}

/* ---- Ver mais ---- */
.ver-mais {
  display: flex;
  justify-content: center;
  margin-top: 32px;
}

.ver-mais-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-family: inherit;
  font-size: 0.92rem;
  font-weight: 600;
  color: var(--oa-accent);
  background: rgba(94, 234, 212, 0.07);
  border: 1px solid rgba(94, 234, 212, 0.25);
  border-radius: 999px;
  padding: 10px 24px;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background: rgba(94, 234, 212, 0.14);
    border-color: rgba(94, 234, 212, 0.5);
  }
}

.ver-mais-btn__count {
  font-size: 0.8rem;
  font-weight: 400;
  color: var(--oa-muted);
}
</style>