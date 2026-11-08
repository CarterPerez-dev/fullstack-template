"""
©AngelaMos | 2026
check_postgres.py
"""

import argparse
from importlib import import_module
import json
from pathlib import Path
import secrets
import shutil
import subprocess
import sys
from uuid import uuid4

from check_dependencies import ROOT, UV_VERSION, copy_source, environment_for, fingerprints
from runtime_checks import cleanup, create_workspace, environment, require_docker, run, write_report


Ports = import_module("rewrite").Ports
PROJECTS = {
    "python": ("backends/fastapi", "stacks/fastapi-react/backend", "stacks/portfolio/backend"),
    "go": ("backends/go-backend", "stacks/go-react/go-backend"),
}


def fixture_config(name: str, port: int, password: str) -> dict:
    return {
        "name": name,
        "services": {
            "postgres": {
                "image": "postgres:18-alpine",
                "environment": {
                    "POSTGRES_USER": "template_test", "POSTGRES_PASSWORD": password,
                    "POSTGRES_DB": "templates_test",
                },
                "ports": [{"target": 5432, "published": str(port), "host_ip": "127.0.0.1"}],
                "volumes": ["postgres_data:/var/lib/postgresql"],
                "healthcheck": {
                    "test": ["CMD-SHELL", "pg_isready -U template_test -d templates_test"],
                    "interval": "2s", "timeout": "5s", "retries": 30,
                },
            },
        },
        "volumes": {"postgres_data": {}},
    }


def commands(group: str, project: str, fixtures: Path) -> list[tuple[str, ...]]:
    if group == "go":
        return [
            ("go", "version"),
            ("go", "mod", "download"),
            ("go", "mod", "verify"),
            ("go", "test", "-race", "-count=1", "-timeout=10m", "-v", "./..."),
            ("go", "run", "golang.org/x/vuln/cmd/govulncheck@v1.9.0", "-show", "verbose", "./..."),
        ]
    uv = ("uvx", "--from", f"uv=={UV_VERSION}", "uv")
    execute = (*uv, "run", "--no-sync")
    cases = [str(fixtures / "test_python_security.py")]
    if project == "stacks/portfolio/backend":
        cases.extend(str(fixtures / name) for name in ("test_portfolio_integrity.py", "test_portfolio_media.py"))
    return [
        (*uv, "sync", "--locked", "--all-extras", "--python", "3.12"),
        (*execute, "python", "--version"),
        (*execute, "pytest", "-v"),
        (*execute, "pytest", f"--confcutdir={fixtures}", *cases, "-v"),
        (*execute, "alembic", "upgrade", "head"),
    ]


def check_project(group: str, project: str, workspace: Path, database_url: str) -> dict:
    target = workspace / "projects" / project
    copy_source(ROOT / project, target)
    before = fingerprints(target)
    values = environment_for(group, target, workspace, False)
    values["TEST_POSTGRES_URL"] = database_url
    if group == "python":
        values["DATABASE_URL"] = database_url
    log_path = workspace / "logs" / (project.replace("/", "__") + ".log")
    result = {"group": group, "project": project, "status": "running", "log": str(log_path), "inputs": before}
    print(f"Checking PostgreSQL: {project}", flush=True)
    with log_path.open("x") as log:
        try:
            for command in commands(group, project, workspace / "fixtures"):
                run(command, target, values, log)
            result["status"] = "passed"
        except KeyboardInterrupt:
            result["status"] = "cancelled"
            raise
        except (OSError, RuntimeError, subprocess.SubprocessError) as error:
            result.update(status="failed", error=str(error))
            log.write(f"FAILED: {error}\n")
        finally:
            if fingerprints(target) != before:
                result.update(status="failed", error="Dependency inputs changed during PostgreSQL verification")
            write_report(workspace / (project.replace("/", "__") + ".json"), result)
    print(f"{result['status'].upper()}: {project}", flush=True)
    if result["status"] != "passed":
        print(f"  {result['error']}\n  Log: {log_path}", flush=True)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Run backend tests against an isolated disposable PostgreSQL container")
    parser.add_argument("group", nargs="?", choices=("all", *PROJECTS), default="all")
    args = parser.parse_args()
    groups = tuple(PROJECTS) if args.group == "all" else (args.group,)
    for group in groups:
        executable = "uvx" if group == "python" else "go"
        if shutil.which(executable) is None:
            raise RuntimeError(f"Required executable is missing: {executable}")
    require_docker()
    workspace = create_workspace("template-postgres-check-")
    (workspace / "logs").mkdir()
    copy_source(ROOT / "tests/release", workspace / "fixtures")
    name = f"verify-postgres-{uuid4().hex[:12]}"
    port = Ports().get("postgres-check", "POSTGRES_HOST_PORT")
    password = secrets.token_hex(24)
    compose_file = workspace / "compose.json"
    compose_file.write_text(json.dumps(fixture_config(name, port, password), indent=2) + "\n")
    compose_file.chmod(0o600)
    compose = ["docker", "compose", "--project-name", name, "-f", str(compose_file)]
    report = {"project_name": name, "port": port, "status": "running", "results": []}
    report_path = workspace / "report.json"
    print(f"Retained projects, logs, and report: {workspace}", flush=True)
    print("Each backend gets a separate disposable database. Source environments stay in place.")
    values = environment(workspace=workspace)
    with (workspace / "logs/postgres.log").open("x") as log:
        try:
            run([*compose, "up", "--wait", "--wait-timeout", "90"], workspace, values, log, timeout=180)
            for group in groups:
                for project in PROJECTS[group]:
                    database = f"template_check_{len(report['results'])}"
                    run([*compose, "exec", "-T", "postgres", "createdb", "-U", "template_test", database], workspace, values, log, timeout=30)
                    scheme = "postgresql+asyncpg" if group == "python" else "postgres"
                    suffix = "" if group == "python" else "?sslmode=disable"
                    url = f"{scheme}://template_test:{password}@127.0.0.1:{port}/{database}{suffix}"
                    report["results"].append(check_project(group, project, workspace, url))
                    write_report(report_path, report)
            report["status"] = "failed" if any(result["status"] != "passed" for result in report["results"]) else "passed"
        except KeyboardInterrupt:
            report["status"] = "cancelled"
            raise
        except (OSError, RuntimeError, subprocess.SubprocessError) as error:
            report.update(status="failed", error=str(error))
        finally:
            errors = cleanup(compose, workspace, values, log)
            if errors:
                report.update(status="failed", cleanup_errors=errors)
            write_report(report_path, report)
    if report["status"] != "passed":
        raise RuntimeError(f"PostgreSQL checks failed; see {report_path}")
    print(f"Passed PostgreSQL checks for all {len(report['results'])} selected projects. Report: {report_path}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("PostgreSQL checks cancelled; logs and completed results were retained.", file=sys.stderr)
        raise SystemExit(130) from None
    except (OSError, RuntimeError, ValueError) as error:
        print(f"PostgreSQL checks stopped: {error}", file=sys.stderr)
        raise SystemExit(1) from None
