"""
© AngelaMos | 2026
schemas.py
"""

from uuid import UUID

from pydantic import Field

from config import ItemStatus
from core.base_schema import BaseResponseSchema, BaseSchema


class ProfileUpdate(BaseSchema):
    """
    Partial update for the profile singleton.
    """
    name: str | None = None
    headline: str | None = None
    subtitle: str | None = None
    location: str | None = None
    availability: str | None = None
    bio: str | None = None
    email: str | None = None
    avatar_media_id: UUID | None = None
    eyebrow_left: str | None = None
    eyebrow_right: str | None = None
    meta_items: list[str] | None = None
    section_titles: dict[str, str] | None = None


class ProfileResponse(BaseResponseSchema):
    """
    Profile singleton response.
    """
    name: str
    headline: str
    subtitle: str | None
    location: str | None
    availability: str | None
    bio: str | None
    email: str | None
    avatar_media_id: UUID | None
    eyebrow_left: str | None
    eyebrow_right: str | None
    meta_items: list[str]
    section_titles: dict[str, str]


class SiteSettingsUpdate(BaseSchema):
    """
    Partial update for the site settings singleton.
    """
    site_title: str | None = None
    meta_description: str | None = None
    favicon_media_id: UUID | None = None
    color_bg: str | None = None
    color_surface: str | None = None
    color_text: str | None = None
    color_text_muted: str | None = None
    color_accent: str | None = None
    color_dark_bg: str | None = None
    color_dark_text: str | None = None
    font_display: str | None = None
    font_body: str | None = None
    font_mono: str | None = None
    dark_mode: bool | None = None
    theme_extra: dict[str, str] | None = None


class SiteSettingsResponse(BaseResponseSchema):
    """
    Site settings singleton response.
    """
    site_title: str
    meta_description: str | None
    favicon_media_id: UUID | None
    color_bg: str
    color_surface: str
    color_text: str
    color_text_muted: str
    color_accent: str
    color_dark_bg: str
    color_dark_text: str
    font_display: str
    font_body: str
    font_mono: str
    dark_mode: bool
    theme_extra: dict[str, str]


class CertificationCreate(BaseSchema):
    """
    Create a certification.
    """
    name: str
    code: str | None = None
    issuer: str | None = None
    status: ItemStatus = ItemStatus.PLANNED
    issue_date: str | None = None
    credential_url: str | None = None
    badge_media_id: UUID | None = None
    display_order: int = 0


class CertificationUpdate(BaseSchema):
    """
    Partial update for a certification.
    """
    name: str | None = None
    code: str | None = None
    issuer: str | None = None
    status: ItemStatus | None = None
    issue_date: str | None = None
    credential_url: str | None = None
    badge_media_id: UUID | None = None
    display_order: int | None = None


class CertificationResponse(BaseResponseSchema):
    """
    Certification response.
    """
    name: str
    code: str | None
    issuer: str | None
    status: ItemStatus
    issue_date: str | None
    credential_url: str | None
    badge_media_id: UUID | None
    display_order: int


class ProjectCreate(BaseSchema):
    """
    Create a project.
    """
    title: str
    description: str | None = None
    status: ItemStatus = ItemStatus.PLANNED
    tags: list[str] = Field(default_factory = list)
    repo_url: str | None = None
    live_url: str | None = None
    image_media_id: UUID | None = None
    display_order: int = 0


class ProjectUpdate(BaseSchema):
    """
    Partial update for a project.
    """
    title: str | None = None
    description: str | None = None
    status: ItemStatus | None = None
    tags: list[str] | None = None
    repo_url: str | None = None
    live_url: str | None = None
    image_media_id: UUID | None = None
    display_order: int | None = None


class ProjectResponse(BaseResponseSchema):
    """
    Project response.
    """
    title: str
    description: str | None
    status: ItemStatus
    tags: list[str]
    repo_url: str | None
    live_url: str | None
    image_media_id: UUID | None
    display_order: int


class ExperienceCreate(BaseSchema):
    """
    Create an experience entry.
    """
    role: str
    company: str | None = None
    dates: str | None = None
    bullets: list[str] = Field(default_factory = list)
    display_order: int = 0


class ExperienceUpdate(BaseSchema):
    """
    Partial update for an experience entry.
    """
    role: str | None = None
    company: str | None = None
    dates: str | None = None
    bullets: list[str] | None = None
    display_order: int | None = None


class ExperienceResponse(BaseResponseSchema):
    """
    Experience response.
    """
    role: str
    company: str | None
    dates: str | None
    bullets: list[str]
    display_order: int


class SkillGroupCreate(BaseSchema):
    """
    Create a skill group.
    """
    label: str
    items: list[str] = Field(default_factory = list)
    display_order: int = 0


class SkillGroupUpdate(BaseSchema):
    """
    Partial update for a skill group.
    """
    label: str | None = None
    items: list[str] | None = None
    display_order: int | None = None


class SkillGroupResponse(BaseResponseSchema):
    """
    Skill group response.
    """
    label: str
    items: list[str]
    display_order: int


class LinkCreate(BaseSchema):
    """
    Create a link.
    """
    label: str
    url: str | None = None
    media_id: UUID | None = None
    icon: str | None = None
    display_order: int = 0


class LinkUpdate(BaseSchema):
    """
    Partial update for a link.
    """
    label: str | None = None
    url: str | None = None
    media_id: UUID | None = None
    icon: str | None = None
    display_order: int | None = None


class LinkResponse(BaseResponseSchema):
    """
    Link response.
    """
    label: str
    url: str | None
    media_id: UUID | None
    icon: str | None
    display_order: int


class CustomSectionCreate(BaseSchema):
    """
    Create a custom section.
    """
    title: str
    subtitle: str | None = None
    body: str | None = None
    items: list[str] = Field(default_factory = list)
    display_order: int = 0


class CustomSectionUpdate(BaseSchema):
    """
    Partial update for a custom section.
    """
    title: str | None = None
    subtitle: str | None = None
    body: str | None = None
    items: list[str] | None = None
    display_order: int | None = None


class CustomSectionResponse(BaseResponseSchema):
    """
    Custom section response.
    """
    title: str
    subtitle: str | None
    body: str | None
    items: list[str]
    display_order: int


class MediaResponse(BaseResponseSchema):
    """
    Uploaded media metadata response.
    """
    original_filename: str
    content_type: str
    byte_size: int


class ReorderRequest(BaseSchema):
    """
    Reorder a list resource by supplying ids in the desired order.
    """
    ordered_ids: list[UUID]


class RegistrationStatusResponse(BaseSchema):
    """
    Whether the owner account can still be claimed.
    """
    registration_open: bool


class PortfolioResponse(BaseSchema):
    """
    Aggregated public portfolio payload.
    """
    profile: ProfileResponse
    settings: SiteSettingsResponse
    certifications: list[CertificationResponse]
    projects: list[ProjectResponse]
    experience: list[ExperienceResponse]
    skill_groups: list[SkillGroupResponse]
    links: list[LinkResponse]
    custom_sections: list[CustomSectionResponse]
