"""
© AngelaMos | 2026
models.py
"""

from uuid import UUID

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Integer, String, Text, true
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from config import ItemStatus, SafeEnum
from core.constants import (
    COLOR_MAX_LENGTH,
    EMAIL_MAX_LENGTH,
    FONT_MAX_LENGTH,
    MEDIA_CONTENT_TYPE_MAX_LENGTH,
    MEDIA_FILENAME_MAX_LENGTH,
    PORTFOLIO_MEDIUM_TEXT,
    PORTFOLIO_META_TEXT,
    PORTFOLIO_SHORT_TEXT,
    PORTFOLIO_TINY_TEXT,
    URL_MAX_LENGTH,
)
from core.Base import Base, TimestampMixin, UUIDMixin


class Profile(Base, UUIDMixin, TimestampMixin):
    """
    Singleton identity block (hero and about content).
    """
    __tablename__ = "portfolio_profile"
    __table_args__ = (
        CheckConstraint("singleton_key = true", name = "singleton_key_true"),
    )

    singleton_key: Mapped[bool] = mapped_column(
        Boolean, default = True, server_default = true(), unique = True,
    )

    name: Mapped[str] = mapped_column(String(PORTFOLIO_SHORT_TEXT), default = "")
    headline: Mapped[str] = mapped_column(
        String(PORTFOLIO_MEDIUM_TEXT), default = ""
    )
    subtitle: Mapped[str | None] = mapped_column(
        String(PORTFOLIO_SHORT_TEXT), default = None
    )
    location: Mapped[str | None] = mapped_column(
        String(PORTFOLIO_SHORT_TEXT), default = None
    )
    availability: Mapped[str | None] = mapped_column(
        String(PORTFOLIO_SHORT_TEXT), default = None
    )
    bio: Mapped[str | None] = mapped_column(Text, default = None)
    email: Mapped[str | None] = mapped_column(
        String(EMAIL_MAX_LENGTH), default = None
    )
    avatar_media_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("portfolio_media.id", ondelete = "SET NULL"), default = None,
    )
    eyebrow_left: Mapped[str | None] = mapped_column(
        String(PORTFOLIO_SHORT_TEXT), default = None
    )
    eyebrow_right: Mapped[str | None] = mapped_column(
        String(PORTFOLIO_SHORT_TEXT), default = None
    )
    meta_items: Mapped[list[str]] = mapped_column(JSONB, default = list)
    section_titles: Mapped[dict[str, str]] = mapped_column(JSONB, default = dict)


class SiteSettings(Base, UUIDMixin, TimestampMixin):
    """
    Singleton site metadata and theme configuration.
    """
    __tablename__ = "portfolio_settings"
    __table_args__ = (
        CheckConstraint("singleton_key = true", name = "singleton_key_true"),
    )

    singleton_key: Mapped[bool] = mapped_column(
        Boolean, default = True, server_default = true(), unique = True,
    )

    site_title: Mapped[str] = mapped_column(
        String(PORTFOLIO_SHORT_TEXT), default = "Portfolio"
    )
    meta_description: Mapped[str | None] = mapped_column(
        String(PORTFOLIO_MEDIUM_TEXT), default = None
    )
    favicon_media_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("portfolio_media.id", ondelete = "SET NULL"), default = None,
    )

    color_bg: Mapped[str] = mapped_column(
        String(COLOR_MAX_LENGTH), default = "#ffffff"
    )
    color_surface: Mapped[str] = mapped_column(
        String(COLOR_MAX_LENGTH), default = "#fafafa"
    )
    color_text: Mapped[str] = mapped_column(
        String(COLOR_MAX_LENGTH), default = "#18181b"
    )
    color_text_muted: Mapped[str] = mapped_column(
        String(COLOR_MAX_LENGTH), default = "#71717a"
    )
    color_accent: Mapped[str] = mapped_column(
        String(COLOR_MAX_LENGTH), default = "#18181b"
    )
    color_dark_bg: Mapped[str] = mapped_column(
        String(COLOR_MAX_LENGTH), default = "#18181b"
    )
    color_dark_text: Mapped[str] = mapped_column(
        String(COLOR_MAX_LENGTH), default = "#fafafa"
    )

    font_display: Mapped[str] = mapped_column(
        String(FONT_MAX_LENGTH), default = "Georgia, serif"
    )
    font_body: Mapped[str] = mapped_column(
        String(FONT_MAX_LENGTH),
        default = "system-ui, -apple-system, sans-serif",
    )
    font_mono: Mapped[str] = mapped_column(
        String(FONT_MAX_LENGTH), default = "ui-monospace, monospace"
    )
    dark_mode: Mapped[bool] = mapped_column(default = False)
    theme_extra: Mapped[dict[str, str]] = mapped_column(JSONB, default = dict)


