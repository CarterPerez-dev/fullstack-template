"""
©AngelaMos | 2026
test_portfolio_media.py
"""

from datetime import UTC, datetime
from io import BytesIO
from pathlib import Path
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

from fastapi import UploadFile
import pytest
from starlette.datastructures import Headers

from portfolio.models import Media
from portfolio.repository import MediaRepository
from portfolio.service import MediaService


@pytest.fixture
def media_session(monkeypatch, tmp_path):
    monkeypatch.setattr("portfolio.service.settings.UPLOAD_DIR", str(tmp_path))
    return AsyncMock()


def uploaded_file():
    return UploadFile(
        file=BytesIO(b"media-fixture"), filename="../../untrusted-name.png",
        headers=Headers({"content-type": "image/png"}),
    )


async def create_media_row(_session, **values):
    return Media(id=uuid4(), created_at=datetime.now(UTC), **values)


@pytest.mark.asyncio
async def test_upload_insert_failure_rolls_back_and_removes_file(media_session, monkeypatch, tmp_path):
    monkeypatch.setattr(MediaRepository, "create", AsyncMock(side_effect=RuntimeError("insert failed")))
    with pytest.raises(RuntimeError, match="insert failed"):
        await MediaService(media_session).upload(uploaded_file())
    media_session.rollback.assert_awaited_once()
    media_session.commit.assert_not_awaited()
    assert list(tmp_path.iterdir()) == []


@pytest.mark.asyncio
async def test_uncertain_commit_keeps_upload_for_reconciliation(media_session, monkeypatch, tmp_path):
    monkeypatch.setattr(MediaRepository, "create", create_media_row)
    media_session.commit.side_effect = RuntimeError("commit acknowledgement lost")
    with pytest.raises(RuntimeError, match="commit acknowledgement lost"):
        await MediaService(media_session).upload(uploaded_file())
    files = list(tmp_path.iterdir())
    assert len(files) == 1
    assert files[0].read_bytes() == b"media-fixture"


@pytest.mark.asyncio
async def test_upload_commits_only_after_complete_file_exists(media_session, monkeypatch, tmp_path):
    monkeypatch.setattr(MediaRepository, "create", create_media_row)

    async def commit():
        files = list(tmp_path.iterdir())
        assert len(files) == 1
        assert files[0].read_bytes() == b"media-fixture"
        assert files[0].name != "untrusted-name.png"

    media_session.commit.side_effect = commit
    response = await MediaService(media_session).upload(uploaded_file())
    assert response.byte_size == len(b"media-fixture")
    media_session.commit.assert_awaited_once()


@pytest.mark.asyncio
@pytest.mark.parametrize("failure", ["delete", "commit", None])
async def test_media_file_survives_until_deletion_commits(media_session, monkeypatch, tmp_path, failure):
    path = tmp_path / "stored.png"
    path.write_bytes(b"retained-media")
    row = Media(id=uuid4(), storage_filename=path.name)
    monkeypatch.setattr(MediaRepository, "get_by_id", AsyncMock(return_value=row))
    delete = AsyncMock()
    if failure == "delete":
        delete.side_effect = RuntimeError("delete failed")
    monkeypatch.setattr(MediaRepository, "delete", delete)

    async def commit():
        assert path.read_bytes() == b"retained-media"
        if failure == "commit":
            raise RuntimeError("commit failed")

    media_session.commit.side_effect = commit
    service = MediaService(media_session)
    if failure:
        with pytest.raises(RuntimeError, match=f"{failure} failed"):
            await service.delete_media(row.id)
        assert path.read_bytes() == b"retained-media"
    else:
        await service.delete_media(row.id)
        assert not path.exists()
        media_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_failed_unlink_is_reported_after_database_deletion(media_session, monkeypatch, tmp_path):
    path = tmp_path / "stored.png"
    path.write_bytes(b"retained-media")
    row = Media(id=uuid4(), storage_filename=path.name)
    monkeypatch.setattr(MediaRepository, "get_by_id", AsyncMock(return_value=row))
    monkeypatch.setattr(MediaRepository, "delete", AsyncMock())
    original_unlink = Path.unlink

    def denied_unlink(target, *args, **kwargs):
        if target == path:
            raise PermissionError("injected file permission error")
        return original_unlink(target, *args, **kwargs)

    monkeypatch.setattr(Path, "unlink", denied_unlink)
    logger = Mock()
    monkeypatch.setattr("portfolio.service.logger", logger)
    await MediaService(media_session).delete_media(row.id)
    media_session.commit.assert_awaited_once()
    assert path.exists()
    logger.warning.assert_called_once_with("media_cleanup_required", storage_filename=path.name)


def test_upload_file_creation_never_replaces_existing_data(tmp_path):
    path = tmp_path / "stored.png"
    path.write_bytes(b"existing")
    with pytest.raises(FileExistsError):
        MediaService._write_upload(path, b"replacement")
    assert path.read_bytes() == b"existing"


def test_failed_file_flush_removes_partial_upload(monkeypatch, tmp_path):
    path = tmp_path / "stored.png"
    monkeypatch.setattr("portfolio.service.os.fsync", Mock(side_effect=OSError("disk failure")))
    with pytest.raises(OSError, match="disk failure"):
        MediaService._write_upload(path, b"partial")
    assert not path.exists()
