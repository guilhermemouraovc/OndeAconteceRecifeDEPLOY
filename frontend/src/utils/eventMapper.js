import { DEFAULT_IMAGES } from 'src/constants/config'
import { generateSlug } from './stringUtils'

const MONTHS = ['JAN', 'FEV', 'MAR', 'ABR', 'MAI', 'JUN', 'JUL', 'AGO', 'SET', 'OUT', 'NOV', 'DEZ']

function formatDateRange(start) {
  if (!start) return 'Data a definir'
  const s = new Date(start.includes('T') ? start : `${start}T00:00:00`)
  if (Number.isNaN(s.getTime())) return 'Data a definir'
  return `${s.getDate()} ${MONTHS[s.getMonth()]}`
}

function formatPrice(value) {
  if (!value || value <= 0) return null
  return value.toLocaleString('pt-BR', {
    style: 'currency',
    currency: 'BRL',
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
  })
}

function formatPriceInfo(row) {
  const gratis = row.gratuito || row.preco === 0
  const preco = row.preco

  if (gratis) {
    return {
      hasPrice: false,
      formattedFullPrice: null,
      shouldShowInstallments: false,
    }
  }

  if (preco != null && preco > 0) {
    return {
      hasPrice: true,
      fullPrice: preco,
      formattedFullPrice: formatPrice(preco),
      shouldShowInstallments: false,
    }
  }

  const ml = row.classificacao_texto?.pago
  if (ml === 0) {
    return { hasPrice: false, formattedFullPrice: null, shouldShowInstallments: false }
  }
  if (ml === 1) {
    return { hasPrice: true, formattedFullPrice: 'Pago*', shouldShowInstallments: false }
  }

  return { hasPrice: false, formattedFullPrice: null, shouldShowInstallments: false }
}

export function toEventCardFromApi(row) {
  const slug = row.slug || generateSlug(row.titulo)
  const priceInfo = formatPriceInfo(row)

  return {
    id: slug,
    slug,
    title: row.titulo,
    description: row.descricao,
    date: formatDateRange(row.inicio_iso),
    start_date: row.inicio_iso,
    location: [row.local, row.bairro].filter(Boolean).join(' · '),
    cityState: row.bairro || 'Recife',
    image: row.image_url || DEFAULT_IMAGES.eventPlaceholder,
    link: { name: 'event-detail', params: { slug } },
    categoria: row.categoria,
    source: row.source,
    link_compra: row.link_compra,
    raw: row,
    ...priceInfo,
  }
}

export function toEventDetailFromApi(row) {
  const card = toEventCardFromApi(row)
  const start = row.inicio_iso
    ? new Date(row.inicio_iso.includes('T') ? row.inicio_iso : `${row.inicio_iso}T00:00:00`)
    : null

  return {
    ...card,
    dateLabel: start
      ? start.toLocaleDateString('pt-BR', {
          weekday: 'long',
          day: 'numeric',
          month: 'long',
          year: 'numeric',
        })
      : 'Data a definir',
    timeLabel: start
      ? start.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })
      : '',
    lat: row.lat,
    lng: row.lng,
    organizador: row.organizador,
    classificacao_texto: row.classificacao_texto,
  }
}

export function categoryColor(categoria) {
  const mapa = {
    música: '#5eead4',
    'música ao vivo': '#5eead4',
    teatro: '#f9a8d4',
    dança: '#c4b5fd',
    cinema: '#93c5fd',
    exposição: '#fcd34d',
    literatura: '#86efac',
    oficina: '#fdba74',
    festival: '#fb923c',
    feira: '#a3e635',
  }
  const k = (categoria || '').toLowerCase()
  for (const [key, cor] of Object.entries(mapa)) {
    if (k.includes(key)) return cor
  }
  return '#94a3b8'
}
