"""
©AngelaMos | 2026
check_dependencies.py
"""

import argparse
import hashlib
from importlib import import_module
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys

from resolve_dependencies import GO_VERSION, PNPM_VERSION, PROJECTS, ROOT, UV_VERSION, cancel_process
from runtime_checks import create_workspace, environment as runtime_environment, write_report


sys.path.insert(0, str(ROOT / "template-tool"))
copy_source = import_module("cli").copy_source
LOCK_INPUTS = ("pyproject.toml", "uv.lock", "package.json", "pnpm-lock.yaml", "go.mod", "go.sum")


def commands(group: str, project: str, target: Path, fixtures: Path, offline: bool) -> list[tuple[str, ...]]:
    uv = ("uvx", *(("--offline",) if offline else ()), "--from", f"uv=={UV_VERSION}", "uv")
    if group == "python":
        run = (*uv, "run", "--no-sync")
        steps = [
            (*uv, "sync", "--locked", "--all-extras", "--python", "3.12", *(("--offline",) if offline else ())),
            (*run, "python", "--version"),
            (*run, "ruff", "check", "app"),
        ]
        if "examples/" not in project:
            steps.extend([
                (*run, "pylint", "--jobs=1", "app"),
                (*run, "mypy", "app"),
            ])
        steps.append((*run, "pytest", f"--confcutdir={fixtures}", str(fixtures / "test_python_lifecycle.py"), "-v"))
        if not offline:
            requirements = str(target / "audit-requirements.txt")
            steps.extend([
                (*uv, "export", "--quiet", "--locked", "--no-dev", "--no-emit-project", "--format", "requirements-txt", "--output-file", requirements),
                ("uvx", "--from", "pip-audit==2.10.1", "pip-audit", "--no-deps", "--disable-pip", "--require-hashes", "-r", requirements),
            ])
        return steps
    if group == "go":
        steps = [
            ("go", "version"),
            ("go", "mod", "download"),
            ("go", "mod", "verify"),
            ("go", "vet", "./..."),
            ("go", "test", "-race", "-count=1", "-v", "./..."),
            ("go", "build", "-o", "api-check", "./cmd/api"),
        ]
        if not offline:
            steps.append(("go", "run", "golang.org/x/vuln/cmd/govulncheck@v1.9.0", "-show", "verbose", "./..."))
        return steps
    steps = [
        ("node", "--version"),
        ("pnpm", "install", "--frozen-lockfile", "--strict-peer-dependencies", "--reporter=append-only", *(("--offline",) if offline else ())),
    ]
    if group == "native":
        steps.append(("pnpm", "exec", "expo", "install", "--check"))
        steps.append(("pnpm", "check"))
    else:
        steps.extend([("pnpm", "lint"), ("pnpm", "lint:scss"), ("pnpm", "build")])
    if project != "frontends/open/react-scss":
        steps.append(("node", "--experimental-vm-modules", str(fixtures / "test_client_refresh.mjs"), str(target)))
    if group == "native":
        steps.extend([
            ("node", "--experimental-vm-modules", str(fixtures / "test_native_storage.mjs"), str(target)),
            ("node", str(fixtures / "test_native_glob.mjs"), str(target)),
            ("pnpm", "exec", "expo", "export", "--platform", "ios", "--output-dir", "native-export"),
            ("pnpm", "exec", "expo", "export", "--platform", "android", "--output-dir", "native-export-android"),
        ])
    if not offline:
        steps.append(("pnpm", "audit", "--prod", "--json"))
    return steps


def fingerprints(target: Path) -> dict[str, str]:
    paths = [target / name for name in LOCK_INPUTS]
    paths.extend(sorted((target / "patches").rglob("*.patch")))
    return {
        path.relative_to(target).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in paths if path.is_file()
    }


def environment_for(group: str, target: Path, workspace: Path, offline: bool) -> dict[str, str]:
    environment = runtime_environment(workspace=workspace)
    for name in ("FORCE_COLOR", "TEST_POSTGRES_URL", "TEMPLATE_TEST_DEPENDENCIES", "VIRTUAL_ENV", "PYTHONHOME"):
        environment.pop(name, None)
    environment.update({
        "CI": "true",
        "NO_COLOR": "1",
        "COREPACK_ENABLE_DOWNLOAD_PROMPT": "0",
        "PYTHONNOUSERSITE": "1",
        "PYTHONDONTWRITEBYTECODE": "1",
        "UV_NO_PROGRESS": "1",
        "UV_PROJECT_ENVIRONMENT": str(target / ".venv"),
        "GOTOOLCHAIN": f"go{GO_VERSION}",
        "GOCACHE": str(workspace / "go-build-cache"),
        "GOWORK": "off",
        "GOFLAGS": "-mod=readonly",
        "EXPO_NO_TELEMETRY": "1",
        "EXPO_PUBLIC_API_URL": "https://api.example.com/api",
    })
    if group == "python":
        environment.update({
            "PYTHONPATH": str(target / "app"),
            "DATABASE_URL": "postgresql+asyncpg://template_test:disposable-fixture-password@127.0.0.1:45432/templates_test",
            "SECRET_KEY": "disposable-check-fixture-secret-not-for-deployment",
            "ENVIRONMENT": "development",
        })
    if offline:
        environment.update({"UV_OFFLINE": "1", "GOPROXY": "off", "EXPO_OFFLINE": "1", "COREPACK_ENABLE_NETWORK": "0"})
    return environment


