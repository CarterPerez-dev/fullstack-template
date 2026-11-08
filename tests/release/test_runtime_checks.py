"""
©AngelaMos | 2026
test_runtime_checks.py
"""

from contextlib import redirect_stdout
import errno
from importlib import import_module
from io import StringIO
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


sys.path.insert(0, str(Path(__file__).resolve().parent))
runtime = import_module("runtime_checks")
postgres = import_module("check_postgres")
generated = import_module("check_generated")


class RuntimeCheckTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)

    def test_failed_child_output_is_retained_without_terminal_flooding(self):
        log_path = self.root / "child.log"
        terminal = StringIO()
        command = [sys.executable, "-c", "import sys; print('fixture stdout'); print('fixture stderr', file=sys.stderr); sys.exit(7)"]
        with log_path.open("w") as log, redirect_stdout(terminal):
            with self.assertRaisesRegex(RuntimeError, "Exit 7"):
                runtime.run(command, self.root, runtime.environment(), log)
        output = log_path.read_text()
        self.assertIn("\nfixture stdout\n", output)
        self.assertIn("\nfixture stderr\n", output)
        self.assertNotIn("\nfixture stdout\n", terminal.getvalue())
        self.assertNotIn("\nfixture stderr\n", terminal.getvalue())

    @unittest.skipUnless(os.name == "posix", "POSIX process cancellation")
    def test_timeout_stops_the_active_child(self):
        command = [sys.executable, "-c", "import os, pathlib, time; pathlib.Path('pid').write_text(str(os.getpid())); time.sleep(30)"]
        with (self.root / "timeout.log").open("w") as log, redirect_stdout(StringIO()):
            with self.assertRaises(subprocess.TimeoutExpired):
                runtime.run(command, self.root, runtime.environment(), log, timeout=1)
        pid = int((self.root / "pid").read_text())
        with self.assertRaises(ProcessLookupError):
            os.kill(pid, 0)

    def test_cleanup_targets_owned_project_even_if_log_capture_fails(self):
        compose = ["docker", "compose", "--project-name", "verify-fixture-owned", "-f", "fixture.json"]
        for failure in (RuntimeError("logs failed"), KeyboardInterrupt()):
            with self.subTest(failure=type(failure).__name__):
                with patch.object(runtime, "run", side_effect=[failure, None]) as run:
                    errors = runtime.cleanup(compose, self.root, {}, StringIO())
                self.assertEqual(len(errors), 1)
                self.assertEqual(run.call_args_list[-1].args[0], [*compose, "down", "--volumes", "--remove-orphans"])

    def test_generated_environment_uses_fixture_values_and_preserves_docker_context(self):
        env_file = self.root / ".env"
        env_file.write_text("DATABASE_URL=fixture-only\nexport POSTGRES_PASSWORD=fixture-password\nAPI_HOST_PORT=49543\n")
        with patch.dict(os.environ, {
            "COMPOSE_PROJECT_NAME": "must-not-use-live-project",
            "DATABASE_URL": "must-not-use-live-database",
            "POSTGRES_PASSWORD": "must-not-use-live-password",
            "API_HOST_PORT": "1234", "DOCKER_CONTEXT": "fixture-context",
        }):
            values = runtime.environment(env_file)
        for key in ("COMPOSE_PROJECT_NAME", "DATABASE_URL", "POSTGRES_PASSWORD", "API_HOST_PORT"):
            self.assertNotIn(key, values)
        self.assertEqual(values["DOCKER_CONTEXT"], "fixture-context")

    def test_workspace_and_child_temporary_files_use_checkout_disk(self):
        checkout = self.root / "source"
        checkout.mkdir()
        with patch.object(runtime, "ROOT", checkout), patch.dict(os.environ, {"TMPDIR": "/must-not-use-tmpfs", "TEMPLATE_CHECK_ROOT": ""}):
            workspace = runtime.create_workspace("fixture-check-")
            values = runtime.environment(workspace=workspace)
        self.assertEqual(workspace.parent, self.root / ".template-checks")
        self.assertEqual(workspace.stat().st_mode & 0o777, 0o700)
        self.assertEqual(Path(values["TMPDIR"]).parent, workspace)
        self.assertTrue(Path(values["TMPDIR"]).is_dir())

    def test_partial_report_write_does_not_truncate_previous_results(self):
        report = self.root / "report.json"
        original = '{"results": [{"status": "passed"}]}\n'
        report.write_text(original)

        def fail_write(_value, stream, **_kwargs):
            stream.write('{"results": [')
            raise OSError(errno.ENOSPC, "fixture disk full")

        with patch.object(runtime.json, "dump", side_effect=fail_write):
            with self.assertRaises(OSError):
                runtime.write_report(report, {"results": []})
        self.assertEqual(report.read_text(), original)
        self.assertEqual(list(self.root.iterdir()), [report])

    def test_cleanup_still_executes_down_when_log_storage_is_full(self):
        class FullLog(StringIO):
            def write(self, _value):
                raise OSError(errno.ENOSPC, "fixture log disk full")

        output = self.root / "cleanup.txt"
        compose = [sys.executable, "-c", "import pathlib, sys; pathlib.Path(sys.argv[1]).write_text(' '.join(sys.argv[2:]))", str(output)]
        with redirect_stdout(StringIO()):
            errors = runtime.cleanup(compose, self.root, runtime.environment(), FullLog())
        self.assertTrue(errors)
        self.assertEqual(output.read_text(), "down --volumes --remove-orphans")


