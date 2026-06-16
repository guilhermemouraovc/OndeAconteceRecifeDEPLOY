<template>
  <q-page class="bg-landing">
    <div class="main-container page-content">
      <PageHeader title="Mapa de eventos" />

      <div class="mapa-actions">
        <q-btn
          color="primary"
          :label="userLocated ? 'Você aqui' : 'Usar minha localização'"
          icon="my_location"
          no-caps
          unelevated
          @click="localizarUsuario"
        />
      </div>

      <q-banner v-if="mapError" class="bg-negative text-white q-mb-md" rounded>
        {{ mapError }}
        <template #action>
          <q-btn flat label="Mapbox" href="https://mapbox.com" target="_blank" />
        </template>
      </q-banner>

      <div class="map-wrap">
        <q-inner-loading :showing="loadingMap" color="primary" />

        <!-- Empty state: mapa carregou mas não há eventos com coordenadas -->
        <transition name="fade">
          <div v-if="!loadingMap && !mapError && eventosNoMapa === 0" class="map-empty">
            <q-icon name="location_off" size="40px" class="map-empty__icon" />
            <p class="map-empty__title">Nenhum evento com localização</p>
            <p class="map-empty__sub">
              Os eventos disponíveis ainda não têm coordenadas cadastradas.
            </p>
            <router-link :to="{ name: 'programacao' }" class="map-empty__link">
              Ver lista de eventos
              <q-icon name="arrow_forward" size="14px" />
            </router-link>
          </div>
        </transition>

        <div ref="mapContainer" class="map-container" aria-label="Mapa de eventos em Recife" />
      </div>

      <div class="legenda q-mt-md" aria-label="Legenda de categorias">
        <q-chip
          v-for="item in legenda"
          :key="item.cat"
          dense
          :style="{ borderColor: item.cor }"
          outline
          color="transparent"
          text-color="grey-4"
        >
          <span class="legenda-dot" :style="{ background: item.cor }" />
          {{ item.cat }}
        </q-chip>
      </div>
    </div>
  </q-page>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref, watch, nextTick } from 'vue'
import { useEventsStore } from 'src/stores/events'
import { categoryColor } from 'src/utils/eventMapper'
import { generateSlug } from 'src/utils/stringUtils'
import PageHeader from 'components/PageHeader.vue'

const store = useEventsStore()
const mapContainer = ref(null)
const mapError = ref('')
const loadingMap = ref(true)
const userLocated = ref(false)

let map = null
let markers = []

const MAPBOX_TOKEN = import.meta.env.VITE_MAPBOX_TOKEN || ''

const legenda = [
  { cat: 'Música', cor: '#5eead4' },
  { cat: 'Teatro', cor: '#f9a8d4' },
  { cat: 'Dança', cor: '#c4b5fd' },
  { cat: 'Cinema', cor: '#93c5fd' },
  { cat: 'Exposição', cor: '#fcd34d' },
  { cat: 'Outros', cor: '#94a3b8' },
]

// Conta eventos que têm coordenadas — usado para o empty state
const eventosNoMapa = computed(() =>
  store.allEvents.filter((ev) => ev.lat && ev.lng).length,
)

function addMarkers() {
  if (!map || !window.mapboxgl) return
  markers.forEach((m) => m.remove())
  markers = []

  store.allEvents
    .filter((ev) => ev.lat && ev.lng)
    .forEach((ev) => {
      const cor = categoryColor(ev.categoria)
      const el = document.createElement('div')
      el.style.cssText = `width:28px;height:28px;border-radius:50% 50% 50% 0;transform:rotate(-45deg);cursor:pointer;background:${cor};border:2px solid rgba(255,255,255,0.8);box-shadow:0 2px 8px rgba(0,0,0,0.4);`

      const slug = ev.slug || generateSlug(ev.titulo)
      const preco =
        ev.gratuito || ev.preco === 0
          ? 'Gratuito'
          : ev.preco != null
            ? `R$ ${Number(ev.preco).toFixed(0)}`
            : 'Consulte'

      const popupHtml = `<div style="font-family:sans-serif;max-width:220px;padding:4px;">
        <div style="font-size:13px;font-weight:600;margin-bottom:6px;">${ev.titulo}</div>
        <div style="font-size:11px;color:#64748b;margin-bottom:6px;">${ev.local || ''}</div>
        <div style="font-size:11px;font-weight:700;">${preco}</div>
        <a href="/evento/${slug}" style="font-size:11px;color:#0f766e;">Ver detalhes →</a>
      </div>`

      const { Popup, Marker } = window.mapboxgl
      const popup = new Popup({ offset: 18, closeButton: true, maxWidth: '240px' }).setHTML(popupHtml)
      const marker = new Marker({ element: el }).setLngLat([ev.lng, ev.lat]).setPopup(popup).addTo(map)
      markers.push(marker)
    })
}

