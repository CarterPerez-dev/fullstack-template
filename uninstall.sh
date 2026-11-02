#!/usr/bin/env bash
# ©AngelaMos | 2026
# uninstall.sh

set -euo pipefail

main() {
    local prefix="${TEMPLATE_INSTALL_DIR:-}"
    case "${1:-}" in
        --prefix)
            [[ $# -eq 2 && -n "$2" ]] || { printf '%s\n' '--prefix requires a directory' >&2; return 1; }
            prefix="$2" ;;
        -h|--help)
            printf '%s\n' 'Usage: bash uninstall.sh [--prefix DIR]' 'Removes the installed release command. Local development symlinks are preserved.'
            return 0 ;;
        "") ;;
        *) printf '%s\n' 'Unknown option' >&2; return 1 ;;
    esac
    python3 - "$prefix" <<'PY'
import json
from pathlib import Path
import shutil
import sys
import zipfile

located = shutil.which("template")
path = Path(sys.argv[1]).expanduser() / "template" if sys.argv[1] else Path(located or Path.home() / ".local/bin/template")
if path.is_symlink():
    raise SystemExit("Local development symlink preserved")
if not path.exists():
    print("template is already uninstalled")
    raise SystemExit(0)
try:
    with zipfile.ZipFile(path) as archive:
        metadata = json.loads(archive.read("release.json"))
        if "archives" not in metadata:
            raise ValueError("not a template release")
except (OSError, ValueError, KeyError, zipfile.BadZipFile):
    raise SystemExit(f"Refusing to remove an unrelated command: {path}") from None
path.unlink()
print("template uninstalled. Shared PATH entries and generated projects were preserved.")
PY
}

main "$@" </dev/null
