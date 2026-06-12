import { ref } from 'vue'
import { useApi } from './useApi'

export function useChatbot() {
  const { postJson } = useApi()
  const loading = ref(false)
  const error = ref('')
  const messages = ref([
    {
      role: 'assistant',
      text: 'Posso buscar eventos aprovados por categoria, bairro, data ou preco.',
    },
  ])

  async function sendMessage(text) {
    const content = text.trim()
    if (!content) return null

    messages.value.push({ role: 'user', text: content })
    loading.value = true
    error.value = ''
    try {
      const payload = {
        mensagem: content,
        historico: messages.value.slice(-6),
      }
      const response = await postJson('/chat', payload)
      messages.value.push({
        role: 'assistant',
        text: response.resposta,
        eventos: response.eventos_citados || [],
      })
      return response
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Falha ao consultar o chatbot.'
      messages.value.push({
        role: 'assistant',
        text: 'Nao consegui responder agora. Tente novamente em instantes.',
      })
      throw err
    } finally {
      loading.value = false
    }
  }

  function clearMessages() {
    messages.value = [
      {
        role: 'assistant',
        text: 'Posso buscar eventos aprovados por categoria, bairro, data ou preco.',
      },
    ]
  }

  return { loading, error, messages, sendMessage, clearMessages }
}
