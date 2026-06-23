# Shoploop AI installer (Windows) — installs the Shoploop Codex video skills via npx.
# Usage:  powershell -ExecutionPolicy Bypass -File install.ps1
$ErrorActionPreference = "Stop"
Write-Host "Shoploop AI - installing Codex video skills..."

if (-not (Get-Command npx -ErrorAction SilentlyContinue)) {
  Write-Error "Node.js / npx not found. Install Node.js from https://nodejs.org and run again."
  exit 1
}

npx -y skills add shoploopai/shoploop-skills --all -a codex

if (-not (Test-Path ".env.shoploop")) {
@"
SHOPLOOP_KEY=sk-your-customer-key
SHOPLOOP_BASE=https://seedance.shoploopai.com
SHOPLOOP_MODEL=seedance2.0
"@ | Out-File -Encoding ascii .env.shoploop
  Write-Host "Created .env.shoploop - set SHOPLOOP_KEY to your Shoploop key."
}

Write-Host ""
Write-Host "Done. Next:"
Write-Host "  1) Put your key in .env.shoploop  (SHOPLOOP_KEY=sk-...)"
Write-Host "  2) Start a NEW Codex session"
Write-Host "  3) Ask Codex:  make a 9:16 product video, 5 seconds"
