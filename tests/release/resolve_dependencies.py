"""
©AngelaMos | 2026
resolve_dependencies.py
"""

import argparse
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[2]
UV_VERSION = "0.13.6"
PNPM_VERSION = "10.34.9"
GO_VERSION = "1.26.10"
PROJECTS = {
    "python": (
        "backends/fastapi",
        "stacks/fastapi-react/backend",
        "stacks/portfolio/backend",
        "stacks/fastapi-react/examples/minimal-production/backend",
        "stacks/portfolio/examples/minimal-production/backend",
    ),
    "web": (
        "frontends/auth/react-scss",
        "frontends/open/react-scss",
        "stacks/fastapi-react/frontend",
        "stacks/go-react/frontend",
        "stacks/portfolio/frontend",
    ),
    "native": ("frontends/auth/react-native",),
    "go": ("backends/go-backend", "stacks/go-react/go-backend"),
}
GO_MODULES = (
    "go@" + GO_VERSION,
    "github.com/go-chi/chi/v5@v5.5.0",
    "github.com/go-playground/validator/v10@v10.30.5",
    "github.com/jackc/pgx/v5@v5.11.0",
    "github.com/lestrrat-go/jwx/v3@v3.4.0",
    "github.com/redis/go-redis/v9@v9.23.0",
    "go.opentelemetry.io/otel@v1.47.0",
    "go.opentelemetry.io/otel/sdk@v1.47.0",
    "go.opentelemetry.io/otel/trace@v1.47.0",
    "go.opentelemetry.io/otel/metric@v1.47.0",
    "go.opentelemetry.io/otel/exporters/otlp/otlptrace@v1.47.0",
    "go.opentelemetry.io/otel/exporters/otlp/otlptrace/otlptracegrpc@v1.47.0",
    "google.golang.org/grpc@v1.85.0",
    "golang.org/x/net@v0.62.0",
    "golang.org/x/crypto@v0.58.0",
)


def commands(group: str) -> tuple[tuple[str, ...], ...]:
    if group == "python":
        return (("uvx", "--from", f"uv=={UV_VERSION}", "uv", "lock",
                 "--upgrade", "--python", "3.12"),)
    if group == "go":
        return (
            ("go", "get", *GO_MODULES),
            ("go", "mod", "tidy"),
            ("go", "mod", "verify"),
        )
    return (("pnpm", "install", "--lockfile-only", "--no-frozen-lockfile"),)


def resolve(group: str, project: str, log_directory: Path) -> None:
    environment = os.environ.copy()
    if group == "go":
        environment["GOTOOLCHAIN"] = f"go{GO_VERSION}"
    directory = ROOT / project
    if group in {"web", "native"}:
        version = subprocess.check_output(
            ["pnpm", "--version"], cwd=directory, text=True, env=environment,
        ).strip()
        if version != PNPM_VERSION:
            raise RuntimeError(f"{project}: expected pnpm {PNPM_VERSION}, got {version}")

    with (log_directory / (project.replace("/", "__") + ".log")).open("x") as log:
        for command in commands(group):
            print(f"[{project}] {shlex.join(command)}", flush=True)
            log.write(shlex.join(command) + "\n")
            log.flush()
            with subprocess.Popen(
                command, cwd=directory, env=environment, text=True,
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            ) as process:
                if process.stdout is None:
                    raise RuntimeError("Dependency resolver did not expose its output")
                for line in process.stdout:
                    print(line, end="", flush=True)
                    log.write(line)
                    log.flush()
                if process.wait() != 0:
                    raise RuntimeError(f"{project}: resolver failed; see {log.name}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Resolve reviewed dependency candidates using real package managers.",
    )
    parser.add_argument("group", nargs="?", choices=("all", *PROJECTS), default="all")
    parser.add_argument("--plan", action="store_true", help="Print commands without running them")
    arguments = parser.parse_args()
    groups = tuple(PROJECTS) if arguments.group == "all" else (arguments.group,)
    if arguments.plan:
        for group in groups:
            for project in PROJECTS[group]:
                for command in commands(group):
                    prefix = f"GOTOOLCHAIN=go{GO_VERSION} " if group == "go" else ""
                    print(f"[{project}] {prefix}{shlex.join(command)}")
        return

    for group in groups:
        executable = commands(group)[0][0]
        if shutil.which(executable) is None:
            raise RuntimeError(f"Required executable is missing: {executable}")

    log_directory = Path(tempfile.mkdtemp(prefix="template-dependency-resolution-"))
    print(f"Resolution logs: {log_directory}", flush=True)
    for group in groups:
        for project in PROJECTS[group]:
            resolve(group, project, log_directory)

    print("Lock resolution completed. Review the manifest and lock diffs next.")
    print("Fresh installs, audits, native SDK migration, and runtime checks remain required.")


if __name__ == "__main__":
    try:
        main()
    except (OSError, RuntimeError, subprocess.CalledProcessError) as error:
        print(f"Dependency resolution stopped: {error}", file=sys.stderr)
        raise SystemExit(1) from error