class ResumeCheckTests(unittest.TestCase):
    def test_resume_selects_failed_and_unrecorded_cases(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "report.json"
            path.write_text(json.dumps({"status": "running", "results": [
                {"variant": "go", "environment": "development", "status": "failed"},
                {"variant": "go", "environment": "production", "status": "passed"},
            ]}))
            cases = [("go", "development"), ("go", "production"), ("native", "development")]
            pending, passed = generated.resume_cases(cases, path)
        self.assertEqual(pending, [("go", "development"), ("native", "development")])
        self.assertEqual([(item["variant"], item["environment"]) for item in passed], [("go", "production")])

    def test_second_resume_preserves_prior_passes_but_retries_newer_failure(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "report.json"
            path.write_text(json.dumps({"retained_passes": [
                {"variant": "go", "environment": "production", "status": "passed"},
                {"variant": "go", "environment": "development", "status": "passed"},
            ], "results": [
                {"variant": "go", "environment": "development", "status": "failed"},
                {"variant": "native", "environment": "development", "status": "passed"},
            ]}))
            cases = [("go", "development"), ("go", "production"), ("native", "development")]
            pending, passed = generated.resume_cases(cases, path)
        self.assertEqual(pending, [("go", "development")])
        self.assertEqual(len(passed), 2)

    def test_resume_rejects_malformed_status_instead_of_skipping_work(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "report.json"
            path.write_text(json.dumps({"results": [{"variant": "go", "environment": "production", "status": "passsed"}]}))
            with self.assertRaises(ValueError):
                generated.resume_cases([("go", "production")], path)


class PostgresCheckTests(unittest.TestCase):
    def test_backend_uses_disposable_database_and_preserves_source(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "source/backend"
            source.mkdir(parents=True)
            (source / "pyproject.toml").write_text('[project]\nname = "fixture"\n')
            (source / ".env").write_text("DATABASE_URL=must-stay-private\n")
            workspace = root / "run"
            (workspace / "logs").mkdir(parents=True)
            url = "postgresql+asyncpg://fixture@127.0.0.1:49543/disposable"

            def run(_command, target, values, _log):
                self.assertEqual(values["TEST_POSTGRES_URL"], url)
                self.assertEqual(values["DATABASE_URL"], url)
                self.assertFalse((target / ".env").exists())
                self.assertEqual(target, workspace / "projects/backend")
                (target / "output.txt").write_text("fixture result")

            with patch.object(postgres, "ROOT", root / "source"), patch.object(postgres, "run", side_effect=run):
                with patch.dict(os.environ, {"DATABASE_URL": "live-not-allowed", "TEST_POSTGRES_URL": "live-not-allowed"}), redirect_stdout(StringIO()):
                    result = postgres.check_project("python", "backend", workspace, url)
            self.assertEqual(result["status"], "passed")
            self.assertTrue((source / ".env").exists())
            self.assertFalse((source / "output.txt").exists())
            self.assertEqual(json.loads((workspace / "backend.json").read_text())["status"], "passed")


class GeneratedCheckTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        (self.root / "projects").mkdir()
        (self.root / "logs").mkdir()
        self.name = None
        self.config = None
        self.commands = []
        self.failure = None

    def run_command(self, command, target, _values, log, **_kwargs):
        self.commands.append(command)
        if command[0] == sys.executable:
            self.name = command[4]
            project = target / self.name
            project.mkdir()
            (project / ".env").write_text("DATABASE_URL=disposable\n")
            (project / "source.txt").write_text("retained generated fixture")
        elif "build" in command and self.failure is not None:
            log.write("fixture compiler diagnostic\n")
            raise self.failure

    def render(self, *_args, **_kwargs):
        config = self.config if self.config is not None else {"name": self.name, "services": {}}
        return subprocess.CompletedProcess([], 0, json.dumps(config), "")

    def invoke(self):
        with patch.object(generated, "run", side_effect=self.run_command):
            with patch.object(generated.subprocess, "run", side_effect=self.render):
                with patch.object(generated, "cleanup", return_value=[]) as cleanup:
                    with patch.object(generated, "check_endpoints"), redirect_stdout(StringIO()):
                        result = generated.check_variant("go", "production", self.root)
        return result, cleanup

    def test_wrong_namespace_prevents_build_start_and_cleanup(self):
        self.config = {"name": "live-project", "services": {}}
        result, cleanup = self.invoke()
        self.assertEqual(result["status"], "failed")
        self.assertIn("unexpected Docker namespace", result["error"])
        self.assertEqual(len(self.commands), 1)
        cleanup.assert_not_called()

    def test_external_resources_are_rejected(self):
        for kind in ("volumes", "networks"):
            with self.subTest(kind=kind):
                config = {"name": "verify-test", kind: {"fixture": {"name": "live-data", "external": True}}}
                with self.assertRaisesRegex(RuntimeError, "disposable project"):
                    generated.validate_namespace(config, "verify-test", False)

    def test_build_failure_retains_project_and_logs_then_cleans_only_owned_project(self):
        self.failure = RuntimeError("fixture build failed")
        result, cleanup = self.invoke()
        self.assertEqual(result["status"], "failed")
        self.assertTrue((Path(result["project"]) / "source.txt").exists())
        self.assertIn("fixture compiler diagnostic", Path(result["log"]).read_text())
        self.assertIn("fixture build failed", Path(result["log"]).read_text())
        compose = cleanup.call_args.args[0]
        self.assertEqual(compose[-2:], ["--project-name", self.name])
        self.assertFalse((Path(result["project"]) / "runtime-compose.json").exists())
        self.assertTrue((self.root / "go-production.compose.json").is_file())
        self.assertEqual(json.loads((self.root / "go-production.json").read_text())["status"], "failed")

    def test_interrupted_build_retains_cancelled_case_and_cleans_owned_project(self):
        self.failure = KeyboardInterrupt()
        with patch.object(generated, "run", side_effect=self.run_command):
            with patch.object(generated.subprocess, "run", side_effect=self.render):
                with patch.object(generated, "cleanup", return_value=[]) as cleanup:
                    with self.assertRaises(KeyboardInterrupt):
                        generated.check_variant("go", "production", self.root)
        self.assertEqual(json.loads((self.root / "go-production.json").read_text())["status"], "cancelled")
        self.assertEqual(cleanup.call_args.args[0][-2:], ["--project-name", self.name])


if __name__ == "__main__":
    unittest.main()
