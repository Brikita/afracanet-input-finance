// npm's portable entry point to the standard-library Python supervisor.
import { spawnSync } from 'node:child_process'
import { existsSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import path from 'node:path'

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')
const local = path.join(
  root,
  '.venv',
  process.platform === 'win32' ? 'Scripts/python.exe' : 'bin/python',
)
const python =
  process.env.AFRACANET_PYTHON ||
  (existsSync(local)
    ? local
    : process.platform === 'win32'
      ? 'python'
      : 'python3')
const child = spawnSync(
  python,
  [path.join(root, 'scripts/run_platform.py'), ...process.argv.slice(2)],
  { cwd: root, stdio: 'inherit' },
)
if (child.error) {
  console.error(
    'Python 3.13 is required. Set AFRACANET_PYTHON if it is not on PATH.',
  )
}
process.exit(child.status ?? 1)
