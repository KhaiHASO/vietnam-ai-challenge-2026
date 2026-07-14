[CmdletBinding()]
param(
  [string]$BackupRoot = "backups"
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot

Push-Location $projectRoot
try {
  New-Item -ItemType Directory -Path $BackupRoot -Force | Out-Null
  $resolvedRoot = (Resolve-Path $BackupRoot).Path
  $stamp = Get-Date -Format "yyyyMMdd-HHmmss"
  $destination = [System.IO.Path]::GetFullPath((Join-Path $resolvedRoot $stamp))
  if (-not $destination.StartsWith($resolvedRoot + [System.IO.Path]::DirectorySeparatorChar, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "Backup destination must remain inside BackupRoot."
  }
  New-Item -ItemType Directory -Path $destination -Force | Out-Null

  $mongoContainer = (docker compose ps -q mongodb).Trim()
  if (-not $mongoContainer) { throw "MongoDB container is not running." }
  docker compose exec -T mongodb mongodump --archive=/tmp/mongo.archive.gz --gzip
  docker cp "${mongoContainer}:/tmp/mongo.archive.gz" (Join-Path $destination "mongo.archive.gz")
  docker compose exec -T mongodb rm -f /tmp/mongo.archive.gz

  docker compose cp chromadb:/data (Join-Path $destination "chromadb")
  docker compose cp backend:/data (Join-Path $destination "object-storage")
  Copy-Item -LiteralPath (Join-Path $projectRoot "domains") -Destination (Join-Path $destination "domains") -Recurse -Force
  [ordered]@{
    created_at = (Get-Date).ToUniversalTime().ToString("o")
    compose_project = (docker compose ls --format json | ConvertFrom-Json | Select-Object -First 1).Name
    schema = "ai-native-backup-v1"
  } | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $destination "manifest.json") -Encoding utf8

  Write-Output "Backup created: $destination"
} finally {
  Pop-Location
}
