"""
©AngelaMos | 2026
rewrite.py
"""
# Safe identity + port rewriter for the `template` scaffolder.
# Reads every text file in a freshly-copied template, swaps the template's
# default identifiers (module path, app names, titles, image names) for the new
# project's, and randomizes every host port so prod + dev never collide with an
# existing project. Every write is read-replace-write -- never an in-place sed.

import argparse
import base64
import re
import secrets
import socket
import sys
from pathlib import Path

# The one string every Go template ships with, in go.mod and ~15 imports.
OLD_MODULE = "github.com/carterperez-dev/templates/go-backend"

CONTAINER_PORTS = {"8080", "8000", "5432", "6379", "80", "5173"}

SKIP_DIRS = {
    ".git", "node_modules", ".venv", "venv", ".mypy_cache", ".ruff_cache",
    ".pytest_cache", ".pnpm-store", ".vite", "dist", "dist-ssr", "__pycache__",
    "tmp", "bin", ".expo",
}


def is_text(path: Path) -> bool:
    try:
        chunk = path.read_bytes()[:8192]
    except OSError:
        return False
    if b"\x00" in chunk:
        return False
    return True


def gen_secret() -> str:
    return base64.b64encode(secrets.token_bytes(32)).decode()


class Ports:
    """Hands out unique random host ports, memoized per (scope, key)."""

    def __init__(self) -> None:
        self.used: set[int] = set()
        self.by_key: dict[tuple[str, str], int] = {}
        self.availability_checked = True

    def _fresh(self) -> int:
        while True:
            p = secrets.randbelow(30001) + 30000
            if p in self.used:
                continue
            if self.availability_checked:
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
                        listener.bind(("127.0.0.1", p))
                except PermissionError:
                    self.availability_checked = False
                    print("template: host port probing is unavailable; assigned ports need checking before startup", file=sys.stderr)
                except OSError:
                    continue
            self.used.add(p)
            return p

    def get(self, scope: str, key: str) -> int:
        k = (scope, key)
        if k not in self.by_key:
            self.by_key[k] = self._fresh()
        return self.by_key[k]


def scope_of(path: Path) -> str:
    name = path.name
    if name == ".env.development" or "dev.compose" in name:
        return "dev"
    return "prod"


def build_replacements(
    slug: str, title: str, owner: str, base: str
) -> list[tuple[str, str]]:
    new_module = f"github.com/{owner}/{slug}"
    reps: list[tuple[str, str]] = []
    # Base = the template's literal compose project namespace (e.g. `go-api`,
    # `no-auth-template`). Apply it FIRST so it can never chew a substring out of
    # the new module path inserted below (str.replace is single-pass).
    if base:
        reps.append((base, slug))
    reps += [
        (OLD_MODULE, new_module),
        ('"name": "frontend-template"', f'"name": "{slug}"'),
        ('name = "full-stack-template"', f'name = "{slug}"'),
        ('name: "Go Backend Template"', f'name: "{title}"'),
        ('issuer: "go-backend"', f'issuer: "{slug}"'),
        ("YOUR_APP_SLUG", slug),       # react-native package.json
        ("YOUR_APP_NAME", title),      # react-native app.json display name
        ("YOUR_URL_SCHEME", slug),
        ("YOUR_BUNDLE_ID", f"dev.{owner.lower().replace('-', '')}.{slug.replace('-', '')}"),
        ("com.yourcompany.app.auth", f"dev.{owner.lower().replace('-', '')}.{slug.replace('-', '')}.auth"),
    ]
    return reps


