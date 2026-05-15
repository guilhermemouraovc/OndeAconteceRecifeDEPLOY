import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import { useApi } from '@/composables/useApi.js'

export const useEventsStore = defineStore('events', () => {
  const { getJson } = useApi()

  // ── estado bruto ──────────────────────────────────────────────────────────
  const allEvents = ref([])
  const loading = ref(false)
  const error = ref('')
  const lastFetch = ref(null)

  // ── filtros ───────────────────────────────────────────────────────────────
  const filterCategoria = ref('')
  const filterPreco = ref('')       // 'gratuito' | 'ate50' | '50a100' | 'acima100'
  const filterBairro = ref('')
  const filterData = ref('')        // 'hoje' | 'amanha' | 'fds' | 'semana' | ''
  const filterAgora = ref(false)

  // ── favoritos (persistido em localStorage) ───────────────────────────────
  const _stored = localStorage.getItem('oa_favoritos')
  const favoritos = ref(_stored ? JSON.parse(_stored) : [])

  function toggleFavorito(titulo) {
    const idx = favoritos.value.indexOf(titulo)
    if (idx === -1) favoritos.value.push(titulo)
    else favoritos.value.splice(idx, 1)
    localStorage.setItem('oa_favoritos', JSON.stringify(favoritos.value))
  }

  function isFavorito(titulo) {
    return favoritos.value.includes(titulo)
  }

  // ── fetch ─────────────────────────────────────────────────────────────────
  async function fetchEvents(force = false) {
    const CACHE_MS = 60_000
    if (!force && lastFetch.value && Date.now() - lastFetch.value < CACHE_MS) return
    loading.value = true
    error.value = ''
    try {
      const data = await getJson('/events?per_page=100')
      // backend v0.2 retorna { total, page, per_page, results }
      // backend v0.1 retorna array direto — suporta ambos
      allEvents.value = Array.isArray(data) ? data : (data?.results ?? [])
      lastFetch.value = Date.now()
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Não foi possível carregar os eventos.'
    } finally {
      loading.value = false
    }
  }

  // ── helpers de data ───────────────────────────────────────────────────────
  function _hoje() {
    const d = new Date(); d.setHours(0,0,0,0); return d
  }
  function _startOf(d) {
    const c = new Date(d); c.setHours(0,0,0,0); return c
  }
  function _endOf(d) {
    const c = new Date(d); c.setHours(23,59,59,999); return c
  }
  function _parseEvtDate(iso) {
    if (!iso) return null
    return new Date(iso.includes('T') ? iso : iso + 'T00:00:00')
  }

  // ── eventos filtrados ─────────────────────────────────────────────────────
  const filteredEvents = computed(() => {
    const now = new Date()
    const hoje = _hoje()

    return allEvents.value.filter(ev => {
      // categoria
      if (filterCategoria.value) {
        const cat = (ev.categoria || '').toLowerCase()
        if (!cat.includes(filterCategoria.value.toLowerCase())) return false
      }

      // preço
      if (filterPreco.value) {
        const preco = ev.preco ?? null
        const gratis = ev.gratuito || preco === 0
        if (filterPreco.value === 'gratuito' && !gratis) return false
        if (filterPreco.value === 'ate50' && (gratis || preco == null || preco > 50)) return false
        if (filterPreco.value === '50a100' && (preco == null || preco <= 50 || preco > 100)) return false
        if (filterPreco.value === 'acima100' && (preco == null || preco <= 100)) return false
      }

      // bairro
      if (filterBairro.value) {
        const b = (ev.bairro || '').toLowerCase()
        if (!b.includes(filterBairro.value.toLowerCase())) return false
      }

      // data
      if (filterData.value) {
        const dt = _parseEvtDate(ev.inicio_iso)
        if (!dt) return false
        if (filterData.value === 'hoje') {
          if (dt < _startOf(hoje) || dt > _endOf(hoje)) return false
        } else if (filterData.value === 'amanha') {
          const amanha = new Date(hoje); amanha.setDate(amanha.getDate() + 1)
          if (dt < _startOf(amanha) || dt > _endOf(amanha)) return false
        } else if (filterData.value === 'fds') {
          const day = dt.getDay()
          if (day !== 0 && day !== 6) return false
        } else if (filterData.value === 'semana') {
          const semana = new Date(hoje); semana.setDate(semana.getDate() + 7)
          if (dt < hoje || dt > semana) return false
        }
      }

      // agora (próximas 3h)
      if (filterAgora.value) {
        const dt = _parseEvtDate(ev.inicio_iso)
        if (!dt) return false
        const tresHoras = new Date(now.getTime() + 3 * 60 * 60 * 1000)
        if (dt < now || dt > tresHoras) return false
      }

      return true
    })
  })

  const eventosFavoritos = computed(() =>
    allEvents.value.filter(ev => favoritos.value.includes(ev.titulo))
  )

  const hasActiveFilters = computed(() =>
    !!(filterCategoria.value || filterPreco.value || filterBairro.value || filterData.value || filterAgora.value)
  )

  const bairrosDisponiveis = computed(() => {
    const set = new Set(allEvents.value.map(ev => ev.bairro).filter(Boolean))
    return [...set].sort()
  })

  function clearFilters() {
    filterCategoria.value = ''
    filterPreco.value = ''
    filterBairro.value = ''
    filterData.value = ''
    filterAgora.value = false
  }

  function getEventoBySlug(slug) {
    return allEvents.value.find(ev => _toSlug(ev.titulo) === slug) || null
  }

  function _toSlug(str) {
    return (str || '')
      .normalize('NFD').replace(/[\u0300-\u036f]/g, '')
      .toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '')
  }

  return {
    allEvents, loading, error,
    filterCategoria, filterPreco, filterBairro, filterData, filterAgora,
    filteredEvents, eventosFavoritos, hasActiveFilters, bairrosDisponiveis,
    favoritos, toggleFavorito, isFavorito,
    fetchEvents, clearFilters, getEventoBySlug,
  }
})
