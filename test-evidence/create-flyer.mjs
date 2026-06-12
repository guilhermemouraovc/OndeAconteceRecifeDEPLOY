import { chromium } from 'playwright'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const out = path.join(__dirname, 'teatro-no-recife-boa-viagem.png')

const browser = await chromium.launch()
const page = await browser.newPage({ viewport: { width: 400, height: 600 } })
await page.setContent(`
  <html>
    <body style="margin:0;background:#0f3d5c;color:#fff;font-family:Arial,sans-serif;">
      <div style="border:4px solid #5eead4;margin:20px;height:560px;padding:32px;box-sizing:border-box;">
        <div style="font-size:34px;font-weight:700;line-height:1.1;">TEATRO NO</div>
        <div style="font-size:34px;font-weight:700;color:#eab308;line-height:1.1;">RECIFE</div>
        <div style="margin-top:48px;font-size:24px;color:#5eead4;">Boa Viagem</div>
        <div style="margin-top:24px;font-size:20px;">22 JUN · 19:30</div>
        <div style="margin-top:12px;font-size:18px;color:#cbd5e1;">Centro Cultural Boa Viagem</div>
      </div>
    </body>
  </html>
`)
await page.screenshot({ path: out })
await browser.close()
console.log('Flyer gerado:', out)
