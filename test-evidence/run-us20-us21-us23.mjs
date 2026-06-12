import { chromium } from 'playwright'
import { mkdir } from 'node:fs/promises'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const OUT = __dirname
const FLYER = path.join(OUT, 'teatro-no-recife-boa-viagem.png')
const BASE = process.env.FRONTEND_URL || 'http://localhost:9300'
const API = process.env.API_URL || 'http://127.0.0.1:8010'
const MOD_KEY = 'demo-moderador'

const MOCK = {
  manual: {
    titulo: 'Show Teste Sem Flyer US20',
    descricao: 'Evento de teste cadastrado sem flyer para moderacao.',
    bairro: 'Boa Viagem',
    local: 'Teatro Boa Viagem',
    inicio_iso: '2026-06-20T20:00',
    organizador: 'Produtor Teste US20',
    email: 'teste.us20@example.com',
  },
  flyer: {
    bairro: 'Boa Viagem',
    local: 'Centro Cultural Boa Viagem',
    inicio_iso: '2026-06-22T19:30',
    categoria: 'Teatro',
    organizador: 'Produtor Flyer US20',
    email: 'flyer.us20@example.com',
  },
  rejeicao: 'Flyer ausente e dados incompletos para teste US21',
}

async function hideChrome(page) {
  await page.addStyleTag({
    content: `
      .oa-footer, .q-footer, .q-layout__section--marginal { display: none !important; }
      .q-page { padding-bottom: 24px !important; }
    `,
  })
}

async function shotFocus(page, selector, name) {
  const el = page.locator(selector).first()
  await el.waitFor({ state: 'visible', timeout: 15000 })
  await el.scrollIntoViewIfNeeded()
  await page.waitForTimeout(400)
  await page.screenshot({
    path: path.join(OUT, name),
    clip: { x: 0, y: 0, width: 1440, height: 900 },
  })
}

async function shotElement(page, selector, name) {
  const el = page.locator(selector).first()
  await el.waitFor({ state: 'visible', timeout: 15000 })
  await el.scrollIntoViewIfNeeded()
  await page.waitForTimeout(400)
  await el.screenshot({ path: path.join(OUT, name) })
}

async function waitForImg(page, selector) {
  await page.locator(selector).first().waitFor({ state: 'visible', timeout: 15000 })
  await page.waitForFunction(
    (sel) => {
      const img = document.querySelector(sel)
      return img instanceof HTMLImageElement && img.complete && img.naturalWidth > 0
    },
    selector,
    { timeout: 15000 },
  )
}

async function assertServers() {
  const checks = [
    fetch(`${API}/events`).then((r) => (r.ok ? null : Promise.reject(new Error(`API ${r.status}`)))),
    fetch(`${BASE}/`).then((r) => (r.ok ? null : Promise.reject(new Error(`Frontend ${r.status}`)))),
  ]
  await Promise.all(checks)
}

