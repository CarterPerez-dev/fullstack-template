"""
©AngelaMos | 2026
check_generated.py
"""

import argparse
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time
from urllib.error import URLError
from urllib.request import urlopen
from uuid import uuid4


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


def check_variant(variant: str, environment: str) -> None:
    if variant == "native" and environment == "production":
        raise ValueError("Native production bundles are verified by the Expo export job")
    with tempfile.TemporaryDirectory(prefix="template-runtime-") as temporary:
        parent = Path(temporary)
        name = f"verify-{variant}-{uuid4().hex[:10]}"
        subprocess.run(
            [sys.executable, "-B", str(ROOT / "template-tool/cli.py"),
             variant, name, "--source", str(ROOT), "--no-git"],
            cwd=parent, check=True,
        )
        target = parent / name
        dev = environment == "development"
        compose = [
            "docker", "compose", "--env-file", ".env.development" if dev else ".env",
            "-f", "dev.compose.yml" if dev else "compose.yml",
        ]
        result = subprocess.run(
            [*compose, "config", "--format", "json"], cwd=target,
            capture_output=True, text=True, check=True,
        )
        config = json.loads(result.stdout)
        if config["name"] not in {name, name + "-dev"}:
            raise RuntimeError("Generated project has an unexpected Docker namespace")
        try:
            subprocess.run([*compose, "build"], cwd=target, check=True, timeout=1800)
            subprocess.run(
                [*compose, "up", "--wait", "--wait-timeout", "180"],
                cwd=target, check=True, timeout=240,
            )
            check_endpoints(variant, config)
            print(f"Verified generated {variant} ({environment})")
        finally:
            subprocess.run(
                [*compose, "down", "--volumes", "--remove-orphans"],
                cwd=target, check=True, timeout=120,
            )


def main() -> None:
    parser = argparse.ArgumentParser(description="Build and start an isolated generated Docker project")
    parser.add_argument("variant", choices=(*VARIANTS, "all"))
    parser.add_argument("environment", choices=("development", "production", "all"))
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
    try:
        subprocess.run(["docker", "info", "--format", "{{.ServerVersion}}"], check=True)
    except (OSError, subprocess.CalledProcessError):
        raise SystemExit("Docker access is required; no runtime cases were started") from None
    failures = []
    for variant, environment in cases:
        try:
            check_variant(variant, environment)
        except (RuntimeError, ValueError, OSError, subprocess.SubprocessError) as error:
            failures.append(f"{variant} ({environment})")
            print(f"FAILED {failures[-1]}: {error}", file=sys.stderr)
    if failures:
        raise SystemExit(f"Failed {len(failures)}/{len(cases)} cases: {', '.join(failures)}")
    print(f"Passed all {len(cases)} generated runtime cases")


if __name__ == "__main__":
    main()
