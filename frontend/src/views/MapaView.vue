<script setup>
import { onMounted, onUnmounted, ref, watch, nextTick } from 'vue'
import { RouterLink } from 'vue-router'
import { useEventsStore } from '@/stores/events.js'

const store = useEventsStore()

const mapContainer = ref(null)
let map = null
let markers = []

const mapError = ref('')
const loadingMap = ref(true)
const userLocated = ref(false)

const MAPBOX_TOKEN = import.meta.env.VITE_MAPBOX_TOKEN || ''

const corCategoria = (categoria) => {
  const mapa = {
    'música': '#5eead4', 'música ao vivo': '#5eead4',
    teatro: '#f9a8d4', dança: '#c4b5fd', cinema: '#93c5fd',
    exposição: '#fcd34d', literatura: '#86efac', oficina: '#fdba74',
    festival: '#fb923c', feira: '#a3e635',
  }
  const k = (categoria || '').toLowerCase()
  for (const [key, cor] of Object.entries(mapa)) {
    if (k.includes(key)) return cor
  }
  return '#94a3b8'
}

function toSlug(str) {
  return (str || '')
    .normalize('NFD').replace(/[\u0300-\u036f]/g, '')
    .toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '')
}

function addMarkers() {
  if (!map) return
  markers.forEach(m => m.remove())
  markers = []

  const eventos = store.allEvents.filter(ev => ev.lat && ev.lng)

  eventos.forEach(ev => {
    const cor = corCategoria(ev.categoria)

    const el = document.createElement('div')
    el.className = 'marker-pin'
    el.style.cssText = `
      width: 28px; height: 28px; border-radius: 50% 50% 50% 0;
      transform: rotate(-45deg); cursor: pointer;
      background: ${cor}; border: 2px solid rgba(255,255,255,0.8);
      box-shadow: 0 2px 8px rgba(0,0,0,0.4);
      transition: transform 0.15s, box-shadow 0.15s;
    `
    el.addEventListener('mouseenter', () => {
      el.style.transform = 'rotate(-45deg) scale(1.2)'
      el.style.boxShadow = `0 4px 16px ${cor}66`
    })
    el.addEventListener('mouseleave', () => {
      el.style.transform = 'rotate(-45deg)'
      el.style.boxShadow = '0 2px 8px rgba(0,0,0,0.4)'
    })

    const precoLabel = ev.gratuito || ev.preco === 0
      ? 'Gratuito'
      : ev.preco != null ? `R$ ${Number(ev.preco).toFixed(0)}` : 'Consulte'

    const horaLabel = ev.inicio_iso
      ? new Date(ev.inicio_iso.includes('T') ? ev.inicio_iso : ev.inicio_iso + 'T00:00')
          .toLocaleString('pt-BR', { weekday: 'short', day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' })
      : ''

    const popupHtml = `
      <div style="font-family: sans-serif; max-width: 220px; padding: 2px;">
        <div style="font-size:10px; font-weight:700; text-transform:uppercase;
          letter-spacing:.06em; color:${cor}; margin-bottom:4px;">
          ${ev.categoria || 'Cultura'}
        </div>
        <div style="font-size:13px; font-weight:600; line-height:1.3; margin-bottom:6px; color:#1e293b;">
          ${ev.titulo}
        </div>
        ${horaLabel ? `<div style="font-size:11px; color:#64748b; margin-bottom:2px;">🕐 ${horaLabel}</div>` : ''}
        ${ev.local ? `<div style="font-size:11px; color:#64748b; margin-bottom:6px;">📍 ${ev.local}</div>` : ''}
        <div style="display:flex; align-items:center; justify-content:space-between; gap:8px;">
          <span style="font-size:11px; font-weight:700; padding:2px 8px; border-radius:999px;
            background:${ev.gratuito || ev.preco === 0 ? 'rgba(34,197,94,0.15)' : 'rgba(234,179,8,0.15)'};
            color:${ev.gratuito || ev.preco === 0 ? '#16a34a' : '#a16207'};">
            ${precoLabel}
          </span>
          <a href="/evento/${toSlug(ev.titulo)}"
            style="font-size:11px; font-weight:600; color:#0ea5e9; text-decoration:none;">
            Ver detalhes →
          </a>
        </div>
      </div>
    `

    const { Popup, Marker } = window.mapboxgl

    const popup = new Popup({ offset: 18, closeButton: true, maxWidth: '240px' })
      .setHTML(popupHtml)

    const marker = new Marker({ element: el })
      .setLngLat([ev.lng, ev.lat])
      .setPopup(popup)
      .addTo(map)

    markers.push(marker)
  })
}

async function initMap() {
  if (!MAPBOX_TOKEN) {
    mapError.value = 'Token do Mapbox não configurado. Adicione VITE_MAPBOX_TOKEN no seu arquivo .env'
    loadingMap.value = false
    return
  }

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

  // esconde o spinner e aguarda o DOM renderizar o container antes de inicializar
  loadingMap.value = false
  await nextTick()

  window.mapboxgl.accessToken = MAPBOX_TOKEN

  map = new window.mapboxgl.Map({
    container: mapContainer.value,
    style: 'mapbox://styles/mapbox/dark-v11',
    center: [-34.8770, -8.0476],
    zoom: 12,
  })

  map.addControl(new window.mapboxgl.NavigationControl(), 'top-right')

  map.on('load', () => {
    // garante que o mapa ocupa todo o container após o primeiro render
    map.resize()
    addMarkers()
  })
}

function localizarUsuario() {
  if (!navigator.geolocation || !map) return
  navigator.geolocation.getCurrentPosition(
    (pos) => {
      map.flyTo({ center: [pos.coords.longitude, pos.coords.latitude], zoom: 14, duration: 1200 })
      const el = document.createElement('div')
      el.style.cssText = `
        width:16px; height:16px; border-radius:50%;
        background:#3b82f6; border:3px solid white;
        box-shadow: 0 0 0 4px rgba(59,130,246,0.35);
      `
      new window.mapboxgl.Marker({ element: el })
        .setLngLat([pos.coords.longitude, pos.coords.latitude])
        .addTo(map)
      userLocated.value = true
    },
    () => {
      alert('Não foi possível obter sua localização.')
    }
  )
}

onMounted(async () => {
  await store.fetchEvents()
  await initMap()
})

onUnmounted(() => {
  if (map) { map.remove(); map = null }
})

watch(() => store.allEvents.length, () => addMarkers())
</script>

<template>
  <div class="mapa-page">
    <header class="top">
      <RouterLink to="/" class="back">← Voltar à agenda</RouterLink>
      <nav class="top-actions">
        <RouterLink to="/favoritos" class="top-link">♥ Salvos</RouterLink>
      </nav>
    </header>

    <div class="mapa-header">
      <h1 class="mapa-titulo">Mapa de eventos</h1>
      <button
        class="btn-localizar"
        @click="localizarUsuario"
        :class="{ 'btn-localizar--ativo': userLocated }"
      >
        {{ userLocated ? '📍 Você aqui' : '📍 Usar minha localização' }}
      </button>
    </div>

    <div v-if="mapError" class="map-error">
      <p>⚠️ {{ mapError }}</p>
      <p class="map-error__hint">
        Crie sua conta em <a href="https://mapbox.com" target="_blank" rel="noopener">mapbox.com</a>,
        copie o token público e adicione ao arquivo <code>frontend/.env</code>:
      </p>
      <code class="map-error__code">VITE_MAPBOX_TOKEN=pk.eyJ1Ijoixxxxxxx</code>
    </div>

    <!-- spinner fica por cima, container nunca some do DOM -->
    <div class="map-wrap">
      <div v-if="loadingMap" class="map-overlay">
        <div class="loading__bar" />
      </div>
      <div
        ref="mapContainer"
        class="map-container"
        aria-label="Mapa interativo de eventos em Recife"
      />
    </div>

    <div class="legenda" aria-label="Legenda de categorias">
      <span
        v-for="[cat, cor] in Object.entries({ 'Música': '#5eead4', 'Teatro': '#f9a8d4', 'Dança': '#c4b5fd', 'Cinema': '#93c5fd', 'Exposição': '#fcd34d', 'Literatura': '#86efac', 'Oficina': '#fdba74', 'Outros': '#94a3b8' })"
        :key="cat"
        class="legenda__item"
      >
        <span class="legenda__dot" :style="{ background: cor }" />
        {{ cat }}
      </span>
    </div>
  </div>
</template>

<style scoped>
.mapa-page {
  max-width: 1120px;
  margin: 0 auto;
  padding: 1.25rem 1.25rem 2rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-bottom: 1rem;
  border-bottom: 1px solid rgba(148, 163, 184, 0.2);
}
.back, .top-link {
  color: var(--oa-muted); font-weight: 600; font-size: 0.92rem; transition: color 0.15s;
}
.back:hover, .top-link:hover { color: var(--oa-text); }

.mapa-header {
  display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: .75rem;
}
.mapa-titulo {
  font-family: 'Fraunces', Georgia, serif; font-size: 1.65rem; margin: 0;
}

.btn-localizar {
  padding: 0.5rem 1rem; border-radius: 999px; font-weight: 700; font-size: 0.88rem;
  cursor: pointer; transition: all 0.15s;
  background: rgba(59,130,246,0.15); border: 1px solid rgba(59,130,246,0.35); color: #93c5fd;
}
.btn-localizar:hover { background: rgba(59,130,246,0.25); }
.btn-localizar--ativo { color: #60a5fa; border-color: rgba(59,130,246,0.6); }

/* wrapper mantém o espaço reservado o tempo todo */
.map-wrap {
  position: relative;
  width: 100%;
  height: 540px;
  border-radius: 16px;
  overflow: hidden;
  border: 1px solid rgba(148, 163, 184, 0.2);
}

/* spinner flutuante sobre o mapa */
.map-overlay {
  position: absolute;
  inset: 0;
  z-index: 10;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(15, 23, 42, 0.75);
  border-radius: 16px;
}

/* container do mapa ocupa todo o wrapper sempre */
.map-container {
  width: 100%;
  height: 100%;
}

.loading__bar {
  width: 48px; height: 48px; border-radius: 50%;
  border: 3px solid rgba(148,163,184,0.15); border-top-color: #5eead4;
  animation: spin 0.9s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

.map-error {
  padding: 1.5rem; border-radius: 12px;
  background: rgba(239,68,68,0.08); border: 1px solid rgba(239,68,68,0.25);
  font-size: 0.9rem; line-height: 1.6;
}
.map-error__hint { color: var(--oa-muted); margin-top: .5rem; }
.map-error a { color: #93c5fd; }
.map-error__code {
  display: block; margin-top: .5rem; padding: .5rem .75rem;
  background: rgba(2,6,23,0.5); border-radius: 8px;
  font-family: monospace; font-size: 0.82rem; color: #86efac;
}

.legenda {
  display: flex; flex-wrap: wrap; gap: 0.5rem; align-items: center;
  padding-top: 0.5rem;
}
.legenda__item {
  display: flex; align-items: center; gap: 0.3rem;
  font-size: 0.75rem; color: var(--oa-muted);
}
.legenda__dot {
  width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0;
}
</style>