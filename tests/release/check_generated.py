"""
©AngelaMos | 2026
check_generated.py
"""

import argparse
import json
from pathlib import Path
import subprocess
import sys
import time
from urllib.error import URLError
from urllib.request import urlopen
from uuid import uuid4

from runtime_checks import cleanup, create_workspace, environment, require_docker, require_space, run, write_report


ROOT = Path(__file__).resolve().parents[2]
VARIANTS = (
    "go", "fastapi", "open", "frontend", "native",
    "fastapi-stack", "go-stack", "portfolio",
)


def request(url: str) -> bytes:
    with urlopen(url, timeout=10) as response:
        if response.status != 200:
            raise RuntimeError(f"Unexpected HTTP status {response.status}")
        return response.read(2 * 1024 * 1024)


def wait_for(url: str) -> bytes:
    deadline = time.monotonic() + 90
    while True:
        try:
            return request(url)
        except (URLError, TimeoutError, ConnectionError):
            if time.monotonic() >= deadline:
                raise RuntimeError(f"Timed out waiting for {url}") from None
            time.sleep(1)


def address(config: dict, service: str) -> str:
    port = config["services"][service]["ports"][0]["published"]
    return f"http://127.0.0.1:{port}"


def check_endpoints(variant: str, config: dict) -> None:
    if variant == "native":
        body = wait_for(address(config, "metro") + "/status")
        if b"packager-status:running" not in body:
            raise RuntimeError("Metro did not report a running packager")
        return
    if variant in {"go", "go-stack"}:
        wait_for(address(config, "api") + "/readyz")
    if variant in {"fastapi", "fastapi-stack", "portfolio"}:
        service = "api" if variant == "fastapi" else "backend"
        body = json.loads(wait_for(address(config, service) + "/health/detailed"))
        if body.get("database") != "healthy" or body.get("redis") != "healthy":
            raise RuntimeError("The generated API could not reach PostgreSQL and Redis")
    if variant in {"open", "frontend", "fastapi-stack", "go-stack", "portfolio"}:
        service = "frontend" if variant in {"frontend", "go-stack"} else "nginx"
        base = address(config, service)
        if b'id="root"' not in wait_for(base + "/"):
            raise RuntimeError("The generated frontend did not return its application document")
        if variant in {"fastapi-stack", "go-stack", "portfolio"}:
            route = "/readyz" if variant == "go-stack" else "/health/detailed"
            wait_for(base + "/api" + route)


def validate_namespace(config: dict, name: str, dev: bool) -> None:
    expected = name + "-dev" if dev else name
    if config.get("name") != expected:
        raise RuntimeError("Generated project has an unexpected Docker namespace")
    for service in config.get("services", {}).values():
        if "container_name" in service and not service["container_name"].startswith(name + "-"):
            raise RuntimeError("Generated container name is outside the disposable namespace")
    for kind in ("volumes", "networks"):
        for resource in config.get(kind, {}).values():
            if resource.get("external") or not resource.get("name", "").startswith(expected + "_"):
                raise RuntimeError(f"Generated {kind} must belong to the disposable project")


def check_variant(variant: str, environment_name: str, workspace: Path) -> dict:
    if variant == "native" and environment_name == "production":
        raise ValueError("Native production bundles are verified by the Expo export job")
    parent = workspace / "projects"
    name = f"verify-{variant}-{uuid4().hex[:10]}"
    target = parent / name
    log_path = workspace / "logs" / f"{variant}-{environment_name}.log"
    result = {
        "variant": variant, "environment": environment_name, "status": "running",
        "project": str(target), "log": str(log_path),
    }
    values = environment(workspace=workspace)
    owned_compose = None
    with log_path.open("x") as log:
        try:
            run(
                [sys.executable, "-B", str(ROOT / "template-tool/cli.py"),
                 variant, name, "--source", str(ROOT), "--no-git"],
                parent, values, log, timeout=120,
            )
            dev = environment_name == "development"
            env_file = ".env.development" if dev else ".env"
            values = environment(target / env_file, workspace=workspace)
            compose = [
                "docker", "compose", "--env-file", env_file,
                "-f", "dev.compose.yml" if dev else "compose.yml",
            ]
            rendered = subprocess.run(
                [*compose, "config", "--format", "json"], cwd=target, env=values,
                capture_output=True, text=True, timeout=30,
            )
            log.write(rendered.stderr)
            log.flush()
            if rendered.returncode:
                raise RuntimeError(f"Compose configuration failed with exit {rendered.returncode}")
            config = json.loads(rendered.stdout)
            (workspace / f"{variant}-{environment_name}.compose.json").write_text(rendered.stdout)
            validate_namespace(config, name, dev)
            owned_compose = [*compose, "--project-name", config["name"]]
            result["project_name"] = config["name"]
            run([*owned_compose, "build", "--pull"], target, values, log, timeout=1800)
            run(
                [*owned_compose, "up", "--wait", "--wait-timeout", "180"],
                target, values, log, timeout=240,
            )
            check_endpoints(variant, config)
            result["status"] = "passed"
        except KeyboardInterrupt:
            result["status"] = "cancelled"
            raise
        except (RuntimeError, ValueError, OSError, subprocess.SubprocessError) as error:
            result.update(status="failed", error=str(error))
            print(f"FAILED: {variant} ({environment_name}): {error}", flush=True)
            try:
                log.write(f"FAILED: {error}\n")
            except OSError:
                pass
        finally:
            if owned_compose is not None:
                errors = cleanup(owned_compose, target, values, log)
                if errors:
                    result.update(status="failed", cleanup_errors=errors)
            write_report(workspace / f"{variant}-{environment_name}.json", result)
    print(f"{result['status'].upper()}: {variant} ({environment_name})", flush=True)
    if result["status"] != "passed":
        print(f"  Log: {log_path}", flush=True)
    return result


