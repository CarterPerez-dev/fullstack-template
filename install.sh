#!/usr/bin/env bash
# ©AngelaMos | 2026
# install.sh

set -euo pipefail

REPOSITORY="CarterPerez-dev/Fullstack-setup"
INSTALL_DIR="${TEMPLATE_INSTALL_DIR:-}"
VERSION="${TEMPLATE_VERSION:-latest}"
FROM_DIR=""
TMP_DIR=""
MODIFY_PATH=1
COLOR=""
RESET=""
if [[ -t 2 && -z "${NO_COLOR:-}" ]]; then
    COLOR=$'\033[36m'
    RESET=$'\033[0m'
fi

info() { printf '%stemplate%s: %s\n' "$COLOR" "$RESET" "$*" >&2; }
die() { info "$*"; exit 1; }
have() { command -v "$1" >/dev/null 2>&1; }
cleanup() {
    if [[ -n "$TMP_DIR" ]]; then
        rm -rf -- "$TMP_DIR"
    fi
    return 0
}
trap cleanup EXIT
trap 'info "installation failed; the previous command has been preserved where possible"' ERR

usage() {
    cat <<'EOF'
Install the template command and download only the stack you later select.

  curl -fsSL https://angelamos.com/template/install.sh | bash
  bash install.sh --prefix /path/already/on/PATH

Options:
  --prefix DIR       Command installation directory
  --version TAG      Pin a release, for example v0.1.0 (default: latest)
  --from DIR         Install checked local release artifacts without networking
  --no-modify-path   Do not edit shell configuration
  -h, --help         Show this help

Environment: TEMPLATE_INSTALL_DIR, TEMPLATE_VERSION, NO_COLOR.
EOF
}

download() {
    if have curl; then
        curl --fail --silent --show-error --location --retry 3 \
            --connect-timeout 10 --max-time 120 --proto '=https' \
            --proto-redir '=https' --tlsv1.2 "$1" --output "$2"
    elif have wget; then
        wget --https-only --timeout=30 --tries=3 -qO "$2" "$1"
    else
        die "curl or wget is required to download release assets"
    fi
}

as_root() {
    if [[ "$(id -u)" -eq 0 ]]; then
        "$@"
    elif have sudo; then
        sudo -n "$@"
    else
        die "Installing Python requires root or noninteractive sudo"
    fi
}

ensure_python() {
    if have python3 && python3 -c 'import sys; raise SystemExit(sys.version_info < (3, 10))'; then
        return
    fi
    info "Installing Python 3"
    if have apt-get; then
        as_root apt-get update
        as_root apt-get install -y python3 ca-certificates
    elif have dnf; then
        as_root dnf install -y python3 ca-certificates
    elif have pacman; then
        as_root pacman -S --needed --noconfirm python ca-certificates
    elif have zypper; then
        as_root zypper --non-interactive install python3 ca-certificates
    elif have apk; then
        as_root apk add python3 ca-certificates
    elif have brew; then
        brew install python
    else
        die "No supported package manager found for Python 3.10 or newer"
    fi
    python3 -c 'import sys; raise SystemExit(sys.version_info < (3, 10))' || die "Python 3.10 or newer is required"
}

main() {
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --prefix|--version|--from)
                [[ $# -ge 2 && -n "$2" ]] || die "$1 requires a value"
                case "$1" in
                    --prefix) INSTALL_DIR="$2" ;;
                    --version) VERSION="$2" ;;
                    --from) FROM_DIR="$2" ;;
                esac
                shift 2 ;;
            --no-modify-path) MODIFY_PATH=0; shift ;;
            -h|--help) usage; return 0 ;;
            *) die "Unknown option: $1" ;;
        esac
    done
    case "$(uname -s)/$(uname -m)" in
        Linux/x86_64|Linux/aarch64|Linux/arm64|Darwin/x86_64|Darwin/arm64) ;;
        *) die "Supported platforms: Linux and macOS on x86_64 or arm64; use WSL on Windows" ;;
    esac
    info "+----------+"
    info "| template |  Opinionated stacks, one command."
    info "+----------+"
    ensure_python
    TMP_DIR="$(mktemp -d "${TMPDIR:-/tmp}/template-install.XXXXXXXX")"
    if [[ -n "$FROM_DIR" ]]; then
        cp -- "$FROM_DIR/template.pyz" "$TMP_DIR/template.pyz"
        cp -- "$FROM_DIR/checksums.txt" "$TMP_DIR/checksums.txt"
    else
        [[ "$VERSION" == latest || "$VERSION" =~ ^v[0-9]+\.[0-9]+\.[0-9]+(-[A-Za-z0-9.-]+)?$ ]] || die "Invalid release tag"
        local endpoint="https://api.github.com/repos/$REPOSITORY/releases/latest"
        if [[ "$VERSION" != latest ]]; then
            endpoint="https://api.github.com/repos/$REPOSITORY/releases/tags/$VERSION"
        fi
        download "$endpoint" "$TMP_DIR/github-release.json"
        VERSION="$(python3 - "$TMP_DIR/github-release.json" <<'PY'
