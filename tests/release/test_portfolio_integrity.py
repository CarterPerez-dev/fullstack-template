"""
©AngelaMos | 2026
test_portfolio_integrity.py
"""

import asyncio

import pytest
from sqlalchemy import func, null, select
from sqlalchemy.exc import IntegrityError

from portfolio.models import Certification, Link, Media, Profile, Project, SiteSettings
from portfolio.repository import ProfileRepository, SiteSettingsRepository
from portfolio.service import MediaService
from test_python_security import sessions as sessions


@pytest.mark.asyncio
@pytest.mark.parametrize("repository", [ProfileRepository, SiteSettingsRepository])
async def test_concurrent_first_reads_create_one_singleton(sessions, repository):
    async def create():
        async with sessions.begin() as session:
            row = await repository.get_or_create(session)
            return row.id

    async with asyncio.timeout(10):
        ids = await asyncio.gather(*(create() for _ in range(8)))
    assert len(set(ids)) == 1
    async with sessions() as session:
        count = await session.scalar(select(func.count()).select_from(repository.model))
        assert count == 1


@pytest.mark.asyncio
@pytest.mark.parametrize("model", [Profile, SiteSettings])
async def test_database_refuses_duplicate_and_false_singleton_keys(sessions, model):
    async with sessions.begin() as session:
        session.add(model())
    for values in ({}, {"singleton_key": False}, {"singleton_key": null()}):
        with pytest.raises(IntegrityError):
            async with sessions.begin() as session:
                session.add(model(**values))
                await session.flush()


@pytest.mark.asyncio
@pytest.mark.parametrize("repository", [ProfileRepository, SiteSettingsRepository])
async def test_existing_singleton_content_survives_repeated_reads(sessions, repository):
    field = "name" if repository is ProfileRepository else "site_title"
    async with sessions.begin() as session:
        row = await repository.get_or_create(session)
        setattr(row, field, "Preserved content")
        original_id = row.id
    async with sessions.begin() as session:
        row = await repository.get_or_create(session)
        assert row.id == original_id
        assert getattr(row, field) == "Preserved content"


@pytest.mark.asyncio
async def test_deleting_media_clears_all_public_references(sessions, monkeypatch, tmp_path):
    monkeypatch.setattr("portfolio.service.settings.UPLOAD_DIR", str(tmp_path))
    async with sessions.begin() as session:
        media = Media(
            original_filename="test.png", content_type="image/png", byte_size=1,
            storage_filename="test.png",
        )
        session.add(media)
        await session.flush()
        profile = await ProfileRepository.get_or_create(session)
        settings = await SiteSettingsRepository.get_or_create(session)
        profile.avatar_media_id = media.id
        settings.favicon_media_id = media.id
        certification = Certification(name="Test", badge_media_id=media.id)
        project = Project(title="Test", image_media_id=media.id)
        link = Link(label="Test", media_id=media.id)
        session.add_all([certification, project, link])
        await session.flush()
        references = [
            (Profile, profile.id, "avatar_media_id"),
            (SiteSettings, settings.id, "favicon_media_id"),
            (Certification, certification.id, "badge_media_id"),
            (Project, project.id, "image_media_id"),
            (Link, link.id, "media_id"),
        ]
        media_id = media.id
    (tmp_path / "test.png").write_bytes(b"x")
    async with sessions() as session:
        await MediaService(session).delete_media(media_id)
    async with sessions() as session:
        for model, record_id, field in references:
            record = await session.get(model, record_id)
            assert record is not None and getattr(record, field) is None
        assert await session.get(Media, media_id) is None
    assert not (tmp_path / "test.png").exists()
