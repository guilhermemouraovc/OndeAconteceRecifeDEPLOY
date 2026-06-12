import { chromium } from 'playwright'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const OUT = __dirname
const FLYER = path.join(OUT, 'teatro-no-recife-boa-viagem.png')
const BASE = 'http://localhost:9300'

async function main() {
  const browser = await chromium.launch({ headless: true })
  const page = await browser.newPage({ viewport: { width: 1400, height: 900 } })
  await page.goto(`${BASE}/cadastro`)
  await page.locator('input[type="file"]').setInputFiles(FLYER)
  await page.getByRole('button', { name: 'Preparar flyer' }).click()
  await page.locator('.flyer-preview img').waitFor()
  await page.getByLabel('Bairro').fill('Boa Viagem')
  await page.getByLabel('Local').fill('Centro Cultural Boa Viagem')
  await page.getByLabel('Data/hora (ISO)').fill('2026-06-22T19:30')
  await page.getByRole('combobox', { name: 'Categoria' }).click()
  await page.getByRole('option', { name: 'Teatro' }).click()
  await page.getByLabel('Organizador *').fill('Produtor Flyer US20')
  await page.getByLabel('E-mail de contato *').fill('flyer.us20@example.com')
  await page.getByLabel('Evento gratuito').click()
  await page.getByRole('button', { name: 'Enviar para moderacao' }).click()
  await page.getByText('Evento enviado para moderacao.').waitFor()
  await page.screenshot({ path: path.join(OUT, '03-moderacao-enviado-com-flyer.png'), fullPage: true })
  await browser.close()
  console.log('OK: screenshot 03 capturado')
}

main().catch((e) => { console.error(e); process.exit(1) })
