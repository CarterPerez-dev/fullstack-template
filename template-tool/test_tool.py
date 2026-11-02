"""
©AngelaMos | 2026
test_tool.py
"""

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import tempfile
import unittest
from unittest.mock import patch

from catalog import CATALOG, excluded
from cli import acquire, copy_source, extract_archive, generate
from release import build


ROOT = Path(__file__).resolve().parent.parent


class SafetyTests(unittest.TestCase):
    def test_only_environment_examples_are_copied(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source, target = root / "source", root / "target"
            source.mkdir()
            target.mkdir()
            for name in (".env", ".env.development", ".env.staging", "secret.pem", "private.key", "release.jks", "signing.p8", ".env.example", ".env.development.example", "app.py"):
                (source / name).write_text("fixture\n")
            (source / ".tamagui").mkdir()
            (source / ".tamagui/config.json").write_text("{}")
            copy_source(source, target)
            self.assertEqual({path.name for path in target.iterdir()}, {".env.example", ".env.development.example", "app.py"})

    def test_source_symlink_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "source").mkdir()
            (root / "target").mkdir()
            (root / "private").write_text("fixture\n")
            (root / "source/leak").symlink_to(root / "private")
            with self.assertRaisesRegex(ValueError, "symlink"):
                copy_source(root / "source", root / "target")
            self.assertFalse((root / "target/leak").exists())

    def test_archive_rejects_traversal_links_and_duplicates(self):
        for name, kind in (("../escape", tarfile.REGTYPE), ("/escape", tarfile.REGTYPE), ("a\\escape", tarfile.REGTYPE), ("a", tarfile.SYMTYPE), ("a", tarfile.LNKTYPE), (".env.development", tarfile.REGTYPE)):
            with self.subTest(name=name, kind=kind), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                archive_path = root / "bad.tar.gz"
                with tarfile.open(archive_path, "w:gz") as archive:
                    entry = tarfile.TarInfo(name)
                    entry.type = kind
                    entry.linkname = "../escape" if kind != tarfile.REGTYPE else ""
                    archive.addfile(entry)
                target = root / "target"
                target.mkdir()
                with self.assertRaises(ValueError):
                    extract_archive(archive_path, target)
                self.assertEqual(list(target.iterdir()), [])

    def test_checksum_failure_does_not_extract(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "template-open.tar.gz").write_bytes(b"altered")
            target = root / "target"
            target.mkdir()
            with self.assertRaisesRegex(ValueError, "Checksum mismatch"):
                acquire("open", {"archives": {"open": {"sha256": "0" * 64}}}, target, root)
            self.assertEqual(list(target.iterdir()), [])

    def test_duplicate_archive_entry_is_rejected_before_writes(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            archive_path = root / "duplicates.tar.gz"
            with tarfile.open(archive_path, "w:gz") as archive:
                archive.addfile(tarfile.TarInfo("same.txt"))
                archive.addfile(tarfile.TarInfo("same.txt"))
            target = root / "target"
            target.mkdir()
            with self.assertRaises(ValueError):
                extract_archive(archive_path, target)
            self.assertEqual(list(target.iterdir()), [])

    def test_existing_project_is_untouched(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "keep.txt").write_text("original")
            args = argparse.Namespace(type="open", name=None, owner="tester", source=ROOT, release_dir=None, no_git=True, install=False)
            with patch("pathlib.Path.cwd", return_value=root), self.assertRaisesRegex(ValueError, "not empty"):
                generate(args, {"version": "development"})
            self.assertEqual((root / "keep.txt").read_text(), "original")
            self.assertEqual(len(list(root.iterdir())), 1)


class ReleaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory(prefix="template-tests-")
        cls.root = Path(cls.temporary.name)
        cls.assets = cls.root / "release"
        cls.metadata = build(ROOT, cls.assets, "v0.1.0-test", allow_dirty=True)

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def test_all_variants_packaged_without_private_files(self):
        self.assertEqual(set(self.metadata["archives"]), set(CATALOG))
        for name in CATALOG:
            with self.subTest(template=name):
                path = self.assets / f"template-{name}.tar.gz"
                self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), self.metadata["archives"][name]["sha256"])
                with tarfile.open(path) as archive:
                    members = archive.getmembers()
                    self.assertTrue(members)
                    self.assertFalse(any(excluded(Path(member.name)) or not member.isfile() for member in members))

    def test_all_eight_archives_generate_with_provenance(self):
        for name in CATALOG:
            with self.subTest(template=name):
                result = subprocess.run(
                    [sys.executable, "-B", str(self.assets / "template.pyz"), name, f"smoke-{name}", "--release-dir", str(self.assets), "--no-git"],
                    cwd=self.root, capture_output=True, text=True,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                target = self.root / f"smoke-{name}"
                provenance = json.loads((target / ".template.json").read_text())
                self.assertEqual(provenance["template"], name)
                self.assertEqual(provenance["source_revision"], self.metadata["revision"])
                self.assertTrue(provenance["source_dirty"])
                self.assertFalse((target / ".git").exists())
                self.assertFalse(any(path.suffix in {".pem", ".key"} for path in target.rglob("*")))
                if (target / "dev.compose.yml").exists() and (target / ".env.example").exists():
                    self.assertTrue((target / ".env.development").exists())
                    self.assertEqual((target / ".env.development").stat().st_mode & 0o777, 0o600)
                if name in {"fastapi", "fastapi-stack", "portfolio"}:
                    prod = dict(line.split("=", 1) for line in (target / ".env").read_text().splitlines() if "=" in line and not line.startswith("#"))
                    dev = dict(line.split("=", 1) for line in (target / ".env.development").read_text().splitlines() if "=" in line and not line.startswith("#"))
                    for key in ("SECRET_KEY", "POSTGRES_PASSWORD", "REDIS_PASSWORD"):
                        self.assertNotIn("CHANGE_ME", prod[key])
                        self.assertNotEqual(prod[key], dev[key])
                    prod_ports = {int(value) for key, value in prod.items() if key.endswith("_HOST_PORT")}
                    dev_ports = {int(value) for key, value in dev.items() if key.endswith("_HOST_PORT")}
                    self.assertFalse(prod_ports & dev_ports)
                    self.assertTrue(all(30000 <= port <= 60000 for port in prod_ports | dev_ports))

    def test_piped_install_reinstall_and_uninstall(self):
        prefix = self.root / "installed-bin"
        environment = os.environ.copy()
        environment["PATH"] = str(prefix) + os.pathsep + environment["PATH"]
        command = ["bash", "-s", "--", "--from", str(self.assets), "--prefix", str(prefix), "--no-modify-path"]
        for _ in range(2):
            result = subprocess.run(command, input=(ROOT / "install.sh").read_text(), env=environment, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
        result = subprocess.run(["template", "--version"], env=environment, capture_output=True, text=True, check=True)
        self.assertEqual(result.stdout.strip(), "template v0.1.0-test")
        subprocess.run(["bash", str(ROOT / "uninstall.sh"), "--prefix", str(prefix)], env=environment, capture_output=True, check=True)
        self.assertFalse((prefix / "template").exists())

    def test_generated_credentials_are_ignored_by_git(self):
        for name in CATALOG:
            with self.subTest(template=name):
                target = self.root / f"ignored-{name}"
                subprocess.run(
                    [sys.executable, "-B", str(self.assets / "template.pyz"), name,
                     target.name, "--release-dir", str(self.assets)],
                    cwd=self.root, capture_output=True, text=True, check=True,
                )
                environments = list(target.rglob(".env*"))
                self.assertTrue(environments)
                for path in environments:
                    result = subprocess.run(
                        ["git", "check-ignore", "--no-index", str(path.relative_to(target))],
                        cwd=target, capture_output=True, text=True,
                    )
                    expected = 1 if path.name.endswith(".example") else 0
                    self.assertEqual(result.returncode, expected, str(path))

    @unittest.skipUnless(shutil.which("docker"), "Docker Compose is needed to render configuration")
    def test_all_variants_compose_contracts(self):
        for name in CATALOG:
            with self.subTest(template=name):
                result = subprocess.run(
                    [sys.executable, "-B", str(self.assets / "template.pyz"), name, f"compose-{name}", "--release-dir", str(self.assets), "--no-git"],
                    cwd=self.root, capture_output=True, text=True,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                target = self.root / f"compose-{name}"
                namespaces = set()
                for compose, environment in (("compose.yml", ".env"), ("dev.compose.yml", ".env.development")):
                    if not (target / compose).exists():
                        self.assertEqual(name, "native")
                        continue
                    result = subprocess.run(
                        ["docker", "compose", "--env-file", environment, "-f", compose, "config", "--format", "json"],
                        cwd=target, capture_output=True, text=True,
                    )
                    self.assertEqual(result.returncode, 0, result.stderr)
                    config = json.loads(result.stdout)
                    self.assertNotIn(config["name"], namespaces)
                    namespaces.add(config["name"])
                    for service in config["services"].values():
                        for port in service.get("ports", []):
                            self.assertTrue(30000 <= int(port["published"]) <= 60000)
                        if service.get("image", "").startswith("postgres:18"):
                            destinations = {volume["target"] for volume in service["volumes"]}
                            self.assertIn("/var/lib/postgresql", destinations)
                            self.assertNotIn("/var/lib/postgresql/data", destinations)

    def test_frontend_and_native_accept_explicit_backend(self):
        for name, key in (("frontend", "API_PROXY_TARGET"), ("native", "EXPO_PUBLIC_API_URL")):
            with self.subTest(template=name):
                result = subprocess.run(
                    [sys.executable, "-B", str(self.assets / "template.pyz"), name, f"endpoint-{name}", "--release-dir", str(self.assets), "--no-git", "--api-url", "https://api.example.com/api"],
                    cwd=self.root, capture_output=True, text=True,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                for environment in (".env", ".env.development"):
                    content = (self.root / f"endpoint-{name}" / environment).read_text()
                    self.assertIn(f"{key}=https://api.example.com/api", content)

    def test_go_source_copies_remain_equivalent(self):
        first = ROOT / "backends/go-backend"
        second = ROOT / "stacks/go-react/go-backend"
        for directory in ("cmd", "internal", "migrations"):
            paths = {path.relative_to(first) for path in (first / directory).rglob("*") if path.is_file()}
            copies = {path.relative_to(second) for path in (second / directory).rglob("*") if path.is_file()}
            self.assertEqual(paths, copies)
            for path in paths:
                with self.subTest(path=str(path)):
                    self.assertEqual((first / path).read_bytes(), (second / path).read_bytes())

    def test_python_auth_copies_remain_equivalent(self):
        first = ROOT / "backends/fastapi/app"
        for name in ("auth/RefreshToken.py", "auth/repository.py", "auth/service.py", "user/repository.py"):
            expected = (first / name).read_bytes()
            for variant in ("fastapi-react", "portfolio"):
                with self.subTest(variant=variant, file=name):
                    self.assertEqual(expected, (ROOT / "stacks" / variant / "backend/app" / name).read_bytes())

    def test_installer_preserves_unrelated_command(self):
        prefix = self.root / "unrelated-bin"
        prefix.mkdir()
        (prefix / "template").write_text("do not replace")
        result = subprocess.run(["bash", str(ROOT / "install.sh"), "--from", str(self.assets), "--prefix", str(prefix), "--no-modify-path"], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual((prefix / "template").read_text(), "do not replace")

    def test_release_bytes_are_reproducible(self):
        second = self.root / "second-release"
        build(ROOT, second, "v0.1.0-test", allow_dirty=True)
        self.assertEqual((self.assets / "checksums.txt").read_bytes(), (second / "checksums.txt").read_bytes())


if __name__ == "__main__":
    unittest.main()
