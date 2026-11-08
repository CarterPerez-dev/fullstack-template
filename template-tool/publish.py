"""
©AngelaMos | 2026
publish.py
"""

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys
import tempfile
import time
from urllib.request import Request, urlopen
import zipfile

from catalog import CATALOG


ROOT = Path(__file__).resolve().parent.parent
REPOSITORY = "CarterPerez-dev/Fullstack-setup"
WEBSITE_REPOSITORY = "AngelaMos-Inc/angelamos.com"
INSTALL_URL = "https://angelamos.com/template/install.sh"


def run(*command: str, cwd: Path | None = None, capture: bool = False, timeout: int = 120, env=None) -> str:
    print(shlex.join(command), flush=True)
    result = subprocess.run(command, cwd=cwd or ROOT, check=True, text=True,
                            stdout=subprocess.PIPE if capture else None, timeout=timeout, env=env)
    return result.stdout.strip() if capture else ""


def clean_checkout(root: Path, repository: str) -> tuple[str, str]:
    origin = run("git", "remote", "get-url", "--push", "origin", cwd=root, capture=True)
    accepted = {f"git@github.com:{repository}.git", f"https://github.com/{repository}.git", f"https://github.com/{repository}"}
    fetch = run("git", "remote", "get-url", "origin", cwd=root, capture=True)
    if origin not in accepted or fetch not in accepted:
        raise ValueError(f"Expected origin to be {repository}; no remote changed")
    if run("git", "status", "--porcelain", cwd=root, capture=True):
        raise ValueError(f"Commit the intended changes first: {root}")
    branch = run("git", "symbolic-ref", "--short", "HEAD", cwd=root, capture=True)
    revision = run("git", "rev-parse", "HEAD", cwd=root, capture=True)
    return branch, revision


def check_ancestor(root: Path, ref: str, revision: str) -> None:
    result = subprocess.run(["git", "merge-base", "--is-ancestor", ref, revision], cwd=root)
    if result.returncode:
        raise ValueError(f"{ref} is not an ancestor of {revision[:12]}; reconcile history before publishing")


def sync_release(version: str, branch: str, revision: str) -> None:
    repository = json.loads(run("gh", "repo", "view", REPOSITORY, "--json",
                                "nameWithOwner,isPrivate,defaultBranchRef", capture=True))
    if repository["nameWithOwner"].lower() != REPOSITORY.lower() or repository["isPrivate"]:
        raise ValueError("Publication requires the expected public repository")
    default = repository["defaultBranchRef"]["name"]
    run("git", "fetch", "--no-tags", "origin")
    for name in dict.fromkeys((default, branch)):
        ref = f"refs/remotes/origin/{name}"
        exists = subprocess.run(["git", "show-ref", "--verify", "--quiet", ref], cwd=ROOT).returncode == 0
        if exists:
            check_ancestor(ROOT, ref, revision)
        elif name == default:
            raise ValueError("The default branch was not fetched; check the origin fetch configuration")
    tag = f"refs/tags/{version}"
    remote = run("git", "ls-remote", "--tags", "origin", tag, tag + "^{}", capture=True)
    remote_refs = {line.split()[1]: line.split()[0] for line in remote.splitlines()}
    if remote and remote_refs.get(tag + "^{}", remote_refs[tag]) != revision:
        raise ValueError(f"Remote {version} belongs to another commit; choose a new version")
    if remote and not run("git", "tag", "--list", version, capture=True):
        run("git", "fetch", "--no-tags", "origin", f"{tag}:{tag}")
    if run("git", "tag", "--list", version, capture=True):
        if run("git", "rev-parse", tag + "^{commit}", capture=True) != revision:
            raise ValueError(f"Local {version} belongs to another commit; choose a new version")
        if remote and run("git", "rev-parse", tag, capture=True) != remote_refs[tag]:
            raise ValueError(f"Local and remote {version} tag objects differ; no tags overwritten")
    else:
        run("git", "tag", "-a", version, "-m", f"template {version}", revision)
    refs = [f"{revision}:refs/heads/{name}" for name in dict.fromkeys((branch, default))]
    run("git", "push", "--atomic", "origin", *refs, tag)


