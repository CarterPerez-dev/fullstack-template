#!/usr/bin/env bash
# =============================================================================
# AngelaMos | 2026
# randomize-ports.sh
# =============================================================================
# Picks 4 unique random ports (10000-65000) and updates:
#   .env              -> prod nginx + frontend ports
#   .env.development  -> dev nginx + frontend ports
#   compose.yml       -> prod default fallbacks
#   dev.compose.yml   -> dev default fallbacks

set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

mapfile -t ports < <(python3 -c "
import random
sample = random.sample(range(10000, 65001), 4)
for p in sample: print(p)
")

PROD_NGINX=${ports[0]}
PROD_FRONTEND=${ports[1]}
DEV_NGINX=${ports[2]}
DEV_FRONTEND=${ports[3]}

echo "New ports:"
echo "  prod  nginx:    $PROD_NGINX"
echo "  prod  frontend: $PROD_FRONTEND"
echo "  dev   nginx:    $DEV_NGINX"
echo "  dev   frontend: $DEV_FRONTEND"
echo ""

update_env() {
  local file="$1" nginx_port="$2" frontend_port="$3"
  sed -i "s/^NGINX_HOST_PORT=.*/NGINX_HOST_PORT=$nginx_port/" "$file"
  sed -i "s/^FRONTEND_HOST_PORT=.*/FRONTEND_HOST_PORT=$frontend_port/" "$file"
  echo "  updated $file"
}

update_compose_defaults() {
  local file="$1" nginx_port="$2" frontend_port="${3:-}"
  sed -i "s/\${NGINX_HOST_PORT:-[0-9]\+}/\${NGINX_HOST_PORT:-$nginx_port}/g" "$file"
  if [[ -n "$frontend_port" ]]; then
    sed -i "s/\${FRONTEND_HOST_PORT:-[0-9]\+}/\${FRONTEND_HOST_PORT:-$frontend_port}/g" "$file"
  fi
  echo "  updated $file"
}

update_env        "$DIR/.env"              "$PROD_NGINX" "$PROD_FRONTEND"
update_env        "$DIR/.env.development"  "$DEV_NGINX"  "$DEV_FRONTEND"
update_compose_defaults "$DIR/compose.yml"     "$PROD_NGINX"
update_compose_defaults "$DIR/dev.compose.yml" "$DEV_NGINX" "$DEV_FRONTEND"

echo ""
echo "Done."
