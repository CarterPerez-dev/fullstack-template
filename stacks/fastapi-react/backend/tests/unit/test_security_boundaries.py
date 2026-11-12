"""
©AngelaMos | 2026
test_security_boundaries.py
"""

import jwt
import pytest
from httpx import AsyncClient
from starlette.requests import Request

from config import settings
from core.rate_limit import get_identifier


@pytest.mark.parametrize("subject", ["first", "second"])
def test_unverified_token_cannot_choose_rate_limit_bucket(subject: str) -> None:
    token = jwt.encode(
        {"sub": subject},
        "untrusted-test-key-with-32-characters",
        algorithm = "HS256"
    )
    request = Request(
        {
            "type": "http",
            "client": ("198.51.100.7",
                       12345),
            "headers": [(b"authorization",
                         f"Bearer {token}".encode())],
        }
    )
    assert get_identifier(request) == "198.51.100.7"


@pytest.mark.asyncio
async def test_public_signup_cannot_claim_admin_email(
    client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "ADMIN_EMAIL", "owner@example.com")
    response = await client.post(
        "/v1/users",
        json = {
            "email": "owner@example.com",
            "password": "RegistrationFixture123",
        }
    )
    assert response.status_code == 201
    assert response.json()["role"] == "user"
