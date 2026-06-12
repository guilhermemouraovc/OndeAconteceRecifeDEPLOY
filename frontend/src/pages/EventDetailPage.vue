<template>
  <q-page class="bg-landing">
    <div class="main-container page-content">
      <LoadingState v-if="loading" />

      <template v-else-if="event">
        <BackButton :to="{ name: 'home' }" label="Voltar à agenda" />

        <article class="detail-article">
          <div class="detail-stripe" :style="{ background: `linear-gradient(90deg, ${catColor}44, transparent)` }" />

          <div class="detail-chips">
            <q-chip dense outline :style="{ color: catColor, borderColor: catColor }">
              {{ event.categoria || 'Cultura' }}
            </q-chip>
            <q-chip dense :color="badge.tipo === 'free' ? 'positive' : 'accent'" text-color="white">
              {{ badge.label }}
            </q-chip>
            <q-chip v-if="sourceLabel" dense outline color="grey-5">{{ sourceLabel }}</q-chip>
          </div>

          <h1 class="detail-title font-display">{{ event.title }}</h1>

          <q-img
            v-if="event.image"
            :src="event.image"
            :alt="event.title"
            class="detail-hero q-my-md"
            ratio="16/9"
            rounded
          />

          <div class="detail-meta">
            <div v-if="event.dateLabel"><q-icon name="event" class="q-mr-sm" />{{ event.dateLabel }}</div>
            <div v-if="event.timeLabel"><q-icon name="schedule" class="q-mr-sm" />{{ event.timeLabel }}</div>
            <div v-if="event.location"><q-icon name="place" class="q-mr-sm" />{{ event.location }}</div>
          </div>

          <p v-if="event.description" class="detail-desc">{{ event.description }}</p>

          <div class="detail-actions q-mt-lg">
            <q-btn
              v-if="event.link_compra"
              color="primary"
              label="Comprar ingresso"
              icon="confirmation_number"
              no-caps
              unelevated
              :href="event.link_compra"
              target="_blank"
            />
            <q-btn
              outline
              color="accent"
              label="Como chegar"
              icon="directions"
              no-caps
              @click="abrirMaps"
            />
            <q-btn
              flat
              color="white"
              :icon="favorito ? 'favorite' : 'favorite_border'"
              :label="favorito ? 'Salvo' : 'Salvar'"
              no-caps
              @click="toggleFav"
            />
            <q-btn flat color="grey-4" icon="share" label="Compartilhar" no-caps @click="compartilhar" />
          </div>

          <q-expansion-item
            v-if="event.classificacao_texto"
            label="Classificação ML (debug)"
            icon="psychology"
            dark
            class="q-mt-lg ml-panel"
          >
            <pre class="ml-json">{{ JSON.stringify(event.classificacao_texto, null, 2) }}</pre>
          </q-expansion-item>
        </article>
      </template>

      <EmptyState
        v-else
        title="Evento não encontrado"
        message="Este evento pode ter sido removido ou o link está incorreto."
        button-label="Ver agenda"
        :button-to="{ name: 'home' }"
      />
    </div>
  </q-page>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useEventsStore } from 'src/stores/events'
import { categoryColor } from 'src/utils/eventMapper'
import BackButton from 'components/BackButton.vue'
import LoadingState from 'components/LoadingState.vue'
import EmptyState from 'components/EmptyState.vue'

const route = useRoute()
const store = useEventsStore()

const event = ref(null)
const loading = ref(true)

const sourceLabelMap = {
  ticketpe: 'via TicketPE',
  sympla: 'via Sympla',
  prefeitura: 'via Prefeitura',
}

const catColor = computed(() => categoryColor(event.value?.categoria))
const favorito = computed(() => (event.value ? store.isFavorito(event.value.title) : false))
const sourceLabel = computed(() => sourceLabelMap[event.value?.source] || null)

const badge = computed(() => {
  const ev = event.value?.raw || event.value
  if (!ev) return { label: 'Consulte', tipo: 'unknown' }
  if (ev.gratuito || ev.preco === 0) return { label: 'Gratuito', tipo: 'free' }
  if (ev.preco != null) return { label: `R$ ${Number(ev.preco).toFixed(2)}`, tipo: 'paid' }
  const p = ev.classificacao_texto?.pago
  if (p === 0) return { label: 'Gratuito (IA)', tipo: 'free' }
  if (p === 1) return { label: 'Pago (IA)', tipo: 'paid' }
  return { label: 'Consulte', tipo: 'unknown' }
})

function toggleFav() {
  if (event.value?.title) store.toggleFavorito(event.value.title)
}

function abrirMaps() {
  const ev = event.value?.raw || event.value
  const q = encodeURIComponent([ev?.local, ev?.bairro, 'Recife PE'].filter(Boolean).join(', '))
  window.open(`https://www.google.com/maps/search/?api=1&query=${q}`, '_blank')
}

function compartilhar() {
  const url = window.location.href
  if (navigator.share) navigator.share({ title: event.value?.title, url })
  else navigator.clipboard.writeText(url)
}

onMounted(async () => {
  loading.value = true
  await store.fetchEvents()
  try {
    event.value = await store.loadEventDetail(route.params.slug)
  } catch {
    event.value = null
  }
  loading.value = false
})
</script>

<style scoped lang="scss">
.page-content {
  padding-top: 16px;
  padding-bottom: 48px;
  max-width: 800px;
}

.detail-stripe {
  height: 4px;
  border-radius: 4px;
  margin-bottom: 20px;
}

.detail-title {
  font-size: clamp(1.75rem, 4vw, 2.5rem);
  color: #fff;
  margin: 12px 0;
}

.detail-meta {
  display: flex;
  flex-direction: column;
  gap: 8px;
  color: var(--oa-muted);
  margin: 16px 0;
}

.detail-desc {
  color: rgba(248, 250, 252, 0.9);
  line-height: 1.7;
  font-size: 1.05rem;
}

.detail-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.detail-hero {
  border-radius: 16px;
  overflow: hidden;
}

.ml-panel {
  background: rgba(255, 255, 255, 0.04);
  border-radius: 12px;
}

.ml-json {
  padding: 12px;
  font-size: 0.8rem;
  color: var(--oa-accent);
  overflow-x: auto;
}
</style>