def run(command: tuple[str, ...], target: Path, environment: dict[str, str], log, *, verbose: bool = False) -> None:
    display = shlex.join(command)
    print(display, flush=True)
    log.write(display + "\n")
    log.flush()
    with subprocess.Popen(
        command, cwd=target, env=environment, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        start_new_session=os.name == "posix",
    ) as process:
        if process.stdout is None:
            raise RuntimeError("Check process did not expose its output")
        try:
            for line in process.stdout:
                log.write(line)
                log.flush()
                if verbose:
                    print(line, end="", flush=True)
            return_code = process.wait()
        except KeyboardInterrupt:
            cancel_process(process)
            raise
        if return_code:
            raise RuntimeError(f"Exit {return_code}: {display}")


def check_project(group: str, project: str, workspace: Path, offline: bool, *, verbose: bool = False) -> dict:
    target = workspace / "projects" / project
    copy_source(ROOT / project, target)
    before = fingerprints(target)
    environment = environment_for(group, target, workspace, offline)
    log_path = workspace / "logs" / (project.replace("/", "__") + ".log")
    result = {"group": group, "project": project, "status": "running", "log": str(log_path), "inputs": before}
    with log_path.open("x") as log:
        try:
            if group in {"web", "native"}:
                version = subprocess.check_output(["pnpm", "--version"], cwd=target, env=environment, text=True).strip()
                if version != PNPM_VERSION:
                    raise RuntimeError(f"Expected pnpm {PNPM_VERSION}, got {version}")
            for command in commands(group, project, target, workspace / "fixtures", offline):
                run(command, target, environment, log, verbose=verbose)
            result["status"] = "passed"
        except (OSError, RuntimeError, subprocess.SubprocessError) as error:
            result.update(status="failed", error=str(error))
            log.write(f"FAILED: {error}\n")
        finally:
            if fingerprints(target) != before:
                result.update(status="failed", error="A manifest, lock, or dependency patch changed during locked verification")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Install locked dependencies in isolated copies and run local compatibility checks.")
    parser.add_argument("group", nargs="?", choices=("all", *PROJECTS), default="all")
    parser.add_argument("--offline", action="store_true", help="Use cached packages and skip registry-backed vulnerability audits")
    parser.add_argument("--plan", action="store_true", help="Print commands without copying or installing")
    parser.add_argument("--verbose", action="store_true", help="Also stream complete command output to the terminal")
    arguments = parser.parse_args()
    groups = tuple(PROJECTS) if arguments.group == "all" else (arguments.group,)
    if arguments.plan:
        for group in groups:
            for project in PROJECTS[group]:
                print(f"[{project}]")
                for command in commands(group, project, Path("<isolated-copy>") / project, Path("<fixtures>"), arguments.offline):
                    print(shlex.join(command))
        return
    required = {"python": ("uvx",), "web": ("pnpm", "node"), "native": ("pnpm", "node"), "go": ("go",)}
    for group in groups:
        for executable in required[group]:
            if shutil.which(executable) is None:
                raise RuntimeError(f"Required executable is missing: {executable}")

    workspace = create_workspace("template-dependency-check-")
    (workspace / "logs").mkdir()
    copy_source(ROOT / "tests/release", workspace / "fixtures")
    print(f"Retained projects, logs, and report: {workspace}", flush=True)
    print("Fresh installs and checks use isolated copies; source environments and lockfiles stay in place.")
    print("PostgreSQL, Docker startup, native binary builds, and browser/device checks remain separate.")
    print("Complete command output is saved in logs; use --verbose to stream it too.")
    if arguments.offline:
        print("Offline mode: vulnerability audits are not run.")
    report = {"offline": arguments.offline, "results": []}
    report_path = workspace / "report.json"
    try:
        for group in groups:
            for project in PROJECTS[group]:
                print(f"\nChecking {project}", flush=True)
                result = check_project(group, project, workspace, arguments.offline, verbose=arguments.verbose)
                report["results"].append(result)
                write_report(report_path, report)
                print(f"{result['status'].upper()}: {project}", flush=True)
                if result["status"] == "failed":
                    print(f"  {result['error']}\n  Log: {result['log']}", flush=True)
    except KeyboardInterrupt:
        report["cancelled"] = True
        write_report(report_path, report)
        print("Checks cancelled; completed results and logs were retained.", file=sys.stderr)
        raise SystemExit(130) from None
    failed = [result["project"] for result in report["results"] if result["status"] != "passed"]
    if failed:
        raise RuntimeError(f"Failed {len(failed)}/{len(report['results'])} projects: {', '.join(failed)}. See {report_path}")
    print(f"Passed local dependency checks for all {len(report['results'])} selected projects. Report: {report_path}")


if __name__ == "__main__":
    try:
        main()
    except (OSError, RuntimeError, ValueError) as error:
        print(f"Dependency checks stopped: {error}", file=sys.stderr)
        raise SystemExit(1) from None
