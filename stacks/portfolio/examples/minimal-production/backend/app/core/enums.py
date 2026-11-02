"""
ⒸAngelaMos | 2025
enums.py
"""

from enum import StrEnum


class Environment(StrEnum):
    """
    Application environment
    """
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class TokenType(StrEnum):
    """
    JWT token types
    """
    ACCESS = "access"


class HealthStatus(StrEnum):
    """
    Health check status values
    """
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"
