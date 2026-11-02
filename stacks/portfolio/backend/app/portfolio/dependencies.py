"""
© AngelaMos | 2026
dependencies.py
"""

from typing import Annotated

from fastapi import Depends

from core.dependencies import DBSession
from .service import MediaService, PortfolioService


def get_portfolio_service(db: DBSession) -> PortfolioService:
    """
    Dependency to inject PortfolioService instance
    """
    return PortfolioService(db)


def get_media_service(db: DBSession) -> MediaService:
    """
    Dependency to inject MediaService instance
    """
    return MediaService(db)


PortfolioServiceDep = Annotated[PortfolioService, Depends(get_portfolio_service)]
MediaServiceDep = Annotated[MediaService, Depends(get_media_service)]
