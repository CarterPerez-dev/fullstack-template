"""
© AngelaMos | 2026
admin_routes.py
"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, UploadFile, status

from config import UserRole
from core.dependencies import RequireRole
from core.responses import AUTH_401, FORBIDDEN_403, NOT_FOUND_404
from user.User import User
from .dependencies import MediaServiceDep, PortfolioServiceDep
from .repository import (
    CertificationRepository,
    CustomSectionRepository,
    ExperienceRepository,
    LinkRepository,
    ProjectRepository,
    SkillGroupRepository,
)
from .schemas import (
    CertificationCreate,
    CertificationResponse,
    CertificationUpdate,
    CustomSectionCreate,
    CustomSectionResponse,
    CustomSectionUpdate,
    ExperienceCreate,
    ExperienceResponse,
    ExperienceUpdate,
    LinkCreate,
    LinkResponse,
    LinkUpdate,
    MediaResponse,
    ProfileResponse,
    ProfileUpdate,
    ProjectCreate,
    ProjectResponse,
    ProjectUpdate,
    ReorderRequest,
    SiteSettingsResponse,
    SiteSettingsUpdate,
    SkillGroupCreate,
    SkillGroupResponse,
    SkillGroupUpdate,
)


router = APIRouter(prefix = "/admin/portfolio", tags = ["portfolio-admin"])

AdminOnly = Annotated[User, Depends(RequireRole(UserRole.ADMIN))]

ADMIN_RESPONSES = {**AUTH_401, **FORBIDDEN_403}
ADMIN_ITEM_RESPONSES = {**AUTH_401, **FORBIDDEN_403, **NOT_FOUND_404}


@router.patch(
    "/profile",
    response_model = ProfileResponse,
    responses = ADMIN_RESPONSES,
)
async def update_profile(
    portfolio_service: PortfolioServiceDep,
    _: AdminOnly,
    data: ProfileUpdate,
) -> ProfileResponse:
    """
    Update the profile singleton
    """
    return await portfolio_service.update_profile(data)


@router.patch(
    "/settings",
    response_model = SiteSettingsResponse,
    responses = ADMIN_RESPONSES,
)
async def update_settings(
    portfolio_service: PortfolioServiceDep,
    _: AdminOnly,
    data: SiteSettingsUpdate,
) -> SiteSettingsResponse:
    """
    Update the site settings singleton
    """
    return await portfolio_service.update_settings(data)


@router.get(
    "/certifications",
    response_model = list[CertificationResponse],
    responses = ADMIN_RESPONSES,
)
async def list_certifications(
    portfolio_service: PortfolioServiceDep,
    _: AdminOnly,
) -> list[CertificationResponse]:
    """
    List certifications
    """
    return await portfolio_service.list_items(
        CertificationRepository, CertificationResponse
    )


@router.post(
    "/certifications",
    response_model = CertificationResponse,
    status_code = status.HTTP_201_CREATED,
    responses = ADMIN_RESPONSES,
)
async def create_certification(
    portfolio_service: PortfolioServiceDep,
    _: AdminOnly,
    data: CertificationCreate,
) -> CertificationResponse:
    """
    Create a certification
    """
    return await portfolio_service.create_item(
        CertificationRepository, CertificationResponse, data
    )


@router.patch(
    "/certifications/{item_id}",
    response_model = CertificationResponse,
    responses = ADMIN_ITEM_RESPONSES,
)
async def update_certification(
    portfolio_service: PortfolioServiceDep,
    _: AdminOnly,
    item_id: UUID,
    data: CertificationUpdate,
) -> CertificationResponse:
    """
    Update a certification
    """
    return await portfolio_service.update_item(
        CertificationRepository,
        CertificationResponse,
        item_id,
        data,
        "Certification",
    )


@router.delete(
    "/certifications/{item_id}",
    status_code = status.HTTP_204_NO_CONTENT,
    responses = ADMIN_ITEM_RESPONSES,
)
async def delete_certification(
    portfolio_service: PortfolioServiceDep,
    _: AdminOnly,
    item_id: UUID,
) -> None:
    """
    Delete a certification
    """
    await portfolio_service.delete_item(
        CertificationRepository, item_id, "Certification"
    )


@router.post(
    "/certifications/reorder",
    status_code = status.HTTP_204_NO_CONTENT,
    responses = ADMIN_RESPONSES,
)
async def reorder_certifications(
    portfolio_service: PortfolioServiceDep,
    _: AdminOnly,
    data: ReorderRequest,
) -> None:
    """
    Reorder certifications
    """
    await portfolio_service.reorder_items(
        CertificationRepository, data.ordered_ids
    )


@router.get(
    "/projects",
    response_model = list[ProjectResponse],
    responses = ADMIN_RESPONSES,
)
async def list_projects(
    portfolio_service: PortfolioServiceDep,
    _: AdminOnly,
) -> list[ProjectResponse]:
    """
    List projects
    """
    return await portfolio_service.list_items(
        ProjectRepository, ProjectResponse
    )


@router.post(
    "/projects",
    response_model = ProjectResponse,
    status_code = status.HTTP_201_CREATED,
    responses = ADMIN_RESPONSES,
)
async def create_project(
    portfolio_service: PortfolioServiceDep,
    _: AdminOnly,
    data: ProjectCreate,
) -> ProjectResponse:
    """
    Create a project
    """
    return await portfolio_service.create_item(
        ProjectRepository, ProjectResponse, data
    )


@router.patch(
    "/projects/{item_id}",
    response_model = ProjectResponse,
    responses = ADMIN_ITEM_RESPONSES,
)
async def update_project(
    portfolio_service: PortfolioServiceDep,
    _: AdminOnly,
    item_id: UUID,
    data: ProjectUpdate,
) -> ProjectResponse:
    """
    Update a project
    """
    return await portfolio_service.update_item(
        ProjectRepository, ProjectResponse, item_id, data, "Project"
    )


@router.delete(
    "/projects/{item_id}",
    status_code = status.HTTP_204_NO_CONTENT,
    responses = ADMIN_ITEM_RESPONSES,
)
async def delete_project(
    portfolio_service: PortfolioServiceDep,
    _: AdminOnly,
    item_id: UUID,
) -> None:
    """
    Delete a project
    """
    await portfolio_service.delete_item(ProjectRepository, item_id, "Project")


@router.post(
    "/projects/reorder",
    status_code = status.HTTP_204_NO_CONTENT,
    responses = ADMIN_RESPONSES,
)
async def reorder_projects(
    portfolio_service: PortfolioServiceDep,
    _: AdminOnly,
    data: ReorderRequest,
) -> None:
    """
    Reorder projects
    """
    await portfolio_service.reorder_items(ProjectRepository, data.ordered_ids)


@router.get(
    "/experience",
    response_model = list[ExperienceResponse],
    responses = ADMIN_RESPONSES,
)
async def list_experience(
    portfolio_service: PortfolioServiceDep,
    _: AdminOnly,
) -> list[ExperienceResponse]:
    """
    List experience entries
    """
    return await portfolio_service.list_items(
        ExperienceRepository, ExperienceResponse
    )


@router.post(
    "/experience",
    response_model = ExperienceResponse,
    status_code = status.HTTP_201_CREATED,
    responses = ADMIN_RESPONSES,
)
async def create_experience(
    portfolio_service: PortfolioServiceDep,
    _: AdminOnly,
    data: ExperienceCreate,
) -> ExperienceResponse:
    """
    Create an experience entry
    """
    return await portfolio_service.create_item(
        ExperienceRepository, ExperienceResponse, data
    )


@router.patch(
    "/experience/{item_id}",
    response_model = ExperienceResponse,
    responses = ADMIN_ITEM_RESPONSES,
)
async def update_experience(
    portfolio_service: PortfolioServiceDep,
    _: AdminOnly,
    item_id: UUID,
    data: ExperienceUpdate,
) -> ExperienceResponse:
    """
    Update an experience entry
    """
    return await portfolio_service.update_item(
        ExperienceRepository, ExperienceResponse, item_id, data, "Experience"
    )


@router.delete(
    "/experience/{item_id}",
    status_code = status.HTTP_204_NO_CONTENT,
    responses = ADMIN_ITEM_RESPONSES,
)
async def delete_experience(
    portfolio_service: PortfolioServiceDep,
    _: AdminOnly,
    item_id: UUID,
) -> None:
    """
    Delete an experience entry
    """
    await portfolio_service.delete_item(
        ExperienceRepository, item_id, "Experience"
    )


@router.post(
    "/experience/reorder",
    status_code = status.HTTP_204_NO_CONTENT,
    responses = ADMIN_RESPONSES,
)
async def reorder_experience(
    portfolio_service: PortfolioServiceDep,
    _: AdminOnly,
    data: ReorderRequest,
) -> None:
    """
    Reorder experience entries
    """
    await portfolio_service.reorder_items(ExperienceRepository, data.ordered_ids)


@router.get(
    "/skill-groups",
    response_model = list[SkillGroupResponse],
    responses = ADMIN_RESPONSES,
)
async def list_skill_groups(
    portfolio_service: PortfolioServiceDep,
    _: AdminOnly,
) -> list[SkillGroupResponse]:
    """
    List skill groups
    """
    return await portfolio_service.list_items(
        SkillGroupRepository, SkillGroupResponse
    )


@router.post(
    "/skill-groups",
    response_model = SkillGroupResponse,
    status_code = status.HTTP_201_CREATED,
    responses = ADMIN_RESPONSES,
)
async def create_skill_group(
    portfolio_service: PortfolioServiceDep,
    _: AdminOnly,
    data: SkillGroupCreate,
) -> SkillGroupResponse:
    """
    Create a skill group
    """
    return await portfolio_service.create_item(
        SkillGroupRepository, SkillGroupResponse, data
    )


@router.patch(
    "/skill-groups/{item_id}",
    response_model = SkillGroupResponse,
    responses = ADMIN_ITEM_RESPONSES,
)
async def update_skill_group(
    portfolio_service: PortfolioServiceDep,
    _: AdminOnly,
    item_id: UUID,
    data: SkillGroupUpdate,
) -> SkillGroupResponse:
    """
    Update a skill group
    """
    return await portfolio_service.update_item(
        SkillGroupRepository, SkillGroupResponse, item_id, data, "Skill group"
    )


@router.delete(
    "/skill-groups/{item_id}",
    status_code = status.HTTP_204_NO_CONTENT,
    responses = ADMIN_ITEM_RESPONSES,
)
async def delete_skill_group(
    portfolio_service: PortfolioServiceDep,
    _: AdminOnly,
    item_id: UUID,
) -> None:
    """
    Delete a skill group
    """
    await portfolio_service.delete_item(
        SkillGroupRepository, item_id, "Skill group"
    )


@router.post(
    "/skill-groups/reorder",
    status_code = status.HTTP_204_NO_CONTENT,
    responses = ADMIN_RESPONSES,
)
async def reorder_skill_groups(
    portfolio_service: PortfolioServiceDep,
    _: AdminOnly,
    data: ReorderRequest,
) -> None:
    """
    Reorder skill groups
    """
    await portfolio_service.reorder_items(SkillGroupRepository, data.ordered_ids)


@router.get(
    "/links",
    response_model = list[LinkResponse],
    responses = ADMIN_RESPONSES,
)
async def list_links(
    portfolio_service: PortfolioServiceDep,
    _: AdminOnly,
) -> list[LinkResponse]:
    """
    List links
    """
    return await portfolio_service.list_items(LinkRepository, LinkResponse)


@router.post(
    "/links",
    response_model = LinkResponse,
    status_code = status.HTTP_201_CREATED,
    responses = ADMIN_RESPONSES,
)
async def create_link(
    portfolio_service: PortfolioServiceDep,
    _: AdminOnly,
    data: LinkCreate,
) -> LinkResponse:
    """
    Create a link
    """
    return await portfolio_service.create_item(
        LinkRepository, LinkResponse, data
    )


@router.patch(
    "/links/{item_id}",
    response_model = LinkResponse,
    responses = ADMIN_ITEM_RESPONSES,
)
async def update_link(
    portfolio_service: PortfolioServiceDep,
    _: AdminOnly,
    item_id: UUID,
    data: LinkUpdate,
) -> LinkResponse:
    """
    Update a link
    """
    return await portfolio_service.update_item(
        LinkRepository, LinkResponse, item_id, data, "Link"
    )


@router.delete(
    "/links/{item_id}",
    status_code = status.HTTP_204_NO_CONTENT,
    responses = ADMIN_ITEM_RESPONSES,
)
async def delete_link(
    portfolio_service: PortfolioServiceDep,
    _: AdminOnly,
    item_id: UUID,
) -> None:
    """
    Delete a link
    """
    await portfolio_service.delete_item(LinkRepository, item_id, "Link")


@router.post(
    "/links/reorder",
    status_code = status.HTTP_204_NO_CONTENT,
    responses = ADMIN_RESPONSES,
)
async def reorder_links(
    portfolio_service: PortfolioServiceDep,
    _: AdminOnly,
    data: ReorderRequest,
) -> None:
    """
    Reorder links
    """
    await portfolio_service.reorder_items(LinkRepository, data.ordered_ids)


@router.get(
    "/custom-sections",
    response_model = list[CustomSectionResponse],
    responses = ADMIN_RESPONSES,
)
async def list_custom_sections(
    portfolio_service: PortfolioServiceDep,
    _: AdminOnly,
) -> list[CustomSectionResponse]:
    """
    List custom sections
    """
    return await portfolio_service.list_items(
        CustomSectionRepository, CustomSectionResponse
    )


@router.post(
    "/custom-sections",
    response_model = CustomSectionResponse,
    status_code = status.HTTP_201_CREATED,
    responses = ADMIN_RESPONSES,
)
async def create_custom_section(
    portfolio_service: PortfolioServiceDep,
    _: AdminOnly,
    data: CustomSectionCreate,
) -> CustomSectionResponse:
    """
    Create a custom section
    """
    return await portfolio_service.create_item(
        CustomSectionRepository, CustomSectionResponse, data
    )


@router.patch(
    "/custom-sections/{item_id}",
    response_model = CustomSectionResponse,
    responses = ADMIN_ITEM_RESPONSES,
)
async def update_custom_section(
    portfolio_service: PortfolioServiceDep,
    _: AdminOnly,
    item_id: UUID,
    data: CustomSectionUpdate,
) -> CustomSectionResponse:
    """
    Update a custom section
    """
    return await portfolio_service.update_item(
        CustomSectionRepository,
        CustomSectionResponse,
        item_id,
        data,
        "Custom section",
    )


@router.delete(
    "/custom-sections/{item_id}",
    status_code = status.HTTP_204_NO_CONTENT,
    responses = ADMIN_ITEM_RESPONSES,
)
async def delete_custom_section(
    portfolio_service: PortfolioServiceDep,
    _: AdminOnly,
    item_id: UUID,
) -> None:
    """
    Delete a custom section
    """
    await portfolio_service.delete_item(
        CustomSectionRepository, item_id, "Custom section"
    )


@router.post(
    "/custom-sections/reorder",
    status_code = status.HTTP_204_NO_CONTENT,
    responses = ADMIN_RESPONSES,
)
async def reorder_custom_sections(
    portfolio_service: PortfolioServiceDep,
    _: AdminOnly,
    data: ReorderRequest,
) -> None:
    """
    Reorder custom sections
    """
    await portfolio_service.reorder_items(
        CustomSectionRepository, data.ordered_ids
    )


@router.get(
    "/media",
    response_model = list[MediaResponse],
    responses = ADMIN_RESPONSES,
)
async def list_media(
    media_service: MediaServiceDep,
    _: AdminOnly,
) -> list[MediaResponse]:
    """
    List uploaded media
    """
    return await media_service.list_media()


@router.post(
    "/media",
    response_model = MediaResponse,
    status_code = status.HTTP_201_CREATED,
    responses = ADMIN_RESPONSES,
)
async def upload_media(
    media_service: MediaServiceDep,
    _: AdminOnly,
    file: Annotated[UploadFile, File()],
) -> MediaResponse:
    """
    Upload a media file
    """
    return await media_service.upload(file)


@router.delete(
    "/media/{media_id}",
    status_code = status.HTTP_204_NO_CONTENT,
    responses = ADMIN_ITEM_RESPONSES,
)
async def delete_media(
    media_service: MediaServiceDep,
    _: AdminOnly,
    media_id: UUID,
) -> None:
    """
    Delete a media file
    """
    await media_service.delete_media(media_id)
