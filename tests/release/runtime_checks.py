"""
©AngelaMos | 2026
runtime_checks.py
"""

import errno
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import tempfile
from typing import TextIO
from uuid import uuid4

from resolve_dependencies import ROOT, cancel_process


def require_space(workspace: Path) -> None:
    if shutil.disk_usage(workspace).free < 2 * 1024 ** 3:
        raise RuntimeError(f"Verification needs at least 2 GiB free at {workspace}; choose another disk with TEMPLATE_CHECK_ROOT")


def create_workspace(prefix: str) -> Path:
    parent = Path(os.environ.get("TEMPLATE_CHECK_ROOT") or ROOT.parent / ".template-checks").expanduser().resolve()
    if parent == ROOT or ROOT in parent.parents:
        raise ValueError("TEMPLATE_CHECK_ROOT must be outside the template source checkout")
    parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    require_space(parent)
    return Path(tempfile.mkdtemp(prefix=prefix, dir=parent))


def write_report(path: Path, report: dict) -> None:
    temporary = path.with_name(f".{path.name}.{uuid4().hex}.tmp")
    try:
        with temporary.open("x") as stream:
            json.dump(report, stream, indent=2)
            stream.write("\n")
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def environment(env_file: Path | None = None, *, workspace: Path | None = None) -> dict[str, str]:
    values = os.environ.copy()
    for name in ("FORCE_COLOR", "COMPOSE_PROJECT_NAME", "COMPOSE_FILE", "COMPOSE_PROFILES", "COMPOSE_ENV_FILES"):
        values.pop(name, None)
    if env_file is not None:
        for line in env_file.read_text().splitlines():
            key, separator, _value = line.strip().removeprefix("export ").partition("=")
            if separator and re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", key.strip()):
                values.pop(key.strip(), None)
    values.update(CI="true", NO_COLOR="1", COMPOSE_ANSI="never", BUILDKIT_PROGRESS="plain")
    if workspace is not None:
        temporary = workspace / "tmp"
        temporary.mkdir(exist_ok=True)
        values["TMPDIR"] = str(temporary)
    return values


def require_docker() -> None:
    try:
        subprocess.run(
            ["docker", "info", "--format", "{{.ServerVersion}}"],
            capture_output=True, text=True, check=True, timeout=15,
        )
    except subprocess.CalledProcessError as error:
        raise RuntimeError(f"Docker access is required; no cases started. {error.stderr.strip()}") from None
    except (OSError, subprocess.TimeoutExpired) as error:
        raise RuntimeError(f"Docker access is required; no cases started. {error}") from None


def run(command: list[str] | tuple[str, ...], target: Path, values: dict[str, str], log: TextIO, *, timeout: int = 900) -> None:
    display = shlex.join(command)
    print(display, flush=True)
    log.write(display + "\n")
    log.flush()
    with subprocess.Popen(
        command, cwd=target, env=values, text=True, stdout=log,
        stderr=subprocess.STDOUT, start_new_session=os.name == "posix",
    ) as process:
        try:
            code = process.wait(timeout=timeout)
        except (KeyboardInterrupt, subprocess.TimeoutExpired):
            cancel_process(process)
            raise
    if code:
        raise RuntimeError(f"Exit {code}: {display}")


def cleanup(compose: list[str], target: Path, values: dict[str, str], log: TextIO) -> list[str]:
    errors = []
    for command in (
        [*compose, "logs", "--no-color", "--tail", "200"],
        [*compose, "down", "--volumes", "--remove-orphans"],
    ):
        try:
            run(command, target, values, log, timeout=120)
        except (KeyboardInterrupt, OSError, RuntimeError, subprocess.SubprocessError) as error:
            errors.append(str(error) or "Cleanup interrupted")
            try:
                log.write(f"Cleanup error: {error}\n")
                log.flush()
            except OSError:
                pass
            if isinstance(error, OSError) and error.errno in {errno.ENOSPC, errno.EDQUOT, errno.EFBIG}:
                try:
                    with open(os.devnull, "w") as fallback:
                        run(command, target, values, fallback, timeout=120)
                except (KeyboardInterrupt, OSError, RuntimeError, subprocess.SubprocessError) as retry_error:
                    errors.append(str(retry_error) or "Cleanup interrupted")
    return errors
