import { chromium } from 'playwright'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const html = path.join(__dirname, 'relatorio-ciclo3.html')
const pdf = path.join(__dirname, 'Relatorio-Ciclo3-OndeAconteceRecife.pdf')

const browser = await chromium.launch()
const page = await browser.newPage()
await page.goto(`file://${html}`, { waitUntil: 'networkidle' })
await page.waitForFunction(() => {
  const imgs = [...document.querySelectorAll('.evidence img')]
  return imgs.length > 0 && imgs.every((img) => img.complete && img.naturalHeight > 0)
})
await page.pdf({
  path: pdf,
  format: 'A4',
  printBackground: true,
  margin: { top: '14mm', bottom: '14mm', left: '12mm', right: '12mm' },
})
await browser.close()
console.log('PDF gerado:', pdf)
