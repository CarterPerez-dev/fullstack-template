"""
© AngelaMos | 2026
service.py
"""

import asyncio
import os
from pathlib import Path
from typing import TypeVar
from uuid import UUID

import uuid6
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from core.base_schema import BaseSchema, BaseResponseSchema
from core.constants import (
    ALLOWED_UPLOAD_CONTENT_TYPES,
    MAX_UPLOAD_BYTES,
)
from core.exceptions import InvalidUpload, ResourceNotFound
from core.logging import get_logger
from .models import Media
from .repository import (
    CertificationRepository,
    CustomSectionRepository,
    ExperienceRepository,
    LinkRepository,
    MediaRepository,
    OrderedModelT,
    OrderedRepository,
    ProfileRepository,
    ProjectRepository,
    SiteSettingsRepository,
    SkillGroupRepository,
)
from .schemas import (
    CertificationResponse,
    CustomSectionResponse,
    ExperienceResponse,
    LinkResponse,
    MediaResponse,
    PortfolioResponse,
    ProfileResponse,
    ProfileUpdate,
    ProjectResponse,
    RegistrationStatusResponse,
    SiteSettingsResponse,
    SiteSettingsUpdate,
    SkillGroupResponse,
)


ResponseT = TypeVar("ResponseT", bound = BaseResponseSchema)
logger = get_logger(__name__)

_EXTENSION_BY_TYPE = {
    "image/png": ".png",
    "image/jpeg": ".jpg",
    "image/gif": ".gif",
    "image/webp": ".webp",
    "image/svg+xml": ".svg",
    "image/x-icon": ".ico",
    "image/vnd.microsoft.icon": ".ico",
    "application/pdf": ".pdf",
}


class PortfolioService:
    """
    Business logic for portfolio content.
    """
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_portfolio(self) -> PortfolioResponse:
        """
        Assemble the full public portfolio payload.
        """
        profile = await ProfileRepository.get_or_create(self.session)
        site_settings = await SiteSettingsRepository.get_or_create(self.session)
        certifications = await CertificationRepository.list_ordered(self.session)
        projects = await ProjectRepository.list_ordered(self.session)
        experience = await ExperienceRepository.list_ordered(self.session)
        skill_groups = await SkillGroupRepository.list_ordered(self.session)
        links = await LinkRepository.list_ordered(self.session)
        custom_sections = await CustomSectionRepository.list_ordered(self.session)

        return PortfolioResponse(
            profile = ProfileResponse.model_validate(profile),
            settings = SiteSettingsResponse.model_validate(site_settings),
            certifications = [
                CertificationResponse.model_validate(item) for item in certifications
            ],
            projects = [ProjectResponse.model_validate(item) for item in projects],
            experience = [
                ExperienceResponse.model_validate(item) for item in experience
            ],
            skill_groups = [
                SkillGroupResponse.model_validate(item) for item in skill_groups
            ],
            links = [LinkResponse.model_validate(item) for item in links],
            custom_sections = [
                CustomSectionResponse.model_validate(item) for item in custom_sections
            ],
        )

    async def registration_status(self) -> RegistrationStatusResponse:
        """
        Owner enrollment is restricted to the trusted server console.
        """
        return RegistrationStatusResponse(registration_open = False)

    async def update_profile(self, data: ProfileUpdate) -> ProfileResponse:
        """
        Update the profile singleton.
        """
        profile = await ProfileRepository.get_or_create(self.session)
        updates = data.model_dump(exclude_unset = True)
        updated = await ProfileRepository.update(self.session, profile, **updates)
        return ProfileResponse.model_validate(updated)

    async def update_settings(self, data: SiteSettingsUpdate) -> SiteSettingsResponse:
        """
        Update the site settings singleton.
        """
        site_settings = await SiteSettingsRepository.get_or_create(self.session)
        updates = data.model_dump(exclude_unset = True)
        updated = await SiteSettingsRepository.update(
            self.session,
            site_settings,
            **updates
        )
        return SiteSettingsResponse.model_validate(updated)

    async def list_items(
        self,
        repo: type[OrderedRepository[OrderedModelT]],
        schema: type[ResponseT],
    ) -> list[ResponseT]:
        """
        List an ordered resource.
        """
        rows = await repo.list_ordered(self.session)
        return [schema.model_validate(row) for row in rows]

    async def create_item(
        self,
        repo: type[OrderedRepository[OrderedModelT]],
        schema: type[ResponseT],
        data: BaseSchema,
    ) -> ResponseT:
        """
        Create a list item.
        """
        row = await repo.create(self.session, **data.model_dump())
        return schema.model_validate(row)

    async def update_item(
        self,
        repo: type[OrderedRepository[OrderedModelT]],
        schema: type[ResponseT],
        item_id: UUID,
        data: BaseSchema,
        resource: str,
    ) -> ResponseT:
        """
        Update a list item.
        """
        row = await repo.get_by_id(self.session, item_id)
        if row is None:
            raise ResourceNotFound(resource, str(item_id))
        updated = await repo.update(
            self.session,
            row,
            **data.model_dump(exclude_unset = True)
        )
        return schema.model_validate(updated)

    async def delete_item(
        self,
        repo: type[OrderedRepository[OrderedModelT]],
        item_id: UUID,
        resource: str,
    ) -> None:
        """
        Delete a list item.
        """
        row = await repo.get_by_id(self.session, item_id)
        if row is None:
            raise ResourceNotFound(resource, str(item_id))
        await repo.delete(self.session, row)

    async def reorder_items(
        self,
        repo: type[OrderedRepository[OrderedModelT]],
        ordered_ids: list[UUID],
    ) -> None:
        """
        Reorder a list resource.
        """
        await repo.reorder(self.session, ordered_ids)


