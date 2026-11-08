"""
©AngelaMos | 2026
cli.py
"""

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import urllib.request
from urllib.parse import urlsplit
import zipfile

from catalog import CATALOG, excluded, resolve, source_files
from rewrite import Ports, build_replacements, is_text, rewrite_file


REPOSITORY = "CarterPerez-dev/fullstack-template"
MAX_ARCHIVE_BYTES = 64 * 1024 * 1024
MAX_EXTRACTED_BYTES = 512 * 1024 * 1024


def release_metadata() -> dict:
    executable = Path(sys.argv[0]).resolve()
    if executable.is_file() and zipfile.is_zipfile(executable):
        with zipfile.ZipFile(executable) as archive:
            return json.loads(archive.read("release.json"))
    return {"version": "development", "revision": None, "dirty": True}


def copy_source(source: Path, target: Path) -> None:
    if not source.is_dir() or source.is_symlink():
        raise ValueError(f"Template source is not a regular directory: {source}")
    for path in source_files(source):
        dest = target / path.relative_to(source)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, dest)
        dest.chmod(0o755 if path.stat().st_mode & 0o111 else 0o644)


def extract_archive(path: Path, target: Path) -> None:
    with tarfile.open(path, "r:gz") as archive:
        members = archive.getmembers()
        total_size = 0
        names = set()
        if len(members) > 20000:
            raise ValueError("Archive contains too many entries")
        for member in members:
            name = PurePosixPath(member.name)
            if (name.is_absolute() or ".." in name.parts or "\\" in member.name
                    or not name.parts or str(name) != member.name):
                raise ValueError(f"Unsafe archive path: {member.name!r}")
            if not member.isfile() or member.name in names or excluded(Path(*name.parts)):
                raise ValueError(f"Unsupported archive entry: {member.name!r}")
            names.add(member.name)
            total_size += member.size
            if member.size < 0 or total_size > MAX_EXTRACTED_BYTES:
                raise ValueError("Archive exceeds the extraction size limit")
        for member in members:
            dest = target / member.name
            dest.parent.mkdir(parents=True, exist_ok=True)
            stream = archive.extractfile(member)
            if stream is None:
                raise ValueError(f"Cannot read archive entry: {member.name!r}")
            with stream, dest.open("xb") as output:
                shutil.copyfileobj(stream, output)
            dest.chmod(0o755 if member.mode & 0o111 else 0o644)


def acquire(name: str, metadata: dict, target: Path, release_dir: Path | None) -> None:
    entry = metadata.get("archives", {}).get(name)
    if not entry:
        raise ValueError("This command has no release metadata; use --source with a checkout")
    filename = f"template-{name}.tar.gz"
    expected = entry.get("sha256", "")
    if not re.fullmatch(r"[0-9a-f]{64}", expected):
        raise ValueError("Release contains an invalid archive checksum")
    with tempfile.TemporaryDirectory(prefix="template-download-") as temporary:
        archive = Path(temporary) / filename
        if release_dir is not None:
            source = release_dir / filename
            if source.is_symlink() or source.stat().st_size > MAX_ARCHIVE_BYTES:
                raise ValueError("Invalid local release archive")
            shutil.copyfile(source, archive)
        else:
            version = metadata["version"]
            if not re.fullmatch(r"v[0-9]+\.[0-9]+\.[0-9]+(?:-[A-Za-z0-9.-]+)?", version):
                raise ValueError("Invalid release version")
            url = f"https://github.com/{REPOSITORY}/releases/download/{version}/{filename}"
            request = urllib.request.Request(url, headers={"User-Agent": "template-cli"})
            with urllib.request.urlopen(request, timeout=60) as response, archive.open("xb") as output:
                if not response.url.startswith("https://"):
                    raise ValueError("Refusing a non-HTTPS archive redirect")
                size = 0
                while chunk := response.read(1024 * 1024):
                    size += len(chunk)
                    if size > MAX_ARCHIVE_BYTES:
                        raise ValueError("Archive exceeds the download size limit")
                    output.write(chunk)
        digest = hashlib.sha256(archive.read_bytes()).hexdigest()
        if digest != expected:
            raise ValueError(f"Checksum mismatch for {filename}; nothing was generated")
        extract_archive(archive, target)