def wait_for_release(version: str, revision: str) -> None:
    for _ in range(24):
        runs = json.loads(run("gh", "run", "list", "--repo", REPOSITORY,
                              "--commit", revision, "--branch", version, "--event", "push",
                              "--json", "databaseId,url,workflowName", capture=True))
        runs = [item for item in runs if item["workflowName"] == "Publish template"]
        if runs:
            print(f"Release checks: {runs[0]['url']}", flush=True)
            run("gh", "run", "watch", str(runs[0]["databaseId"]), "--repo", REPOSITORY,
                "--exit-status", "--interval", "10", timeout=7200)
            return
        time.sleep(5)
    raise RuntimeError("No release workflow appeared. Check GitHub Actions settings and the pushed tag; no installer deployed")


def verify_assets(directory: Path, version: str, revision: str) -> None:
    expected_names = {f"template-{name}.tar.gz" for name in CATALOG}
    expected_names.update({"template.pyz", "release.json", "install.sh", "uninstall.sh"})
    sums = {}
    for line in (directory / "checksums.txt").read_text().splitlines():
        digest, name = line.split()
        if name not in expected_names or name in sums or not re.fullmatch(r"[a-f0-9]{64}", digest):
            raise ValueError("Unexpected or duplicated release checksum entry")
        sums[name] = digest
    if sums.keys() != expected_names:
        raise ValueError("The release is missing assets")
    for name, digest in sums.items():
        path = directory / name
        if path.is_symlink() or hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise ValueError(f"Release checksum mismatch: {name}")
    metadata = json.loads((directory / "release.json").read_text())
    if metadata.get("version") != version or metadata.get("revision") != revision or metadata.get("dirty") is not False:
        raise ValueError("The published release does not match the clean reviewed commit")
    with zipfile.ZipFile(directory / "template.pyz") as archive:
        if json.loads(archive.read("release.json")) != metadata:
            raise ValueError("CLI and release provenance disagree")
    if set(metadata["archives"]) != set(CATALOG):
        raise ValueError("Release catalog does not match the reviewed catalog")
    for name, details in metadata["archives"].items():
        path = directory / f"template-{name}.tar.gz"
        if details["sha256"] != sums[path.name] or details["bytes"] != path.stat().st_size:
            raise ValueError(f"CLI archive metadata does not match {name}")
    for name in ("install.sh", "uninstall.sh"):
        if (directory / name).read_bytes() != (ROOT / name).read_bytes():
            raise ValueError(f"Published {name} does not match the reviewed source")


def website_ready(root: Path) -> tuple[str, str]:
    identity = clean_checkout(root, WEBSITE_REPOSITORY)
    for name in ("install.sh", "uninstall.sh"):
        if (root / "frontend/public/template" / name).read_bytes() != (ROOT / name).read_bytes():
            raise ValueError(f"Website {name} does not match this release source")
    run("docker", "info", "--format", "{{.ServerVersion}}", cwd=root, timeout=15,
        env={**os.environ, "DOCKER_CONTEXT": "default"})
    return identity


def deploy_website(root: Path, identity: tuple[str, str]) -> None:
    if website_ready(root) != identity:
        raise ValueError("Website commit changed during publication; deployment stopped")
    branch, revision = identity
    run("git", "fetch", "--no-tags", "origin", cwd=root)
    check_ancestor(root, f"refs/remotes/origin/{branch}", revision)
    run("git", "push", "origin", f"{revision}:refs/heads/{branch}", cwd=root)
    env = {**os.environ, "DOCKER_CONTEXT": "default"}
    run("just", "installer-check", cwd=root)
    run("just", "build", "nginx", cwd=root, env=env, timeout=1800)
    run("just", "tunnel-start", "--no-deps", "--no-build", "nginx", cwd=root, env=env, timeout=120)


