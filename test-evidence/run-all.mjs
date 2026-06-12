import { spawn } from 'node:child_process'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))

function run(nodeScript) {
  return new Promise((resolve, reject) => {
    const child = spawn(process.execPath, [nodeScript], {
      cwd: __dirname,
      stdio: 'inherit',
      env: process.env,
    })
    child.on('exit', (code) => {
      if (code === 0) resolve()
      else reject(new Error(`${path.basename(nodeScript)} exit ${code}`))
    })
  })
}

async function main() {
  await run(path.join(__dirname, 'create-flyer.mjs'))
  await run(path.join(__dirname, 'reset-evidence-data.mjs'))
  await run(path.join(__dirname, 'run-us20-us21-us23.mjs'))
  await run(path.join(__dirname, 'gerar-pdf.mjs'))
  console.log('Evidencias e PDF prontos em test-evidence/')
}

main().catch((err) => {
  console.error(err)
  process.exit(1)
})
