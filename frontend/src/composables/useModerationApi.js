import { ref } from 'vue'
import { useApi } from './useApi'

const defaultKey = import.meta.env.VITE_MODERATOR_KEY || 'demo-moderador'

export function useModerationApi() {
  const { getJsonWithHeaders, patchJson } = useApi()
  const loading = ref(false)
  const error = ref('')

  function buildHeaders(key) {
    const normalized = (key || defaultKey).trim()
    return { 'X-Moderator-Key': normalized }
  }

  async function fetchPendentes(key) {
    loading.value = true
    error.value = ''
    try {
      return await getJsonWithHeaders('/moderacao/pendentes', buildHeaders(key))
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Erro ao carregar pendentes.'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function aprovar(id, key) {
    return patchJson(`/moderacao/${encodeURIComponent(id)}/aprovar`, {}, buildHeaders(key))
  }

  async function rejeitar(id, motivo, key) {
    return patchJson(
      `/moderacao/${encodeURIComponent(id)}/rejeitar`,
      { motivo },
      buildHeaders(key),
    )
  }

  return { loading, error, defaultKey, fetchPendentes, aprovar, rejeitar }
}