def rewrite_file(path: Path, slug: str, title: str, literals, ports: Ports) -> bool:
    text = path.read_text(encoding="utf-8", errors="surrogateescape")
    orig = text
    scope = scope_of(path)
    name = path.name

    # 1. literal identity swaps (namespace base, module path, package/config names)
    for old, new in literals:
        text = text.replace(old, new)

    # 2. host-port compose defaults: ${X_HOST_PORT:-1234} -> assigned port
    def _compose_port(m: re.Match) -> str:
        key = m.group(1)
        return "${" + key + ":-" + str(ports.get(scope, key)) + "}"

    text = re.sub(r"\$\{([A-Z0-9_]*_HOST_PORT):-\d+\}", _compose_port, text)

    # 4. literal "HOST:CONTAINER" compose mappings (the Go templates)
    if "compose" in name and name.endswith((".yml", ".yaml")):
        def _literal_port(m: re.Match) -> str:
            container = m.group(2)
            if container in CONTAINER_PORTS or container in {"4317", "4318", "16686"}:
                return f'"{ports.get(scope, "svc:" + container)}:{container}"'
            return m.group(0)

        text = re.sub(r'"(\d+):(\d+)"', _literal_port, text)

    # 5. .env line-level rewrites
    if name.startswith(".env"):
        is_example = name == ".env.example"
        dev = scope == "dev"

        def _env_line(m: re.Match) -> str:
            key, val = m.group(1), m.group(2)
            if key == "APP_NAME":
                # APP_NAME is the app's display title now (namespace is literal).
                return f'APP_NAME="{title} (Dev)"' if dev else f"APP_NAME={title}"
            if key == "VITE_APP_TITLE":
                if dev:
                    return f'VITE_APP_TITLE="{title} (Dev)"'
                return f"VITE_APP_TITLE={title}"
            if key == "OTEL_SERVICE_NAME":
                return f"OTEL_SERVICE_NAME={slug}"
            if key == "ENVIRONMENT":
                return "ENVIRONMENT=development" if dev else "ENVIRONMENT=production"
            if key == "DEBUG":
                return "DEBUG=false"
            if key == "RELOAD":
                return f"RELOAD={'true' if dev else 'false'}"
            if key == "ADMIN_EMAIL" and not val.strip():
                return ""
            if key.endswith("_HOST_PORT"):
                return f"{key}={ports.get(scope, key)}"
            if key in {"POSTGRES_PASSWORD", "REDIS_PASSWORD"} and not is_example:
                return f"{key}={secrets.token_hex(24)}"
            if key == "SECRET_KEY" and not is_example:
                if "CHANGE_ME" in val or val.strip() == "":
                    return f"SECRET_KEY={gen_secret()}"
            return m.group(0)

        text = re.sub(
            r"^([A-Z0-9_]+)=(.*)$", _env_line, text, flags=re.MULTILINE
        )

    # 6. index.html <title>
    if name == "index.html":
        text = re.sub(r"<title>.*?</title>", f"<title>{title}</title>", text)

    if text != orig:
        path.write_text(text, encoding="utf-8", errors="surrogateescape")
        return True
    return False


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", required=True)
    ap.add_argument("--kind", required=True)
    ap.add_argument("--slug", required=True)
    ap.add_argument("--title", required=True)
    ap.add_argument("--owner", default="CarterPerez-dev")
    ap.add_argument("--base", default="", help="template's literal compose namespace")
    args = ap.parse_args()

    root = Path(args.target).resolve()
    literals = build_replacements(args.slug, args.title, args.owner, args.base)
    ports = Ports()

    changed = 0
    for path in sorted(root.rglob("*")):
        if any(part in SKIP_DIRS for part in path.relative_to(root).parts):
            continue
        if not path.is_file() or path.is_symlink():
            continue
        if not is_text(path):
            continue
        try:
            if rewrite_file(path, args.slug, args.title, literals, ports):
                changed += 1
        except (OSError, UnicodeDecodeError) as exc:
            print(f"  cannot rewrite {path}: {exc}", file=sys.stderr)
            return 1

    print(f"  rewrote {changed} file(s)")
    if ports.by_key:
        shown = ", ".join(
            f"{k[1].replace('svc:', '')}={v}" for k, v in sorted(ports.by_key.items())
        )
        print(f"  ports: {shown}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
