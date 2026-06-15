import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import { useEventsApi } from 'src/composables/useEventsApi'
import { toEventCardFromApi } from 'src/utils/eventMapper'
import { generateSlug } from 'src/utils/stringUtils'
import { normalizeString } from 'src/utils/stringUtils'

export const useEventsStore = defineStore('events', () => {
  const { fetchEvents: apiFetch, fetchEventBySlug } = useEventsApi()

  const allEvents = ref([])
  const loading = ref(false)
  const error = ref('')
  const lastFetch = ref(null)
  const searchQuery = ref('')

  const filterCategoria = ref('')
  const filterPreco = ref('')
  const filterBairro = ref('')
  const filterData = ref('')
  const filterAgora = ref(false)

  const sortOrder = ref('data')

  const PAGE_SIZE = 20
  const visibleCount = ref(PAGE_SIZE)

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

  async function fetchEvents(force = false) {
    const CACHE_MS = 60_000
    if (!force && lastFetch.value && Date.now() - lastFetch.value < CACHE_MS) return
    loading.value = true
    error.value = ''
    try {
      const cards = await apiFetch({ limit: 100 })
      allEvents.value = cards.map((c) => c.raw)
      lastFetch.value = Date.now()
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Não foi possível carregar os eventos.'
    } finally {
      loading.value = false
    }
  }

  function _hoje() {
    const d = new Date()
    d.setHours(0, 0, 0, 0)
    return d
  }

  function _startOf(d) {
    const c = new Date(d)
    c.setHours(0, 0, 0, 0)
    return c
  }

  function _endOf(d) {
    const c = new Date(d)
    c.setHours(23, 59, 59, 999)
    return c
  }

  function _parseEvtDate(iso) {
    if (!iso) return null
    return new Date(iso.includes('T') ? iso : `${iso}T00:00:00`)
  }

  const filteredEvents = computed(() => {
    const now = new Date()
    const hoje = _hoje()
    let list = allEvents.value

    if (searchQuery.value.trim()) {
      const q = normalizeString(searchQuery.value)
      list = list.filter((ev) => {
        const blob = normalizeString(`${ev.titulo} ${ev.descricao} ${ev.categoria} ${ev.bairro} ${ev.local}`)
        return blob.includes(q)
      })
    }

    list = list.filter((ev) => {
      if (filterCategoria.value) {
        const cat = (ev.categoria || '').toLowerCase()
        if (!cat.includes(filterCategoria.value.toLowerCase())) return false
      }
      if (filterPreco.value) {
        const preco = ev.preco ?? null
        const gratis = ev.gratuito || preco === 0
        if (filterPreco.value === 'gratuito' && !gratis) return false
        if (filterPreco.value === 'ate50' && (gratis || preco == null || preco > 50)) return false
        if (filterPreco.value === '50a100' && (preco == null || preco <= 50 || preco > 100)) return false
        if (filterPreco.value === 'acima100' && (preco == null || preco <= 100)) return false
      }
      if (filterBairro.value) {
        const b = (ev.bairro || '').toLowerCase()
        if (!b.includes(filterBairro.value.toLowerCase())) return false
      }
      if (filterData.value) {
        const dt = _parseEvtDate(ev.inicio_iso)
        if (!dt) return false
        if (filterData.value === 'hoje') {
          if (dt < _startOf(hoje) || dt > _endOf(hoje)) return false
        } else if (filterData.value === 'amanha') {
          const amanha = new Date(hoje)
          amanha.setDate(amanha.getDate() + 1)
          if (dt < _startOf(amanha) || dt > _endOf(amanha)) return false
        } else if (filterData.value === 'fds') {
          const day = dt.getDay()
          if (day !== 0 && day !== 6) return false
        } else if (filterData.value === 'semana') {
          const semana = new Date(hoje)
          semana.setDate(semana.getDate() + 7)
          if (dt < hoje || dt > semana) return false
        }
      }
      if (filterAgora.value) {
        const dt = _parseEvtDate(ev.inicio_iso)
        if (!dt) return false
        const tresHoras = new Date(now.getTime() + 3 * 60 * 60 * 1000)
        if (dt < now || dt > tresHoras) return false
      }
      return true
    })

    // Ordenação
    const sorted = [...list]
    if (sortOrder.value === 'data') {
      sorted.sort((a, b) => {
        const da = _parseEvtDate(a.inicio_iso)
        const db = _parseEvtDate(b.inicio_iso)
        if (!da && !db) return 0
        if (!da) return 1
        if (!db) return -1
        return da - db
      })
    } else if (sortOrder.value === 'preco_asc') {
      sorted.sort((a, b) => {
        const pa = a.gratuito || a.preco === 0 ? 0 : (a.preco ?? Infinity)
        const pb = b.gratuito || b.preco === 0 ? 0 : (b.preco ?? Infinity)
        return pa - pb
      })
    } else if (sortOrder.value === 'preco_desc') {
      sorted.sort((a, b) => {
        const pa = a.preco ?? -1
        const pb = b.preco ?? -1
        return pb - pa
      })
    }

    return sorted
  })

  // Total sem paginação (para mostrar "X de Y")
  const totalFilteredCount = computed(() => filteredEvents.value.length)

  // Eventos paginados
  const filteredEventsPaged = computed(() =>
    filteredEvents.value.slice(0, visibleCount.value),
  )

  const eventCards = computed(() => filteredEventsPaged.value.map(toEventCardFromApi))

  // Todos os cards sem paginação (usado na home)
  const allEventCards = computed(() => filteredEvents.value.map(toEventCardFromApi))

  const hasMore = computed(() => visibleCount.value < filteredEvents.value.length)

  function loadMore() {
    visibleCount.value += PAGE_SIZE
  }

  function resetPagination() {
    visibleCount.value = PAGE_SIZE
  }

  const eventosFavoritos = computed(() =>
    allEvents.value.filter((ev) => favoritos.value.includes(ev.titulo)).map(toEventCardFromApi),
  )

  const hasActiveFilters = computed(
    () =>
      !!(
        filterCategoria.value ||
        filterPreco.value ||
        filterBairro.value ||
        filterData.value ||
        filterAgora.value ||
        searchQuery.value.trim()
      ),
  )

  const bairrosDisponiveis = computed(() => {
    const set = new Set(allEvents.value.map((ev) => ev.bairro).filter(Boolean))
    return [...set].sort()
  })

  const categoriasDisponiveis = computed(() => {
    const set = new Set(allEvents.value.map((ev) => ev.categoria).filter(Boolean))
    return [...set].sort()
  })

  const eventsByCategory = computed(() => {
    const map = new Map()
    for (const card of allEventCards.value) {
      const cat = card.categoria || 'Outros'
      if (!map.has(cat)) map.set(cat, [])
      map.get(cat).push(card)
    }
    return map
  })

  function clearFilters() {
    filterCategoria.value = ''
    filterPreco.value = ''
    filterBairro.value = ''
    filterData.value = ''
    filterAgora.value = false
    searchQuery.value = ''
    resetPagination()
  }

  function getEventoBySlug(slug) {
    return (
      allEvents.value.find((ev) => ev.slug === slug || generateSlug(ev.titulo) === slug) || null
    )
  }

  async function loadEventDetail(slug) {
    const cached = getEventoBySlug(slug)
    if (cached) return toEventCardFromApi(cached)
    return fetchEventBySlug(slug)
  }

  return {
    allEvents,
    loading,
    error,
    searchQuery,
    filterCategoria,
    filterPreco,
    filterBairro,
    filterData,
    filterAgora,
    sortOrder,
    filteredEvents,
    filteredEventsPaged,
    totalFilteredCount,
    eventCards,
    allEventCards,
    hasMore,
    loadMore,
    resetPagination,
    eventosFavoritos,
    hasActiveFilters,
    bairrosDisponiveis,
    categoriasDisponiveis,
    eventsByCategory,
    favoritos,
    toggleFavorito,
    isFavorito,
    fetchEvents,
    clearFilters,
    getEventoBySlug,
    loadEventDetail,
  }
})