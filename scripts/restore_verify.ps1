[CmdletBinding()]
param(
  [Parameter(Mandatory = $true)]
  [string]$BackupDirectory,
  [string]$ProjectName = "restore-verify-$([guid]::NewGuid().ToString('N').Substring(0, 8))"
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$resolvedBackup = (Resolve-Path $BackupDirectory).Path
foreach ($required in @("manifest.json", "mongo.archive.gz", "chromadb", "object-storage", "domains")) {
  if (-not (Test-Path (Join-Path $resolvedBackup $required))) { throw "Backup is missing $required" }
}

Push-Location $projectRoot
try {
  docker compose -p $ProjectName up -d mongodb redis chromadb backend
  $mongoContainer = (docker compose -p $ProjectName ps -q mongodb).Trim()
  if (-not $mongoContainer) { throw "Isolated MongoDB did not start." }
  docker compose -p $ProjectName cp (Join-Path $resolvedBackup "mongo.archive.gz") "${mongoContainer}:/tmp/mongo.archive.gz"
  docker compose -p $ProjectName exec -T mongodb mongorestore --archive=/tmp/mongo.archive.gz --gzip --drop
  docker compose -p $ProjectName cp (Join-Path $resolvedBackup "chromadb/.") chromadb:/data
  docker compose -p $ProjectName cp (Join-Path $resolvedBackup "object-storage/.") backend:/data
  docker compose -p $ProjectName restart chromadb backend
  docker compose -p $ProjectName exec -T backend python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health/ready')"
  docker compose -p $ProjectName exec -T backend python -c "from ai_layer.rag.core.dependencies import get_vector_store; assert get_vector_store('agriculture') is not None"
  Write-Output "Restore verification passed for compose project $ProjectName"
} finally {
  docker compose -p $ProjectName down -v --remove-orphans
  Pop-Location
}
