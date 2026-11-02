#!/usr/bin/env bash
# =============================================================================
# AngelaMos | 2026
# install.sh
# =============================================================================
# Symlink the `template` command onto PATH so you can scaffold from anywhere.
# Re-run any time; it just refreshes the symlink. Source of truth stays in this
# repo, so editing a template here changes what `template` produces.
# =============================================================================

set -euo pipefail

command -v python3 >/dev/null 2>&1 || { echo "python3 is required" >&2; exit 1; }
python3 -c 'import sys; raise SystemExit(sys.version_info < (3, 10))' || {
  echo "Python 3.10 or newer is required" >&2
  exit 1
}

SELF="$(python3 -c 'from pathlib import Path; import sys; print(Path(sys.argv[1]).resolve())' "${BASH_SOURCE[0]}")"
TOOL_DIR="$(dirname "$SELF")"
BIN_DIR="${1:-$HOME/.local/bin}"

mkdir -p "$BIN_DIR"
if [[ -e "$BIN_DIR/template" || -L "$BIN_DIR/template" ]]; then
  [[ "$BIN_DIR/template" -ef "$TOOL_DIR/template" ]] || {
    echo "Refusing to replace an unrelated template command; choose another directory" >&2
    exit 1
  }
fi
chmod +x "$TOOL_DIR/template"
ln -sf "$TOOL_DIR/template" "$BIN_DIR/template"

echo "linked: $BIN_DIR/template -> $TOOL_DIR/template"
case ":$PATH:" in
  *":$BIN_DIR:"*) echo "ready. try: template list" ;;
  *) echo "note: $BIN_DIR is not on PATH. add it, e.g.:"
     echo "      export PATH=\"$BIN_DIR:\$PATH\"" ;;
esac
