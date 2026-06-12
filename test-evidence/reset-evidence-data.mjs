import { copyFile, mkdir, readdir, unlink } from 'node:fs/promises'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const ROOT = path.resolve(__dirname, '..')
const BASELINE = path.join(__dirname, 'baseline-events.json')
const EVENTS = path.join(ROOT, 'backend/data/events.json')
const UPLOADS = path.join(ROOT, 'backend/uploads')

async function main() {
  await mkdir(path.dirname(EVENTS), { recursive: true })
  await copyFile(BASELINE, EVENTS)

  try {
    const files = await readdir(UPLOADS)
    await Promise.all(
      files.map((file) => unlink(path.join(UPLOADS, file)).catch(() => {})),
    )
  } catch {
    // uploads folder may not exist yet
  }

  console.log('Dados resetados:', EVENTS)
}

main().catch((err) => {
  console.error(err)
  process.exit(1)
})