class MediaService:
    """
    Business logic for uploaded media.
    """
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def _upload_dir(self) -> Path:
        directory = Path(settings.UPLOAD_DIR)
        directory.mkdir(parents = True, exist_ok = True)
        return directory

    @staticmethod
    def _write_upload(destination: Path, contents: bytes) -> None:
        with destination.open("xb") as stream:
            try:
                stream.write(contents)
                stream.flush()
                os.fsync(stream.fileno())
            except OSError:
                destination.unlink(missing_ok = True)
                raise
        directory = os.open(destination.parent, os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)

    @staticmethod
    async def _remove_file(path: Path) -> None:
        try:
            await asyncio.to_thread(path.unlink, missing_ok = True)
        except OSError:
            logger.warning("media_cleanup_required", storage_filename = path.name)

    async def list_media(self) -> list[MediaResponse]:
        """
        List all uploaded media.
        """
        rows = await MediaRepository.list_all(self.session)
        return [MediaResponse.model_validate(row) for row in rows]

    async def upload(self, file: UploadFile) -> MediaResponse:
        """
        Validate and persist an uploaded file.
        """
        content_type = (file.content_type or "").lower()
        if content_type not in ALLOWED_UPLOAD_CONTENT_TYPES:
            raise InvalidUpload(
                message = f"Unsupported file type: {content_type or 'unknown'}"
            )

        contents = await file.read(MAX_UPLOAD_BYTES + 1)
        if len(contents) == 0:
            raise InvalidUpload(message = "Uploaded file is empty")
        if len(contents) > MAX_UPLOAD_BYTES:
            raise InvalidUpload(message = "File exceeds the maximum upload size")

        original_filename = file.filename or "upload"
        extension = _EXTENSION_BY_TYPE[content_type]

        storage_filename = f"{uuid6.uuid7().hex}{extension}"
        directory = self._upload_dir()
        destination = directory / storage_filename

        await asyncio.to_thread(self._write_upload, destination, contents)

        try:
            row = await MediaRepository.create(
                self.session,
                original_filename = original_filename,
                content_type = content_type,
                byte_size = len(contents),
                storage_filename = storage_filename,
            )
            response = MediaResponse.model_validate(row)
        except Exception:
            await self.session.rollback()
            await self._remove_file(destination)
            raise

        await self.session.commit()
        return response

    async def get_media(self, media_id: UUID) -> Media:
        """
        Fetch media metadata or raise 404.
        """
        row = await MediaRepository.get_by_id(self.session, media_id)
        if row is None:
            raise ResourceNotFound("Media", str(media_id))
        return row

    def media_path(self, media: Media) -> Path:
        """
        Resolve the on-disk path for a media row, raising 404 if missing.
        """
        path = Path(settings.UPLOAD_DIR) / media.storage_filename
        if not path.is_file():
            raise ResourceNotFound("Media", str(media.id))
        return path

    async def delete_media(self, media_id: UUID) -> None:
        """
        Delete media metadata and the underlying file.
        """
        row = await self.get_media(media_id)
        path = Path(settings.UPLOAD_DIR) / row.storage_filename
        await MediaRepository.delete(self.session, row)
        await self.session.commit()
        await self._remove_file(path)
