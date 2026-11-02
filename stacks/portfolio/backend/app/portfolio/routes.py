"""
© AngelaMos | 2026
routes.py
"""

from uuid import UUID

from fastapi import APIRouter
from fastapi.responses import FileResponse

from core.responses import NOT_FOUND_404
from .dependencies import MediaServiceDep, PortfolioServiceDep
from .schemas import PortfolioResponse, RegistrationStatusResponse


router = APIRouter(prefix = "/portfolio", tags = ["portfolio"])


@router.get("", response_model = PortfolioResponse)
async def get_portfolio(
    portfolio_service: PortfolioServiceDep,
) -> PortfolioResponse:
    """
    Public aggregated portfolio content
    """
    return await portfolio_service.get_portfolio()


@router.get(
    "/registration-status",
    response_model = RegistrationStatusResponse,
)
async def registration_status(
    portfolio_service: PortfolioServiceDep,
) -> RegistrationStatusResponse:
    """
    Public enrollment policy
    """
    return await portfolio_service.registration_status()


media_router = APIRouter(prefix = "/media", tags = ["media"])


@media_router.get(
    "/{media_id}/raw",
    responses = {**NOT_FOUND_404},
)
async def get_media_raw(
    media_service: MediaServiceDep,
    media_id: UUID,
) -> FileResponse:
    """
    Stream a stored media file
    """
    media = await media_service.get_media(media_id)
    path = media_service.media_path(media)
    return FileResponse(
        path = path,
        media_type = media.content_type,
        filename = media.original_filename,
        headers = {
            "X-Content-Type-Options": "nosniff",
            "Content-Security-Policy": "sandbox; default-src 'none'",
        },
    )
