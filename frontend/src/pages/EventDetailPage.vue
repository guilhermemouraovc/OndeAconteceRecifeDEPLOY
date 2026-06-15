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
            <q-btn flat color="grey-4" icon="share" label="Compartilhar link" no-caps @click="compartilharLink" />
            <button class="whatsapp-btn" type="button" @click="compartilharWhatsApp">
              <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" class="whatsapp-btn__icon" aria-hidden="true">
                <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347z"/>
                <path d="M12 0C5.373 0 0 5.373 0 12c0 2.117.549 4.107 1.508 5.84L.057 23.428a.75.75 0 0 0 .921.921l5.588-1.451A11.934 11.934 0 0 0 12 24c6.627 0 12-5.373 12-12S18.627 0 12 0zm0 21.818a9.787 9.787 0 0 1-4.997-1.37l-.358-.213-3.716.965.99-3.614-.234-.372A9.818 9.818 0 0 1 2.182 12C2.182 6.57 6.57 2.182 12 2.182c5.43 0 9.818 4.388 9.818 9.818 0 5.43-4.388 9.818-9.818 9.818z"/>
              </svg>
              WhatsApp
            </button>
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

function compartilharLink() {
  const url = window.location.href
  if (navigator.share) navigator.share({ title: event.value?.title, url })
  else {
    navigator.clipboard.writeText(url)
    // feedback visual via Quasar Notify se disponível
    if (window.Quasar) window.Quasar.Notify.create({ message: 'Link copiado!', color: 'dark', timeout: 1800 })
  }
}

function compartilharWhatsApp() {
  const url = window.location.href
  const ev = event.value
  const texto = ev?.title
    ? `Olha esse evento que encontrei no Onde Acontece Recife 👀
*${ev.title}*
${ev.dateLabel ? ev.dateLabel + '\n' : ''}${url}`
    : url
  window.open(`https://wa.me/?text=${encodeURIComponent(texto)}`, '_blank')
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
.whatsapp-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-family: inherit;
  font-size: 0.875rem;
  font-weight: 600;
  color: #25d366;
  background: rgba(37, 211, 102, 0.1);
  border: 1px solid rgba(37, 211, 102, 0.3);
  border-radius: 8px;
  padding: 8px 16px;
  cursor: pointer;
  transition: background 0.2s ease, border-color 0.2s ease;

  &:hover {
    background: rgba(37, 211, 102, 0.18);
    border-color: rgba(37, 211, 102, 0.55);
  }
}

.whatsapp-btn__icon {
  width: 18px;
  height: 18px;
  fill: #25d366;
  flex-shrink: 0;
}
</style>