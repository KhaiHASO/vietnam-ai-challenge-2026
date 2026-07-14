[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$python = if ($env:PYTHON) { $env:PYTHON } else { 'python' }

Push-Location $root
try {
  & $python -m pytest backend/tests tests/ai_layer/rag -q
  Push-Location (Join-Path $root 'frontend')
  try {
    npm run test
    npm run type-check
    npm run lint
    npm run format:check
    npm run build
  } finally { Pop-Location }
  docker compose config | Out-Null
} finally { Pop-Location }
