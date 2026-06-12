import { ref } from 'vue'
import { useApi } from './useApi'
import { toEventCardFromApi, toEventDetailFromApi } from 'src/utils/eventMapper'
import { sortEventsByPriorityAndDate } from 'src/utils/eventSorting'

export function useEventsApi() {
  const { getJson } = useApi()
  const loading = ref(false)
  const error = ref(null)

  async function fetchEvents({ limit = 100, ...filters } = {}) {
    loading.value = true
    error.value = null
    try {
      const params = new URLSearchParams({ per_page: String(limit) })
      if (filters.categoria) params.set('categoria', filters.categoria)
      if (filters.preco) params.set('preco', filters.preco)
      if (filters.bairro) params.set('bairro', filters.bairro)
      if (filters.data) params.set('data', filters.data)
      if (filters.agora) params.set('agora', 'true')

      const data = await getJson(`/events?${params}`)
      const rows = Array.isArray(data) ? data : (data?.results ?? [])
      const mapped = rows.map(toEventCardFromApi)
      return sortEventsByPriorityAndDate(mapped)
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Falha ao carregar eventos'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchEventBySlug(slug) {
    loading.value = true
    error.value = null
    try {
      const row = await getJson(`/events/${encodeURIComponent(slug)}`)
      return toEventDetailFromApi(row)
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Evento não encontrado'
      throw err
    } finally {
      loading.value = false
    }
  }

  return { loading, error, fetchEvents, fetchEventBySlug }
}
