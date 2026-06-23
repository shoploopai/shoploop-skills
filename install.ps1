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

# Brief a fresh Codex via AGENTS.md (append a marked block; never overwrite).
if ((-not (Test-Path "AGENTS.md")) -or (-not (Select-String -Path "AGENTS.md" -Pattern "shoploop:start" -Quiet))) {
  $brief = @'

<!-- shoploop:start -->
## Shoploop video generation

This workspace generates no-watermark videos through **Shoploop**. When the user asks to create, make, render, or download a video (from text, one or more images, first+last frames, a reference video, or mixed references), use the **shoploop-video** skill and run its bundled CLI yourself — do not ask the user to run the commands.

Provider & privacy:
- Shoploop / Seedance is the only provider. Never mention, guess, or expose any hidden upstream vendor, internal model versions, or supplier tokens.
- The API key is `SHOPLOOP_KEY` in `.env.shoploop`. Never print, log, or commit it.
- If no key is configured yet (`.env.shoploop` missing, empty, or still `sk-your-customer-key`), ask the user for their Shoploop key and write it to `.env.shoploop` before generating. Never guess a key. Verify with `python3 .agents/skills/shoploop-video/scripts/shoploop.py --check-key`.

If the shoploop-video skill is not installed yet, install it, then make sure the key is set:

    npx skills add shoploopai/shoploop-skills --all

Generate with the bundled CLI (it auto-detects the mode; pass references when you have them):

    python3 .agents/skills/shoploop-video/scripts/shoploop.py "<prompt>" --duration 5 --aspect-ratio 9:16 --resolution 1080p --download shoploop_outputs/out.mp4

- image to video: add `--image-file /abs/path.png --mode image`
- first/last frame: two `--image-file` (first then last) + `--mode first-last`
- multi-reference: several `--image-file` + `--mode multi-reference`
- video reference: `--image-file ... --video-file /abs/clip.mp4 --mode video-reference`

Defaults & behavior:
- Model `seedance2.0`. Before generating, CONFIRM the output settings with the user (二次确认): duration (4-15s), resolution (e.g. 1080p), aspect ratio (e.g. 9:16). Suggest 5s/1080p/9:16 but never assume — wait for the user's go-ahead, then pass the confirmed values.
- Save outputs under `shoploop_outputs/`. The CLI prints the mp4 URL; use `--json` for machine-readable output.
- Rendering takes several minutes — do not assume an instant result.
- On HTTP 401 the key is missing or invalid; on a moderation failure, suggest a clearer or safer prompt. Report problems in Shoploop terms only.
<!-- shoploop:end -->
'@
  Add-Content -Path "AGENTS.md" -Value $brief -Encoding utf8
  Write-Host "Briefed Codex in AGENTS.md."
}

Write-Host ""
Write-Host "Done. Next:"
Write-Host "  1) Put your key in .env.shoploop  (SHOPLOOP_KEY=sk-...)"
Write-Host "  2) Start a NEW Codex session"
Write-Host "  3) Ask Codex:  make a 9:16 product video, 5 seconds"
