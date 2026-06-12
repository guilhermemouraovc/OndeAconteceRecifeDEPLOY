import { chromium } from 'playwright'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const OUT = __dirname
const BASE = 'http://localhost:9300'
const API = 'http://127.0.0.1:8010'

async function shot(page, name) {
  await page.screenshot({ path: path.join(OUT, name), fullPage: true })
}

async function main() {
  const browser = await chromium.launch({ headless: true })
  const page = await browser.newPage({ viewport: { width: 1400, height: 900 } })

  // US21
  await page.goto(`${BASE}/moderacao`)
  await page.getByLabel('Moderator key').fill('demo-moderador')
  await page.getByRole('button', { name: 'Carregar pendentes' }).click()
  await page.waitForTimeout(1200)
  await shot(page, '04-moderacao-fila-carregada.png')

  await page.locator('.moderacao-list .q-item').filter({ hasText: 'Teatro No Recife Boa Viagem' }).first().click()
  await page.locator('.detail-flyer img').waitFor()
  await shot(page, '05-moderacao-detalhe-flyer.png')
  await page.getByRole('button', { name: 'Aprovar' }).click()
  await page.waitForTimeout(1200)

  await page.locator('.moderacao-list .q-item').filter({ hasText: 'Show Teste Sem Flyer US20' }).first().click()
  await page.getByLabel('Motivo da rejeicao').fill('Dados incompletos e sem flyer para teste US21')
  await page.getByRole('button', { name: 'Rejeitar' }).click()
  await page.waitForTimeout(1200)
  await shot(page, '06-moderacao-apos-acoes.png')

  const pendentes = await fetch(`${API}/moderacao/pendentes`, {
    headers: { 'X-Moderator-Key': 'demo-moderador' },
  }).then((r) => r.json())
  const restantes = pendentes.filter((e) => e.titulo === 'Show Teste Sem Flyer US20')
  if (restantes.length > 0) {
    for (const ev of restantes) {
      await page.locator('.moderacao-list .q-item').filter({ hasText: ev.titulo }).first().click()
      await page.getByLabel('Motivo da rejeicao').fill('Duplicata de teste US20')
      await page.getByRole('button', { name: 'Rejeitar' }).click()
      await page.waitForTimeout(800)
    }
  }

  // US23
  await page.goto(`${BASE}/`)
  await page.waitForTimeout(2000)
  await page.getByText('Teatro No Recife Boa Viagem').first().waitFor({ timeout: 10000 })
  await shot(page, '07-feed-evento-aprovado.png')

  await page.getByRole('button', { name: 'Abrir chatbot' }).click({ force: true })
  await page.waitForTimeout(500)
  const perguntas = ['eventos gratuitos', 'o que tem em boa viagem?', 'teatro no recife']
  for (const [i, pergunta] of perguntas.entries()) {
    await page.getByPlaceholder('Pergunte por shows, teatro, gratis...').fill(pergunta)
    await page.getByRole('button', { name: 'Enviar' }).click()
    await page.waitForTimeout(3000)
    await shot(page, `08-chatbot-${i + 1}.png`)
  }

  const chatText = await page.locator('.chatbot-stack').innerText()
  if (!chatText.includes('/evento/') && !chatText.toLowerCase().includes('nao encontrei')) {
    throw new Error(`Chatbot sem links nem fallback: ${chatText.slice(0, 300)}`)
  }

  await page.goto(`${API}/docs`)
  await page.waitForTimeout(1500)
  await shot(page, '09-swagger-endpoints.png')

  const publicEvents = await fetch(`${API}/events`).then((r) => r.json())
  const aprovadoNoFeed = publicEvents.some((e) => e.titulo === 'Teatro No Recife Boa Viagem')
  const rejeitadoNoFeed = publicEvents.some((e) => e.titulo === 'Show Teste Sem Flyer US20')
  if (!aprovadoNoFeed) throw new Error('Evento aprovado nao aparece na API publica')
  if (rejeitadoNoFeed) throw new Error('Evento rejeitado aparece na API publica')

  console.log('OK: US21 e US23 concluidos')
  await browser.close()
}

main().catch((err) => {
  console.error(err)
  process.exit(1)
})
