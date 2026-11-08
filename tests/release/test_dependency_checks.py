"""
©AngelaMos | 2026
test_dependency_checks.py
"""

from contextlib import redirect_stdout
from importlib import import_module
from io import StringIO
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch


sys.path.insert(0, str(Path(__file__).resolve().parent))
checks = import_module("check_dependencies")


class DependencyCheckTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.source = self.root / "source" / "client"
        self.source.mkdir(parents=True)
        (self.source / "package.json").write_text('{"private": true}\n')
        (self.source / "pnpm-lock.yaml").write_text("lockfileVersion: '9.0'\n")
        (self.source / ".env").write_text("SECRET_KEY=fixture-only\n")
        (self.source / "node_modules").mkdir()
        (self.source / "node_modules/stale").write_text("stale fixture")
        (self.source / ".venv").mkdir()
        (self.source / ".venv/stale").write_text("stale fixture")
        self.workspace = self.root / "run"
        (self.workspace / "logs").mkdir(parents=True)
        self.addCleanup(patch.stopall)
        patch.object(checks, "ROOT", self.root / "source").start()
        patch.object(checks.subprocess, "check_output", return_value=checks.PNPM_VERSION).start()
        patch.object(checks, "commands", return_value=[("fixture-install",), ("fixture-build",)]).start()

    def test_checks_use_clean_copy_and_leave_source_untouched(self):
        original = checks.fingerprints(self.source)

        def run(_command, target, environment, _log, *, verbose=False):
            self.assertEqual(target, self.workspace / "projects/client")
            self.assertFalse((target / ".env").exists())
            self.assertFalse((target / "node_modules/stale").exists())
            self.assertFalse((target / ".venv/stale").exists())
            self.assertNotIn("TEST_POSTGRES_URL", environment)
            self.assertNotIn("TEMPLATE_TEST_DEPENDENCIES", environment)
            (target / "build-fixture.txt").write_text("isolated build")

        with patch.object(checks, "run", side_effect=run), patch.dict(
            checks.os.environ, {"TEST_POSTGRES_URL": "fixture-must-not-connect", "TEMPLATE_TEST_DEPENDENCIES": "stale-tree"},
        ):
            result = checks.check_project("web", "client", self.workspace, False)
        self.assertEqual(result["status"], "passed")
        self.assertEqual(checks.fingerprints(self.source), original)
        self.assertFalse((self.source / "build-fixture.txt").exists())
        self.assertTrue((self.source / ".env").is_file())
        self.assertTrue((self.source / "node_modules/stale").is_file())

    def test_command_failure_stops_project_and_retains_log(self):
        with patch.object(checks, "run", side_effect=RuntimeError("fixture build failed")) as run:
            result = checks.check_project("web", "client", self.workspace, False)
        self.assertEqual(result["status"], "failed")
        self.assertEqual(run.call_count, 1)
        self.assertIn("fixture build failed", Path(result["log"]).read_text())

    def test_successful_command_cannot_silently_change_lock(self):
        original = checks.fingerprints(self.source)

        def rewrite_lock(_command, target, _environment, _log, *, verbose=False):
            (target / "pnpm-lock.yaml").write_text("changed fixture lock\n")

        with patch.object(checks, "run", side_effect=rewrite_lock):
            result = checks.check_project("web", "client", self.workspace, False)
        self.assertEqual(result["status"], "failed")
        self.assertIn("changed during locked verification", result["error"])
        self.assertEqual(checks.fingerprints(self.source), original)

    def test_successful_command_cannot_silently_change_dependency_patch(self):
        patches = self.source / "patches"
        patches.mkdir()
        (patches / "fixture.patch").write_text("original dependency patch\n")

        def rewrite_patch(_command, target, _environment, _log, *, verbose=False):
            (target / "patches/fixture.patch").write_text("changed dependency patch\n")

        with patch.object(checks, "run", side_effect=rewrite_patch):
            result = checks.check_project("web", "client", self.workspace, False)
        self.assertEqual(result["status"], "failed")
        self.assertIn("patches/fixture.patch", result["inputs"])
        self.assertEqual((patches / "fixture.patch").read_text(), "original dependency patch\n")


class CommandOutputTests(unittest.TestCase):
    def test_quiet_output_retains_child_stdout_and_stderr(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            terminal = StringIO()
            log = StringIO()
            command = (sys.executable, "-c", "import sys; print('fixture stdout'); print('fixture stderr', file=sys.stderr)")
            with redirect_stdout(terminal):
                checks.run(command, target, checks.os.environ.copy(), log)
            self.assertNotIn("\nfixture stdout\n", terminal.getvalue())
            self.assertNotIn("\nfixture stderr\n", terminal.getvalue())
            self.assertIn("\nfixture stdout\n", log.getvalue())
            self.assertIn("\nfixture stderr\n", log.getvalue())


if __name__ == "__main__":
    unittest.main()