def verify_hosted_install(workspace: Path, version: str, revision: str) -> None:
    request = Request(INSTALL_URL, headers={"Cache-Control": "no-cache"})
    with urlopen(request, timeout=30) as response:
        installer = response.read(1024 * 1024)
    if installer != (ROOT / "install.sh").read_bytes():
        raise ValueError("The public installer bytes do not match the release; check deployment and CDN caching")
    path = workspace / "hosted-install.sh"
    path.write_bytes(installer)
    prefix = workspace / "bin"
    run("bash", str(path), "--version", version, "--prefix", str(prefix), "--no-modify-path", timeout=300)
    metadata = json.loads(run(str(prefix / "template"), "info", capture=True))
    if metadata.get("version") != version or metadata.get("revision") != revision or metadata.get("dirty") is not False:
        raise ValueError("Hosted installation provenance mismatch")
    for variant in ("fastapi-stack", "go-stack", "open"):
        run(str(prefix / "template"), variant, f"smoke-{variant}", "--no-git", cwd=workspace, timeout=180)
    run("bash", str(ROOT / "uninstall.sh"), "--prefix", str(prefix))


def main() -> None:
    parser = argparse.ArgumentParser(description="Publish the committed template release and optionally deploy its Angelamos installer")
    parser.add_argument("version")
    parser.add_argument("--website", default="", help="Clean Angelamos checkout; deploy only its nginx service")
    parser.add_argument("--plan", action="store_true", help="Describe the steps without network access or writes")
    args = parser.parse_args()
    if not re.fullmatch(r"v[0-9]+\.[0-9]+\.[0-9]+(?:-[A-Za-z0-9.-]+)?", args.version):
        parser.error("Use a release tag such as v0.1.0")
    if args.plan:
        print("Verify clean source and origin; fetch and fast-forward the current/default branches plus the version tag atomically.")
        print("Wait for GitHub web/backend CI and release publication; download and verify every release asset.")
        if args.website:
            print("Verify and push the clean Angelamos checkout; rebuild/recreate only nginx; verify hosted installation and three stack downloads.")
        print("Native validation stays deferred. Existing tags and releases are never overwritten.")
        return
    branch, revision = clean_checkout(ROOT, REPOSITORY)
    website = Path(args.website).expanduser().resolve() if args.website else None
    website_identity = website_ready(website) if website else None
    sync_release(args.version, branch, revision)
    wait_for_release(args.version, revision)
    parent = ROOT.parent / ".template-checks"
    parent.mkdir(exist_ok=True, mode=0o700)
    with tempfile.TemporaryDirectory(prefix="publication-", dir=parent) as temporary:
        workspace = Path(temporary)
        assets = workspace / "assets"
        run("gh", "release", "download", args.version, "--repo", REPOSITORY, "--dir", str(assets), timeout=300)
        verify_assets(assets, args.version, revision)
        if clean_checkout(ROOT, REPOSITORY) != (branch, revision):
            raise ValueError("Source commit changed during publication; deployment stopped")
        if website is not None:
            deploy_website(website, website_identity)
            verify_hosted_install(workspace, args.version, revision)
            print(f"Verified hosted installation: {INSTALL_URL}")
    print(f"Published and verified: https://github.com/{REPOSITORY}/releases/tag/{args.version}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Publication interrupted. Existing remote changes were preserved; inspect the release workflow before resuming.", file=sys.stderr)
        raise SystemExit(130) from None
    except (OSError, ValueError, RuntimeError, KeyError, subprocess.SubprocessError, zipfile.BadZipFile) as error:
        print(f"Publication stopped: {error}", file=sys.stderr)
        raise SystemExit(1) from None
