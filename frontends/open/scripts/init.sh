#!/usr/bin/env bash
# =============================================================================
# AngelaMos | 2026
# init.sh
# =============================================================================
# Run once after copying the template.
# Prompts for a project name, randomizes ports, updates all the right files.

set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# ── prompt ────────────────────────────────────────────────────────────────────
echo ""
read -rp "Project name (kebab-case): " RAW

SLUG="$(echo "$RAW" | tr '[:upper:]' '[:lower:]' | tr ' ' '-' | tr -cd '[:alnum:]-')"
[[ -z "$SLUG" ]] && { echo "Error: empty name" >&2; exit 1; }

TITLE="$(echo "$SLUG" | tr '-' ' ' | python3 -c "import sys; print(sys.stdin.read().strip().title())")"

# ── ports ─────────────────────────────────────────────────────────────────────
mapfile -t ports < <(python3 -c "
import random
for p in random.sample(range(10000, 65001), 4): print(p)
")

PROD_NGINX=${ports[0]}
PROD_FRONTEND=${ports[1]}
DEV_NGINX=${ports[2]}
DEV_FRONTEND=${ports[3]}

echo ""
echo "  slug:            $SLUG"
echo "  title:           $TITLE"
echo "  prod  nginx:     $PROD_NGINX"
echo "  prod  frontend:  $PROD_FRONTEND"
echo "  dev   nginx:     $DEV_NGINX"
echo "  dev   frontend:  $DEV_FRONTEND"
echo ""

# ── .env (prod) ───────────────────────────────────────────────────────────────
sed -i "s|^APP_NAME=.*|APP_NAME=$SLUG|"                         "$DIR/.env"
sed -i "s|^VITE_APP_TITLE=.*|VITE_APP_TITLE=$TITLE|"           "$DIR/.env"
sed -i "s|^NGINX_HOST_PORT=.*|NGINX_HOST_PORT=$PROD_NGINX|"     "$DIR/.env"
sed -i "s|^FRONTEND_HOST_PORT=.*|FRONTEND_HOST_PORT=$PROD_FRONTEND|" "$DIR/.env"
echo "  updated .env"

# ── .env.development ──────────────────────────────────────────────────────────
sed -i "s|^APP_NAME=.*|APP_NAME=$SLUG-dev|"                          "$DIR/.env.development"
sed -i "s|^VITE_APP_TITLE=.*|VITE_APP_TITLE=\"$TITLE (Dev)\"|"       "$DIR/.env.development"
sed -i "s|^NGINX_HOST_PORT=.*|NGINX_HOST_PORT=$DEV_NGINX|"           "$DIR/.env.development"
sed -i "s|^FRONTEND_HOST_PORT=.*|FRONTEND_HOST_PORT=$DEV_FRONTEND|"  "$DIR/.env.development"
echo "  updated .env.development"

# ── .env.example ──────────────────────────────────────────────────────────────
sed -i "s|^APP_NAME=.*|APP_NAME=$SLUG|"                         "$DIR/.env.example"
sed -i "s|^VITE_APP_TITLE=.*|VITE_APP_TITLE=$TITLE|"           "$DIR/.env.example"
sed -i "s|^NGINX_HOST_PORT=.*|NGINX_HOST_PORT=$PROD_NGINX|"     "$DIR/.env.example"
sed -i "s|^FRONTEND_HOST_PORT=.*|FRONTEND_HOST_PORT=$PROD_FRONTEND|" "$DIR/.env.example"
echo "  updated .env.example"

# ── compose.yml ───────────────────────────────────────────────────────────────
sed -i "s|\${APP_NAME:-[a-z0-9-]*}|\${APP_NAME:-$SLUG}|g"                          "$DIR/compose.yml"
sed -i "s|\${NGINX_HOST_PORT:-[0-9]\+}|\${NGINX_HOST_PORT:-$PROD_NGINX}|g"         "$DIR/compose.yml"
echo "  updated compose.yml"

# ── dev.compose.yml ───────────────────────────────────────────────────────────
sed -i "s|\${APP_NAME:-[a-z0-9-]*}|\${APP_NAME:-$SLUG}|g"                          "$DIR/dev.compose.yml"
sed -i "s|\${NGINX_HOST_PORT:-[0-9]\+}|\${NGINX_HOST_PORT:-$DEV_NGINX}|g"          "$DIR/dev.compose.yml"
sed -i "s|\${FRONTEND_HOST_PORT:-[0-9]\+}|\${FRONTEND_HOST_PORT:-$DEV_FRONTEND}|g" "$DIR/dev.compose.yml"
echo "  updated dev.compose.yml"

# ── cloudflared.compose.yml ───────────────────────────────────────────────────
sed -i "s|\${APP_NAME:-[a-z0-9-]*}|\${APP_NAME:-$SLUG}|g" "$DIR/cloudflared.compose.yml"
echo "  updated cloudflared.compose.yml"

# ── react-scss/package.json ───────────────────────────────────────────────────
sed -i "s|\"name\": \".*\"|\"name\": \"$SLUG\"|" "$DIR/react-scss/package.json"
echo "  updated react-scss/package.json"

# ── react-scss/index.html ─────────────────────────────────────────────────────
sed -i "s|Full Stack Template No Auth|$TITLE|g" "$DIR/react-scss/index.html"
echo "  updated react-scss/index.html"

echo ""
echo "Done. Go build something."