class Certification(Base, UUIDMixin, TimestampMixin):
    """
    A certification list item.
    """
    __tablename__ = "portfolio_certifications"

    name: Mapped[str] = mapped_column(String(PORTFOLIO_SHORT_TEXT))
    code: Mapped[str | None] = mapped_column(
        String(PORTFOLIO_META_TEXT), default = None
    )
    issuer: Mapped[str | None] = mapped_column(
        String(PORTFOLIO_SHORT_TEXT), default = None
    )
    status: Mapped[ItemStatus] = mapped_column(
        SafeEnum(ItemStatus, unknown_value = ItemStatus.PLANNED),
        default = ItemStatus.PLANNED,
    )
    issue_date: Mapped[str | None] = mapped_column(
        String(PORTFOLIO_TINY_TEXT), default = None
    )
    credential_url: Mapped[str | None] = mapped_column(
        String(URL_MAX_LENGTH), default = None
    )
    badge_media_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("portfolio_media.id", ondelete = "SET NULL"), default = None,
    )
    display_order: Mapped[int] = mapped_column(
        Integer, default = 0, index = True
    )


class Project(Base, UUIDMixin, TimestampMixin):
    """
    A project list item.
    """
    __tablename__ = "portfolio_projects"

    title: Mapped[str] = mapped_column(String(PORTFOLIO_SHORT_TEXT))
    description: Mapped[str | None] = mapped_column(Text, default = None)
    status: Mapped[ItemStatus] = mapped_column(
        SafeEnum(ItemStatus, unknown_value = ItemStatus.PLANNED),
        default = ItemStatus.PLANNED,
    )
    tags: Mapped[list[str]] = mapped_column(JSONB, default = list)
    repo_url: Mapped[str | None] = mapped_column(
        String(URL_MAX_LENGTH), default = None
    )
    live_url: Mapped[str | None] = mapped_column(
        String(URL_MAX_LENGTH), default = None
    )
    image_media_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("portfolio_media.id", ondelete = "SET NULL"), default = None,
    )
    display_order: Mapped[int] = mapped_column(
        Integer, default = 0, index = True
    )


class Experience(Base, UUIDMixin, TimestampMixin):
    """
    A work or training experience list item.
    """
    __tablename__ = "portfolio_experience"

    role: Mapped[str] = mapped_column(String(PORTFOLIO_SHORT_TEXT))
    company: Mapped[str | None] = mapped_column(
        String(PORTFOLIO_SHORT_TEXT), default = None
    )
    dates: Mapped[str | None] = mapped_column(
        String(PORTFOLIO_META_TEXT), default = None
    )
    bullets: Mapped[list[str]] = mapped_column(JSONB, default = list)
    display_order: Mapped[int] = mapped_column(
        Integer, default = 0, index = True
    )


class SkillGroup(Base, UUIDMixin, TimestampMixin):
    """
    A labelled group of skills.
    """
    __tablename__ = "portfolio_skill_groups"

    label: Mapped[str] = mapped_column(String(PORTFOLIO_SHORT_TEXT))
    items: Mapped[list[str]] = mapped_column(JSONB, default = list)
    display_order: Mapped[int] = mapped_column(
        Integer, default = 0, index = True
    )


class Link(Base, UUIDMixin, TimestampMixin):
    """
    A generic external or file-backed link.
    """
    __tablename__ = "portfolio_links"

    label: Mapped[str] = mapped_column(String(PORTFOLIO_SHORT_TEXT))
    url: Mapped[str | None] = mapped_column(
        String(URL_MAX_LENGTH), default = None
    )
    media_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("portfolio_media.id", ondelete = "SET NULL"), default = None,
    )
    icon: Mapped[str | None] = mapped_column(
        String(PORTFOLIO_TINY_TEXT), default = None
    )
    display_order: Mapped[int] = mapped_column(
        Integer, default = 0, index = True
    )


class CustomSection(Base, UUIDMixin, TimestampMixin):
    """
    A free-form section for arbitrary content.
    """
    __tablename__ = "portfolio_custom_sections"

    title: Mapped[str] = mapped_column(String(PORTFOLIO_SHORT_TEXT))
    subtitle: Mapped[str | None] = mapped_column(
        String(PORTFOLIO_SHORT_TEXT), default = None
    )
    body: Mapped[str | None] = mapped_column(Text, default = None)
    items: Mapped[list[str]] = mapped_column(JSONB, default = list)
    display_order: Mapped[int] = mapped_column(
        Integer, default = 0, index = True
    )


class Media(Base, UUIDMixin, TimestampMixin):
    """
    An uploaded file stored on disk.
    """
    __tablename__ = "portfolio_media"

    original_filename: Mapped[str] = mapped_column(
        String(MEDIA_FILENAME_MAX_LENGTH)
    )
    content_type: Mapped[str] = mapped_column(
        String(MEDIA_CONTENT_TYPE_MAX_LENGTH)
    )
    byte_size: Mapped[int] = mapped_column(Integer)
    storage_filename: Mapped[str] = mapped_column(
        String(MEDIA_FILENAME_MAX_LENGTH), unique = True, index = True
    )