def seed_environments(target: Path) -> None:
    for example in sorted(target.rglob(".env.example")):
        if "examples" in example.relative_to(target).parts:
            continue
        names = [".env"]
        if (example.parent / "dev.compose.yml").exists():
            names.append(".env.development")
        for name in names:
            dest = example.with_name(name)
            with dest.open("x", encoding="utf-8") as output:
                output.write(example.read_text())
            dest.chmod(0o600)
    ignore = target / ".gitignore"
    text = ignore.read_text() if ignore.exists() else "# ©AngelaMos | 2026\n# .gitignore\n"
    required = [".env", ".env.*", "!.env.example", "!.env.*.example", "*.pem", "*.key"]
    additions = [line for line in required if line not in text.splitlines()]
    if additions:
        ignore.write_text(text.rstrip() + "\n" + "\n".join(additions) + "\n")


def local_identity(source: Path) -> dict:
    revision = subprocess.run(
        ["git", "-C", str(source), "rev-parse", "HEAD"],
        check=True, text=True, capture_output=True,
    ).stdout.strip()
    status = subprocess.run(
        ["git", "-C", str(source), "status", "--porcelain"],
        check=True, text=True, capture_output=True,
    ).stdout
    return {"version": "development", "revision": revision, "dirty": bool(status)}


def install_dependencies(target: Path) -> None:
    roots = [target, target / "backend", target / "go-backend", target / "frontend", target / "react-scss"]
    for root in roots:
        if (root / "go.mod").exists():
            subprocess.run(["go", "mod", "download"], cwd=root, check=True)
        if (root / "pyproject.toml").exists():
            subprocess.run(["uv", "sync", "--locked", "--extra", "dev"], cwd=root, check=True)
        if (root / "package.json").exists():
            subprocess.run(["pnpm", "install", "--frozen-lockfile"], cwd=root, check=True)


def configure_api(target: Path, name: str, api_url: str | None) -> None:
    if api_url is None:
        return
    if name not in {"frontend", "native"}:
        raise ValueError("--api-url is for the standalone frontend and native clients")
    url = urlsplit(api_url)
    if (url.scheme not in {"http", "https"} or not url.hostname
            or url.username or url.password or url.query or url.fragment
            or any(character in api_url for character in '\r\n\"\'`$ {}')):
        raise ValueError("--api-url must be an HTTP(S) URL without credentials, query, or fragment")
    key = "EXPO_PUBLIC_API_URL" if name == "native" else "API_PROXY_TARGET"
    for env in (target / ".env", target / ".env.development"):
        lines = env.read_text().splitlines()
        env.write_text("\n".join(f"{key}={api_url.rstrip('/')}" if line.startswith(f"{key}=") else line for line in lines) + "\n")


