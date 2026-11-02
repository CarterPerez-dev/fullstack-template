"""
©AngelaMos | 2026
release.py
"""

import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess
import tarfile
import zipfile

from catalog import CATALOG, source_files


def build(root: Path, output: Path, version: str, allow_dirty: bool = False) -> dict:
    if not re.fullmatch(r"v[0-9]+\.[0-9]+\.[0-9]+(?:-[A-Za-z0-9.-]+)?", version):
        raise ValueError("Version must be a tag such as v0.1.0 or v0.1.0-rc.1")
    revision = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"], check=True, capture_output=True, text=True).stdout.strip()
    status = subprocess.run(["git", "-C", str(root), "status", "--porcelain"], check=True, capture_output=True, text=True).stdout
    if status and not allow_dirty:
        raise ValueError("Release builds require a clean checkout; --allow-dirty is for local verification only")
    output = output.resolve()
    if output == root or root in output.parents:
        raise ValueError("Write release assets outside the source checkout")
    if output.exists():
        raise ValueError("Release output directory already exists; choose a fresh directory")
    output.mkdir(parents=True)
    metadata = {"version": version, "revision": revision, "dirty": bool(status), "archives": {}}
    for name, entry in CATALOG.items():
        source = root / entry.path
        if not source.is_dir():
            raise ValueError(f"Missing template: {entry.path}")
        dest = output / f"template-{name}.tar.gz"
        with dest.open("xb") as raw, gzip.GzipFile(fileobj=raw, mode="wb", filename="", mtime=0) as compressed, tarfile.open(fileobj=compressed, mode="w") as archive:
            for path in source_files(source):
                data = path.read_bytes()
                info = tarfile.TarInfo(path.relative_to(source).as_posix())
                info.size = len(data)
                info.mode = 0o755 if path.stat().st_mode & 0o111 else 0o644
                archive.addfile(info, io.BytesIO(data))
            if not (source / "LICENSE").exists():
                data = (root / "LICENSE").read_bytes()
                info = tarfile.TarInfo("LICENSE")
                info.size = len(data)
                info.mode = 0o644
                archive.addfile(info, io.BytesIO(data))
        metadata["archives"][name] = {"sha256": hashlib.sha256(dest.read_bytes()).hexdigest(), "bytes": dest.stat().st_size}
    executable = output / "template.pyz"
    executable.write_bytes(b"#!/usr/bin/env python3\n")
    with zipfile.ZipFile(executable, "a", compression=zipfile.ZIP_DEFLATED) as archive:
        contents = {
            "__main__.py": b'# Copyright AngelaMos | 2026\n# __main__.py\nfrom cli import main\nraise SystemExit(main())\n',
            "release.json": (json.dumps(metadata, sort_keys=True) + "\n").encode(),
        }
        for name in ("cli.py", "catalog.py", "rewrite.py"):
            contents[name] = (root / "template-tool" / name).read_bytes()
        for name, data in sorted(contents.items()):
            info = zipfile.ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, data)
    executable.chmod(0o755)
    (output / "release.json").write_text(json.dumps(metadata, indent=2) + "\n")
    for name in ("install.sh", "uninstall.sh"):
        path = root / name
        if path.exists():
            (output / name).write_bytes(path.read_bytes())
            (output / name).chmod(0o755)
    checksums = [f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}" for path in sorted(output.iterdir())]
    (output / "checksums.txt").write_text("\n".join(checksums) + "\n")
    return metadata


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the CLI and one checked archive for each template")
    parser.add_argument("--version", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--allow-dirty", action="store_true")
    args = parser.parse_args()
    try:
        metadata = build(Path(__file__).resolve().parent.parent, args.output, args.version, args.allow_dirty)
    except (ValueError, OSError, subprocess.CalledProcessError) as exc:
        parser.exit(1, f"release: {exc}\n")
    print(f"Built {len(metadata['archives'])} templates at {args.output}")
    if metadata["dirty"]:
        print("Development artifacts only: source checkout has uncommitted changes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
