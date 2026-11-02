"""
ⒸAngelaMos | 2025
rate_limit.py
"""

from slowapi import Limiter
from slowapi.util import get_remote_address
from starlette.requests import Request

from config import settings


def get_identifier(request: Request) -> str:
    """
    Use the connection identity before authentication has established a user.
    """
    return get_remote_address(request)


limiter = Limiter(
    key_func = get_identifier,
    storage_uri = str(settings.REDIS_URL) if settings.REDIS_URL else None,
    default_limits = [settings.RATE_LIMIT_DEFAULT],
    headers_enabled = True,
    in_memory_fallback_enabled = True,
)
