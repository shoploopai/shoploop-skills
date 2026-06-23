#!/bin/sh
# Shoploop AI installer — installs the Shoploop Codex video skills via npx.
# Usage:  sh install.sh        (install into the current project)
#         sh install.sh -g     (install globally, available in every project)
set -e

GLOBAL=""
case "${1:-}" in
  -g|--global) GLOBAL="-g" ;;
esac

echo "Shoploop AI — installing Codex video skills..."

if ! command -v npx >/dev/null 2>&1; then
  echo "Error: Node.js / npx not found." >&2
  echo "Install Node.js from https://nodejs.org and run this again." >&2
  exit 1
fi

npx -y skills add shoploopai/shoploop-skills --all -a codex $GLOBAL

if [ -z "$GLOBAL" ] && [ ! -f .env.shoploop ]; then
  cat > .env.shoploop <<'EOF'
SHOPLOOP_KEY=sk-your-customer-key
SHOPLOOP_BASE=https://seedance.shoploopai.com
SHOPLOOP_MODEL=seedance2.0
EOF
  echo "Created .env.shoploop — set SHOPLOOP_KEY to your Shoploop key."
  if [ -f .gitignore ]; then
    grep -qx '.env.shoploop' .gitignore 2>/dev/null || printf '\n# Shoploop\n.env.shoploop\nshoploop_outputs/\n' >> .gitignore
  else
    printf '# Shoploop\n.env.shoploop\nshoploop_outputs/\n' > .gitignore
  fi
fi

echo ""
echo "Done. Next:"
echo "  1) Put your key in .env.shoploop  (SHOPLOOP_KEY=sk-...)"
echo "  2) Start a NEW Codex session"
echo "  3) Ask Codex:  make a 9:16 product video, 5 seconds"