async function main() {
  await mkdir(OUT, { recursive: true })
  await assertServers()

  const browser = await chromium.launch({ headless: true })
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } })

  // US20 — cadastro manual
  await page.goto(`${BASE}/cadastro`, { waitUntil: 'networkidle' })
  await hideChrome(page)
  await page.getByLabel('Titulo *').fill(MOCK.manual.titulo)
  await page.getByLabel('Descricao').fill(MOCK.manual.descricao)
  await page.getByLabel('Bairro').fill(MOCK.manual.bairro)
  await page.getByLabel('Local').fill(MOCK.manual.local)
  await page.getByLabel('Data/hora (ISO)').fill(MOCK.manual.inicio_iso)
  await page.getByLabel('Organizador *').fill(MOCK.manual.organizador)
  await page.getByLabel('E-mail de contato *').fill(MOCK.manual.email)
  await page.getByRole('button', { name: 'Enviar para moderacao' }).click()
  await page.getByText('Evento enviado para moderacao.').waitFor()
  await shotFocus(page, '.bg-positive', '01-moderacao-enviado-sem-flyer.png')

  // US20 — flyer preview
  await page.goto(`${BASE}/cadastro`, { waitUntil: 'networkidle' })
  await hideChrome(page)
  await page.locator('input[type="file"]').setInputFiles(FLYER)
  await page.getByRole('button', { name: 'Preparar flyer' }).click()
  await waitForImg(page, '.flyer-preview img')
  const titulo = await page.getByLabel('Titulo *').inputValue()
  if (!titulo.toLowerCase().includes('teatro')) {
    throw new Error(`Titulo sugerido inesperado: ${titulo}`)
  }
  await page.getByLabel('Bairro').fill(MOCK.flyer.bairro)
  await page.getByLabel('Local').fill(MOCK.flyer.local)
  await page.getByLabel('Data/hora (ISO)').fill(MOCK.flyer.inicio_iso)
  await page.getByRole('combobox', { name: 'Categoria' }).click()
  await page.getByRole('option', { name: MOCK.flyer.categoria }).click()
  await page.getByLabel('Organizador *').fill(MOCK.flyer.organizador)
  await page.getByLabel('E-mail de contato *').fill(MOCK.flyer.email)
  await page.getByLabel('Evento gratuito').click()
  await shotFocus(page, '.flyer-preview', '02-cadastro-flyer-preview.png')

  await page.getByRole('button', { name: 'Enviar para moderacao' }).click()
  await page.getByText('Evento enviado para moderacao.').waitFor()
  await shotFocus(page, '.bg-positive', '03-moderacao-enviado-com-flyer.png')

  // Feed não deve listar pendentes
  await page.goto(`${BASE}/`, { waitUntil: 'networkidle' })
  const feedHtml = await page.content()
  if (feedHtml.includes(MOCK.manual.titulo) || feedHtml.includes('Teatro No Recife Boa Viagem')) {
    throw new Error('Eventos pendentes apareceram no feed publico')
  }

  // US21 — moderação
  await page.goto(`${BASE}/moderacao`, { waitUntil: 'networkidle' })
  await hideChrome(page)
  await page.getByLabel('Moderator key').fill(MOD_KEY)
  await page.getByRole('button', { name: 'Carregar pendentes' }).click()
  await page.locator('.moderacao-list .q-item').first().waitFor({ timeout: 10000 })
  const count = await page.locator('.moderacao-list .q-item').count()
  if (count < 2) throw new Error(`Esperava 2 pendentes, achei ${count}`)
  await shotFocus(page, '.moderacao-layout', '04-moderacao-fila-carregada.png')

  const items = page.locator('.moderacao-list .q-item')
  await items.filter({ hasText: 'Teatro No Recife Boa Viagem' }).first().click()
  await waitForImg(page, '.detail-flyer img')
  await page.locator('.detail-grid').waitFor()
  await shotFocus(page, '.moderacao-detail', '05-moderacao-detalhe-flyer.png')
  await page.getByRole('button', { name: 'Aprovar' }).click()
  await page.locator('.moderacao-list .q-item').first().waitFor({ timeout: 10000 })

  await items.filter({ hasText: MOCK.manual.titulo }).first().click()
  await page.getByLabel('Motivo da rejeicao').fill(MOCK.rejeicao)
  await page.locator('.moderacao-detail').waitFor()
  await shotFocus(page, '.detail-actions', '06-moderacao-apos-acoes.png')
  await page.getByRole('button', { name: 'Rejeitar' }).click()
  await page.waitForTimeout(800)

  const pendentes = await fetch(`${API}/moderacao/pendentes`, {
    headers: { 'X-Moderator-Key': MOD_KEY },
  }).then((r) => r.json())
  if (pendentes.length !== 0) throw new Error('Ainda existem pendentes apos moderacao')

  // US23 — feed + chatbot
  await page.goto(`${BASE}/`, { waitUntil: 'networkidle' })
  await hideChrome(page)
  const eventCard = page.getByText('Teatro No Recife Boa Viagem').first()
  await eventCard.waitFor({ timeout: 10000 })
  await eventCard.scrollIntoViewIfNeeded()
  await page.waitForTimeout(600)
  const box = await eventCard.boundingBox()
  if (!box) throw new Error('Card do evento aprovado nao encontrado')
  const clipY = Math.max(0, Math.floor(box.y - 120))
  await page.screenshot({
    path: path.join(OUT, '07-feed-evento-aprovado.png'),
    clip: { x: 0, y: clipY, width: 1440, height: Math.min(900, 1440) },
  })

  await page.locator('.chatbot-fab').evaluate((el) => el.click())
  await page.locator('.chatbot-drawer').waitFor({ state: 'visible', timeout: 10000 })

  const perguntas = ['eventos gratuitos', 'o que tem em boa viagem?', 'teatro no recife']
  for (const [i, pergunta] of perguntas.entries()) {
    await page.getByPlaceholder('Pergunte por shows, teatro, gratis...').fill(pergunta)
    await page.getByRole('button', { name: 'Enviar' }).click()
    await page.waitForTimeout(2200)
    await shotElement(page, '.chatbot-drawer', `08-chatbot-${i + 1}.png`)
  }

  const chatText = await page.locator('.chatbot-stack').innerText()
  if (!chatText.includes('/evento/') && !chatText.toLowerCase().includes('nao encontrei')) {
    throw new Error('Chatbot sem links /evento/ nem fallback')
  }

  await page.goto(`${API}/docs`, { waitUntil: 'networkidle' })
  await page.waitForTimeout(800)
  await page.screenshot({
    path: path.join(OUT, '09-swagger-endpoints.png'),
    clip: { x: 0, y: 0, width: 1440, height: 900 },
  })

  console.log('OK: fluxo US20 -> US21 -> US23 concluido')
  await browser.close()
}

main().catch((err) => {
  console.error(err)
  process.exit(1)
})
