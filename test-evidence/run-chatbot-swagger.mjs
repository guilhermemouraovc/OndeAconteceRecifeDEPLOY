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

  await page.goto(`${BASE}/`)
  await page.waitForTimeout(1500)
  await page.evaluate(() => document.querySelector('.chatbot-fab')?.click())
  await page.locator('.chatbot-title', { hasText: 'Assistente de agenda' }).waitFor({ state: 'visible', timeout: 10000 })

  const perguntas = ['eventos gratuitos', 'o que tem em boa viagem?', 'teatro no recife']
  for (const [i, pergunta] of perguntas.entries()) {
    const input = page.locator('.chatbot-form input')
    await input.waitFor({ state: 'visible' })
    await input.fill(pergunta)
    await page.locator('.chatbot-form button[type="submit"]').click()
    await page.waitForTimeout(3500)
    await shot(page, `08-chatbot-${i + 1}.png`)
  }

  const chatText = await page.locator('.chatbot-stack').innerText()
  console.log('CHAT SAMPLE:', chatText.slice(0, 500))
  if (!chatText.includes('/evento/') && !chatText.toLowerCase().includes('nao encontrei')) {
    throw new Error('Chatbot sem links /evento/ nem fallback')
  }

  await page.goto(`${API}/docs`)
  await page.waitForTimeout(1500)
  await shot(page, '09-swagger-endpoints.png')

  await browser.close()
  console.log('OK: chatbot e swagger capturados')
}

main().catch((err) => {
  console.error(err)
  process.exit(1)
})
