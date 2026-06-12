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

    return list.filter((ev) => {
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
  })

  const eventCards = computed(() => filteredEvents.value.map(toEventCardFromApi))

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
    for (const card of eventCards.value) {
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
    filteredEvents,
    eventCards,
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