async function loadMapbox() {
  if (!window.mapboxgl) {
    await new Promise((resolve, reject) => {
      const link = document.createElement('link')
      link.rel = 'stylesheet'
      link.href = 'https://api.mapbox.com/mapbox-gl-js/v3.4.0/mapbox-gl.css'
      document.head.appendChild(link)
      const script = document.createElement('script')
      script.src = 'https://api.mapbox.com/mapbox-gl-js/v3.4.0/mapbox-gl.js'
      script.onload = resolve
      script.onerror = reject
      document.head.appendChild(script)
    })
  }
}

async function initMap() {
  if (!MAPBOX_TOKEN) {
    mapError.value = 'Configure VITE_MAPBOX_TOKEN no arquivo .env'
    loadingMap.value = false
    return
  }

  await loadMapbox()
  loadingMap.value = false
  await nextTick()

  window.mapboxgl.accessToken = MAPBOX_TOKEN
  map = new window.mapboxgl.Map({
    container: mapContainer.value,
    style: 'mapbox://styles/mapbox/dark-v11',
    center: [-34.877, -8.0476],
    zoom: 12,
  })
  map.addControl(new window.mapboxgl.NavigationControl(), 'top-right')
  map.on('load', () => {
    map.resize()
    addMarkers()
  })
}

function localizarUsuario() {
  if (!navigator.geolocation || !map) return
  navigator.geolocation.getCurrentPosition(
    (pos) => {
      map.flyTo({ center: [pos.coords.longitude, pos.coords.latitude], zoom: 14, duration: 1200 })
      userLocated.value = true
    },
    () => {
      mapError.value = 'Não foi possível obter sua localização.'
    },
  )
}

onMounted(async () => {
  await store.fetchEvents()
  await initMap()
})

onUnmounted(() => {
  if (map) {
    map.remove()
    map = null
  }
})

watch(() => store.allEvents.length, () => addMarkers())
</script>

<style scoped>
.page-content {
  padding-top: 16px;
  padding-bottom: 48px;
}

.mapa-actions {
  margin-bottom: 16px;
}

.map-wrap {
  position: relative;
  height: 520px;
  border-radius: 16px;
  overflow: hidden;
  border: 1px solid rgba(148, 163, 184, 0.2);
}

.map-container {
  width: 100%;
  height: 100%;
}

/* ---- Empty state do mapa ---- */
.map-empty {
  position: absolute;
  inset: 0;
  z-index: 10;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
  background: rgba(4, 16, 29, 0.82);
  backdrop-filter: blur(6px);
  text-align: center;
  padding: 32px;
}

.map-empty__icon {
  color: var(--oa-muted);
  opacity: 0.6;
  margin-bottom: 4px;
}

.map-empty__title {
  font-size: 1.1rem;
  font-weight: 600;
  color: #fff;
  margin: 0;
}

.map-empty__sub {
  font-size: 0.88rem;
  color: var(--oa-muted);
  max-width: 300px;
  line-height: 1.5;
  margin: 0;
}

.map-empty__link {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  margin-top: 8px;
  font-size: 0.88rem;
  font-weight: 600;
  color: var(--oa-accent);
  text-decoration: none;
  transition: opacity 0.2s;

  &:hover {
    opacity: 0.8;
  }
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.legenda {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.legenda-dot {
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  margin-right: 6px;
}
</style>