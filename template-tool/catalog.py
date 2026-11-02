"""
©AngelaMos | 2026
catalog.py
"""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Template:
    path: str
    kind: str
    namespace: str
    aliases: tuple[str, ...] = ()


CATALOG = {
    "go": Template("backends/go-backend", "go", "go-api", ("go-backend", "golang")),
    "fastapi": Template("backends/fastapi", "fastapi", "fastapi-api", ("api", "py", "python")),
    "open": Template("frontends/open", "open", "no-auth-template", ("no-auth", "noauth")),
    "frontend": Template("frontends/auth/react-scss", "frontend", "frontend-template", ("auth", "react", "web")),
    "native": Template("frontends/auth/react-native", "native", "native-template", ("mobile", "ios", "react-native")),
    "fastapi-stack": Template("stacks/fastapi-react", "fastapi-stack", "fastapi-react", ("fullstack", "stack", "fastapi-react")),
    "go-stack": Template("stacks/go-react", "go-stack", "go-api", ("go-react", "gostack")),
    "portfolio": Template("stacks/portfolio", "fastapi-stack", "portfolio-template", ("folio",)),
}

EXCLUDED_DIRS = {
    ".git", "node_modules", ".venv", "venv", ".mypy_cache", ".ruff_cache",
    ".pytest_cache", "__pycache__", ".pnpm-store", ".vite", "dist", "dist-ssr",
    "tmp", "bin", ".expo", ".tamagui", ".next", "web-build", "coverage", "htmlcov", "uploads",
}


def excluded(path: Path) -> bool:
    if any(part in EXCLUDED_DIRS for part in path.parts):
        return True
    name = path.name
    if name == ".env" or name.startswith(".env."):
        return not name.endswith(".example")
    if name in {".envrc", ".DS_Store", ".coverage", "Thumbs.db"}:
        return True
    return path.suffix.lower() in {
        ".pem", ".key", ".p12", ".pfx", ".p8", ".jks", ".keystore",
        ".mobileprovision", ".log", ".pyc",
    }


def source_files(root: Path):
    for path in sorted(root.iterdir()):
        if excluded(path.relative_to(root)):
            continue
        if path.is_symlink():
            raise ValueError(f"Template source contains a symlink: {path}")
        if path.is_dir():
            for child in source_files(path):
                if not excluded(child.relative_to(root)):
                    yield child
        elif path.is_file():
            yield path
        else:
            raise ValueError(f"Template source contains a special file: {path}")


def resolve(name: str) -> tuple[str, Template]:
    for key, entry in CATALOG.items():
        if name == key or name in entry.aliases:
            return key, entry
    raise ValueError(f"Unknown template {name!r}; run template list")
