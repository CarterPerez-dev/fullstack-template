"""
©AngelaMos | 2026
test_publish.py
"""

from contextlib import redirect_stdout
import hashlib
from io import StringIO
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import zipfile

import publish
from catalog import CATALOG


class PublicationHistoryTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.parent = Path(temporary.name)
        self.source = self.parent / "source"
        self.remote = self.parent / "remote.git"
        self.git(self.parent, "init", "-q", "--bare", str(self.remote))
        self.git(self.parent, "init", "-q", "--initial-branch=main", str(self.source))
        self.git(self.source, "config", "user.name", "Release Fixture")
        self.git(self.source, "config", "user.email", "fixture@example.invalid")
        self.git(self.source, "config", "commit.gpgsign", "false")
        self.git(self.source, "config", "tag.gpgsign", "false")
        (self.source / "README").write_text("base fixture\n")
        self.git(self.source, "add", "README")
        self.git(self.source, "commit", "-qm", "Initial fixture")
        self.base = self.git(self.source, "rev-parse", "HEAD")
        self.git(self.source, "remote", "add", "origin", str(self.remote))
        self.git(self.source, "push", "-q", "origin", "main")
        self.git(self.source, "switch", "-qc", "release-work")
        (self.source / "README").write_text("release fixture\n")
        self.git(self.source, "commit", "-qam", "Release fixture")
        self.revision = self.git(self.source, "rev-parse", "HEAD")

    def git(self, directory, *arguments):
        return subprocess.check_output(["git", *arguments], cwd=directory, stderr=subprocess.PIPE, text=True).strip()

    def sync(self):
        execute = publish.run

        def command(*arguments, **keywords):
            if arguments[:3] == ("gh", "repo", "view"):
                return json.dumps({"nameWithOwner": publish.REPOSITORY, "isPrivate": False, "defaultBranchRef": {"name": "main"}})
            return execute(*arguments, **keywords)

        with patch.object(publish, "ROOT", self.source), patch.object(publish, "run", side_effect=command), redirect_stdout(StringIO()):
            publish.sync_release("v0.1.0", "release-work", self.revision)

    def test_sync_fast_forwards_both_branches_and_tag_without_switching_checkout(self):
        self.sync()
        self.sync()
        for ref in ("refs/heads/main", "refs/heads/release-work", "refs/tags/v0.1.0^{commit}"):
            self.assertEqual(self.git(self.remote, "rev-parse", ref), self.revision)
        self.assertEqual(self.git(self.source, "branch", "--show-current"), "release-work")
        self.assertEqual(self.git(self.source, "status", "--porcelain"), "")

    def test_diverged_remote_is_preserved_and_no_tag_is_created(self):
        peer = self.parent / "peer"
        self.git(self.parent, "clone", "-q", "--branch", "main", str(self.remote), str(peer))
        self.git(peer, "config", "user.name", "Concurrent Fixture")
        self.git(peer, "config", "user.email", "fixture@example.invalid")
        self.git(peer, "config", "commit.gpgsign", "false")
        (peer / "README").write_text("concurrent remote change\n")
        self.git(peer, "commit", "-qam", "Concurrent fixture")
        self.git(peer, "push", "-q", "origin", "main")
        remote_head = self.git(peer, "rev-parse", "HEAD")
        with self.assertRaisesRegex(ValueError, "not an ancestor"):
            self.sync()
        self.assertEqual(self.git(self.remote, "rev-parse", "main"), remote_head)
        self.assertEqual(self.git(self.source, "tag", "--list"), "")

    def test_existing_remote_version_cannot_be_reassigned(self):
        self.git(self.source, "tag", "v0.1.0", self.base)
        self.git(self.source, "push", "-q", "origin", "refs/tags/v0.1.0")
        with self.assertRaisesRegex(ValueError, "another commit"):
            self.sync()
        self.assertEqual(self.git(self.remote, "rev-parse", "main"), self.base)
        self.assertEqual(self.git(self.remote, "rev-parse", "v0.1.0"), self.base)


class PublishedAssetTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.assets = self.root / "assets"
        self.assets.mkdir()
        for name in ("install.sh", "uninstall.sh"):
            (self.root / name).write_text(f"{name} fixture\n")
            (self.assets / name).write_bytes((self.root / name).read_bytes())
        self.revision = "a" * 40
        self.metadata = {"version": "v0.1.0", "revision": self.revision, "dirty": False, "archives": {}}
        for name in CATALOG:
            path = self.assets / f"template-{name}.tar.gz"
            path.write_bytes(f"fixture archive {name}".encode())
            self.metadata["archives"][name] = {"sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "bytes": path.stat().st_size}
        self.refresh_manifest()

    def refresh_manifest(self):
        data = json.dumps(self.metadata)
        (self.assets / "release.json").write_text(data)
        with zipfile.ZipFile(self.assets / "template.pyz", "w") as archive:
            archive.writestr("release.json", data)
        sums = [f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}" for path in sorted(self.assets.iterdir()) if path.name != "checksums.txt"]
        (self.assets / "checksums.txt").write_text("\n".join(sums) + "\n")

    def verify(self):
        with patch.object(publish, "ROOT", self.root):
            publish.verify_assets(self.assets, "v0.1.0", self.revision)

    def test_complete_release_matches_reviewed_source_and_provenance(self):
        self.verify()

    def test_changed_archive_is_rejected_before_installation(self):
        (self.assets / "template-go.tar.gz").write_bytes(b"tampered archive")
        with self.assertRaisesRegex(ValueError, "checksum mismatch"):
            self.verify()

    def test_dirty_or_wrong_commit_is_rejected_even_with_valid_checksums(self):
        for changes in ({"dirty": True}, {"dirty": False, "revision": "b" * 40}):
            with self.subTest(changes=changes):
                self.metadata.update(changes)
                self.refresh_manifest()
                with self.assertRaisesRegex(ValueError, "clean reviewed commit"):
                    self.verify()

    def test_checksum_path_traversal_is_rejected(self):
        with (self.assets / "checksums.txt").open("a") as stream:
            stream.write(f"{'b' * 64}  ../outside\n")
        with self.assertRaisesRegex(ValueError, "Unexpected or duplicated"):
            self.verify()


if __name__ == "__main__":
    unittest.main()