def resume_cases(cases: list[tuple[str, str]], path: Path) -> tuple[list[tuple[str, str]], list[dict]]:
    report = json.loads(path.read_text())
    if not isinstance(report, dict) or not isinstance(report.get("results"), list) or not isinstance(report.get("retained_passes", []), list):
        raise ValueError("Resume requires a generated runtime report with a results list")
    recorded = {}
    for result in [*report.get("retained_passes", []), *report["results"]]:
        if (not isinstance(result, dict) or result.get("variant") not in VARIANTS
                or result.get("environment") not in {"development", "production"}
                or result.get("status") not in {"passed", "failed", "cancelled", "running"}):
            raise ValueError("Resume report contains an invalid runtime case")
        recorded[result["variant"], result["environment"]] = result
    passed = [recorded[case] for case in cases if recorded.get(case, {}).get("status") == "passed"]
    pending = [case for case in cases if recorded.get(case, {}).get("status") != "passed"]
    return pending, passed


def main() -> None:
    parser = argparse.ArgumentParser(description="Build and start an isolated generated Docker project")
    parser.add_argument("variant", choices=(*VARIANTS, "all"))
    parser.add_argument("environment", choices=("development", "production", "all"))
    parser.add_argument("--resume", type=Path, help="Skip cases recorded as passed in this earlier runtime report")
    parser.add_argument("--plan", action="store_true", help="List selected cases without starting Docker or creating projects")
    args = parser.parse_args()
    variants = VARIANTS if args.variant == "all" else (args.variant,)
    environments = ("development", "production") if args.environment == "all" else (args.environment,)
    cases = [
        (variant, environment)
        for variant in variants for environment in environments
        if (variant, environment) != ("native", "production")
    ]
    if not cases:
        parser.error("Native production bundles are verified by the Expo export job")
    retained = []
    if args.resume:
        args.resume = args.resume.resolve()
        cases, retained = resume_cases(cases, args.resume)
        print(f"Retaining {len(retained)} prior passes from {args.resume}; {len(cases)} cases remain.", flush=True)
    if args.plan or not cases:
        for variant, environment_name in cases:
            print(f"{variant} ({environment_name})")
        return
    require_docker()
    workspace = create_workspace("template-runtime-check-")
    (workspace / "projects").mkdir()
    (workspace / "logs").mkdir()
    report = {"status": "running", "results": [], "retained_passes": retained}
    if args.resume:
        report["previous_report"] = str(args.resume)
    report_path = workspace / "report.json"
    print(f"Retained projects, logs, and report: {workspace}", flush=True)
    print("Only each generated project's containers and volumes are removed after its checks.")
    try:
        for variant, environment_name in cases:
            require_space(workspace)
            print(f"Checking generated {variant} ({environment_name})", flush=True)
            result = check_variant(variant, environment_name, workspace)
            report["results"].append(result)
            write_report(report_path, report)
        report["status"] = "failed" if any(result["status"] != "passed" for result in report["results"]) else "passed"
    except KeyboardInterrupt:
        report["status"] = "cancelled"
        raise
    except (OSError, RuntimeError, ValueError) as error:
        report.update(status="failed", error=str(error))
        raise
    finally:
        write_report(report_path, report)
    failures = [result for result in report["results"] if result["status"] != "passed"]
    if failures:
        raise RuntimeError(f"Failed {len(failures)}/{len(cases)} generated runtime cases; see {report_path}")
    print(f"Passed all {len(cases)} selected generated runtime cases; {len(retained)} prior passes referenced. Report: {report_path}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Runtime checks cancelled; projects, logs, and case results were retained.", file=sys.stderr)
        raise SystemExit(130) from None
    except (OSError, RuntimeError, ValueError) as error:
        print(f"Runtime checks stopped: {error}", file=sys.stderr)
        raise SystemExit(1) from None