import json
import re
import sys

with open(sys.argv[1], encoding="utf-8") as stream:
    release = json.load(stream)
tag = release.get("tag_name", "")
if release.get("draft") or not re.fullmatch(r"v[0-9]+\.[0-9]+\.[0-9]+(?:-[A-Za-z0-9.-]+)?", tag):
    raise SystemExit("Invalid public release metadata")
print(tag)
PY
)"
        local base="https://github.com/$REPOSITORY/releases/download/$VERSION"
        download "$base/template.pyz" "$TMP_DIR/template.pyz"
        download "$base/checksums.txt" "$TMP_DIR/checksums.txt"
    fi
    python3 - "$TMP_DIR" "$INSTALL_DIR" "$MODIFY_PATH" "$FROM_DIR" "$VERSION" <<'PY'
import hashlib
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import tempfile
import zipfile

temporary, requested, modify, local, requested_version = sys.argv[1:]
source = Path(temporary) / "template.pyz"
expected = []
for line in (Path(temporary) / "checksums.txt").read_text().splitlines():
    parts = line.split()
    if len(parts) == 2 and parts[1] == "template.pyz":
        expected.append(parts[0])
if len(expected) != 1 or hashlib.sha256(source.read_bytes()).hexdigest() != expected[0]:
    raise SystemExit("Release checksum verification failed")
with zipfile.ZipFile(source) as archive:
    metadata = json.loads(archive.read("release.json"))
if not local and (metadata.get("dirty") or metadata.get("version") != requested_version):
    raise SystemExit("Public artifact is dirty or does not match the requested release")
subprocess.run([sys.executable, str(source), "--version"], check=True)
path_dirs = [Path(item).expanduser() for item in os.environ.get("PATH", "").split(os.pathsep) if item and Path(item).is_absolute()]
preferred = Path.home() / ".local" / "bin"
if requested:
    prefix = Path(requested).expanduser().absolute()
elif preferred in path_dirs:
    prefix = preferred
else:
    candidates = [path for path in path_dirs if path.is_relative_to(Path.home()) and path.is_dir() and os.access(path, os.W_OK)]
    prefix = candidates[0] if candidates else preferred
prefix.mkdir(parents=True, exist_ok=True)
destination = prefix / "template"
if destination.is_symlink():
    raise SystemExit(f"Keeping existing development symlink: {destination}. Choose a different --prefix.")
if destination.exists():
    try:
        with zipfile.ZipFile(destination) as existing:
            old = json.loads(existing.read("release.json"))
            if "archives" not in old:
                raise ValueError("not a template release")
    except (OSError, ValueError, KeyError, zipfile.BadZipFile):
        raise SystemExit(f"Refusing to replace an unrelated command: {destination}") from None
descriptor, staged_name = tempfile.mkstemp(prefix=".template-install-", dir=prefix)
staged = Path(staged_name)
try:
    with os.fdopen(descriptor, "wb") as output:
        output.write(source.read_bytes())
    staged.chmod(0o755)
    os.replace(staged, destination)
finally:
    staged.unlink(missing_ok=True)
if prefix not in path_dirs:
    if modify == "1":
        shell = Path(os.environ.get("SHELL", "bash")).name
        if shell == "fish":
            rc = Path.home() / ".config/fish/conf.d/template.fish"
            line = f"fish_add_path -- {shlex.quote(str(prefix))}"
        else:
            rc = Path.home() / ({"zsh": ".zshrc", "bash": ".bashrc"}.get(shell, ".profile"))
            line = f"export PATH={shlex.quote(str(prefix))}:\"$PATH\""
        rc.parent.mkdir(parents=True, exist_ok=True)
        content = rc.read_text() if rc.exists() else ""
        if line not in content.splitlines():
            with rc.open("a") as output:
                output.write("\n" + line + "\n")
        print(f"PATH configured in {rc}. For this existing shell: {line}", file=sys.stderr)
    else:
        print(f"Install directory is not on this shell's PATH: {prefix}", file=sys.stderr)
verification_env = os.environ.copy()
verification_env["PATH"] = str(prefix) + os.pathsep + verification_env.get("PATH", "")
subprocess.run(["template", "--version"], env=verification_env, check=True)
print(f"Installed template in {prefix}", file=sys.stderr)
PY
    info "Try: template list"
    info "Create a project: template fastapi-stack my-app"
    if have just; then
        info "Generated projects expose their available commands through just."
    fi
    info "Docs: https://github.com/$REPOSITORY/tree/main/template-tool"
}

main "$@" </dev/null
