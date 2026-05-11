const defaultBase = () =>
  import.meta.env.VITE_API_BASE_URL?.replace(/\/$/, '') || 'http://localhost:8000'

async function parseJson(res) {
  const text = await res.text()
  try {
    return text ? JSON.parse(text) : null
  } catch {
    return { detail: text || 'Resposta inválida' }
  }
}

export function useApi() {
  const base = defaultBase()

  async function getJson(path) {
    const res = await fetch(`${base}${path}`)
    const data = await parseJson(res)
    if (!res.ok) {
      const msg = data?.detail || res.statusText
      throw new Error(typeof msg === 'string' ? msg : JSON.stringify(msg))
    }
    return data
  }

  async function postJson(path, body) {
    const res = await fetch(`${base}${path}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    })
    const data = await parseJson(res)
    if (!res.ok) {
      const msg = data?.detail || res.statusText
      throw new Error(typeof msg === 'string' ? msg : JSON.stringify(msg))
    }
    return data
  }

  return { base, getJson, postJson }
}
