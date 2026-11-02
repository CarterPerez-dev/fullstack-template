"""
© AngelaMos | 2026
repository.py
"""

from collections.abc import Sequence
from typing import Generic, TypeVar
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from core.base_repository import BaseRepository
from .models import (
    Certification,
    CustomSection,
    Experience,
    Link,
    Media,
    Profile,
    Project,
    SiteSettings,
    SkillGroup,
)

ModelT = TypeVar("ModelT", bound = Profile | SiteSettings)
OrderedModelT = TypeVar(
    "OrderedModelT",
    bound = Certification | Project | Experience | SkillGroup | Link | CustomSection,
)


class SingletonRepository(BaseRepository[ModelT], Generic[ModelT]):
    """
    Repository for a single-row table.
    """

    @classmethod
    async def get_or_create(cls, session: AsyncSession) -> ModelT:
        """
        Return the sole row, creating a default one if absent.
        """
        result = await session.execute(select(cls.model))
        instance = result.scalar_one_or_none()
        if instance is None:
            await session.execute(
                insert(cls.model).values(singleton_key = True)
                .on_conflict_do_nothing(index_elements = ["singleton_key"])
            )
            result = await session.execute(select(cls.model))
            instance = result.scalar_one()
        return instance


class OrderedRepository(BaseRepository[OrderedModelT], Generic[OrderedModelT]):
    """
    Repository for an ordered list resource with display_order.
    """

    @classmethod
    async def list_ordered(cls, session: AsyncSession) -> Sequence[OrderedModelT]:
        """
        Return all rows ordered by display_order then creation time.
        """
        result = await session.execute(
            select(cls.model).order_by(
                cls.model.display_order.asc(),
                cls.model.created_at.asc(),
            )
        )
        return result.scalars().all()

    @classmethod
    async def reorder(
        cls,
        session: AsyncSession,
        ordered_ids: list[UUID],
    ) -> None:
        """
        Assign display_order to match the supplied id ordering.
        """
        for index, item_id in enumerate(ordered_ids):
            instance = await session.get(cls.model, item_id)
            if instance is not None:
                instance.display_order = index
        await session.flush()


class ProfileRepository(SingletonRepository[Profile]):
    """
    Store the public portfolio profile.
    """
    model = Profile


class SiteSettingsRepository(SingletonRepository[SiteSettings]):
    """
    Store the portfolio presentation settings.
    """
    model = SiteSettings


class CertificationRepository(OrderedRepository[Certification]):
    """
    Store ordered certification entries.
    """
    model = Certification


class ProjectRepository(OrderedRepository[Project]):
    """
    Store ordered project entries.
    """
    model = Project


class ExperienceRepository(OrderedRepository[Experience]):
    """
    Store ordered employment and experience entries.
    """
    model = Experience


class SkillGroupRepository(OrderedRepository[SkillGroup]):
    """
    Store ordered groups of portfolio skills.
    """
    model = SkillGroup


class LinkRepository(OrderedRepository[Link]):
    """
    Store ordered public profile links.
    """
    model = Link


class CustomSectionRepository(OrderedRepository[CustomSection]):
    """
    Store ordered custom portfolio sections.
    """
    model = CustomSection


class MediaRepository(BaseRepository[Media]):
    """
    Store uploaded media metadata.
    """
    model = Media

    @classmethod
    async def list_all(cls, session: AsyncSession) -> Sequence[Media]:
        """
        Return all media rows, newest first.
        """
        result = await session.execute(
            select(Media).order_by(Media.created_at.desc())
        )
        return result.scalars().all()