def generate(args: argparse.Namespace, metadata: dict) -> Path:
    name, entry = resolve(args.type)
    raw_name = Path.cwd().name if args.name in {None, "."} else args.name
    if "/" in raw_name or "\\" in raw_name:
        raise ValueError("Project name must be a name, not a path")
    slug = re.sub(r"[^a-z0-9]+", "-", raw_name.lower()).strip("-")
    if not slug or len(slug) > 63 or not slug[0].isalpha():
        raise ValueError("Project name must start with a letter and contain at most 63 characters")
    if not re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?", args.owner):
        raise ValueError("Owner must be a valid GitHub account name")
    target = Path.cwd() if args.name in {None, "."} else Path.cwd() / slug
    existing = target.exists()
    if target.is_symlink() or (existing and not target.is_dir()):
        raise ValueError(f"Destination is not a regular directory: {target}")
    if existing and any(path.name != ".git" for path in target.iterdir()):
        raise ValueError(f"Destination is not empty: {target}")
    if existing and (target / ".git").is_symlink():
        raise ValueError("Refusing a symlinked .git directory")
    source = args.source
    if source is None and metadata["version"] == "development":
        source = Path(__file__).resolve().parent.parent
    if source is not None:
        source = source.resolve()
        if target == source or source in target.parents:
            raise ValueError("Generate outside the template source checkout")
        metadata = local_identity(source)
    if not args.no_git and shutil.which("git") is None:
        raise ValueError("git is required unless --no-git is used")
    with tempfile.TemporaryDirectory(prefix=".template-", dir=target.parent) as temporary:
        staged = Path(temporary) / "project"
        staged.mkdir()
        if source is not None:
            copy_source(source / entry.path, staged)
            if not (staged / "LICENSE").exists():
                shutil.copyfile(source / "LICENSE", staged / "LICENSE")
        else:
            acquire(name, metadata, staged, args.release_dir)
        seed_environments(staged)
        ports = Ports()
        title = slug.replace("-", " ").title()
        literals = build_replacements(slug, title, args.owner, entry.namespace)
        for path in sorted(staged.rglob("*")):
            if path.is_file() and is_text(path):
                rewrite_file(path, slug, title, literals, ports)
        configure_api(staged, name, getattr(args, "api_url", None))
        provenance = {
            "template": name, "version": metadata["version"],
            "source_revision": metadata["revision"], "source_dirty": metadata["dirty"],
            "source": str(source) if source is not None else REPOSITORY,
            "host_ports_probed": ports.availability_checked,
        }
        (staged / ".template.json").write_text(json.dumps(provenance, indent=2) + "\n")
        if not args.no_git and not (target / ".git").exists():
            subprocess.run(["git", "init", "-q", str(staged)], check=True)
        if not existing:
            target.mkdir()
        elif any(path.name != ".git" for path in target.iterdir()):
            raise ValueError("Destination changed during generation; refusing to overwrite it")
        for path in staged.iterdir():
            dest = target / path.name
            if dest.exists() or dest.is_symlink():
                raise ValueError(f"Refusing to overwrite: {dest}")
            path.rename(dest)
    print(f"Generated {name} in {target}")
    print(f"Source: {metadata['version']} ({metadata['revision'] or 'unknown revision'})")
    if name == "native":
        print("Native is experimental: Docker, binary, and device validation are deferred.", file=sys.stderr)
    if args.install:
        try:
            install_dependencies(target)
        except (OSError, subprocess.CalledProcessError) as exc:
            raise ValueError(f"Project retained at {target}; dependency installation failed: {exc}") from exc
    if (target / "justfile").exists() or (target / "Justfile").exists():
        print("Next: enter the project directory and run just to see its commands.")
    else:
        print("Next: enter the project directory and review its package.json commands.")
    return target


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a project from a local checkout or a pinned public release.")
    parser.add_argument("type", nargs="?", help="Template name, list, or info")
    parser.add_argument("name", nargs="?", help="New directory name; omit to use an empty current directory")
    parser.add_argument("--owner", default="CarterPerez-dev")
    parser.add_argument("--source", type=Path, help="Use this local template checkout")
    parser.add_argument("--release-dir", type=Path, help="Use locally downloaded release archives with embedded checksum verification")
    parser.add_argument("--no-git", action="store_true")
    parser.add_argument("--install", action="store_true", help="Install locked dependencies after generation")
    parser.add_argument("--api-url", help="Connect a standalone frontend or native client to a FastAPI backend")
    parser.add_argument("--version", action="store_true")
    args = parser.parse_args()
    try:
        metadata = release_metadata()
        if args.version:
            print(f"template {metadata['version']}")
        elif args.type == "list":
            for name, entry in CATALOG.items():
                status = " (experimental)" if name == "native" else ""
                print(f"{name:16} {entry.path}{status}")
        elif args.type == "info":
            print(json.dumps(metadata, indent=2))
        elif args.type is None:
            parser.print_help()
        else:
            generate(args, metadata)
    except (ValueError, RuntimeError, OSError, subprocess.CalledProcessError, tarfile.TarError, zipfile.BadZipFile) as exc:
        print(f"template: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
