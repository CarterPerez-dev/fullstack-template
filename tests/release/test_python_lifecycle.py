"""
©AngelaMos | 2026
test_python_lifecycle.py
"""

from asyncio import CancelledError
from unittest.mock import AsyncMock, Mock

import httpx
import pytest
from fastapi import FastAPI

from core.database import sessionmanager
from core.dependencies import DBSession
from factory import lifespan


@pytest.mark.asyncio
@pytest.mark.parametrize("commit_fails", [False, True])
async def test_database_commit_finishes_before_http_response(monkeypatch, commit_fails):
    events = []
    session = AsyncMock()
    session.__aenter__.return_value = session

    async def commit():
        events.append("commit")
        if commit_fails:
            raise RuntimeError("injected commit failure")

    session.commit.side_effect = commit
    monkeypatch.setattr(sessionmanager, "_async_sessionmaker", lambda: session)
    app = FastAPI()

    @app.post("/write", status_code=201)
    async def write(db: DBSession):
        assert db is session
        return {"saved": True}

    async def observed_app(scope, receive, send):
        async def observe(message):
            if message["type"] == "http.response.start":
                events.append(f"response:{message['status']}")
            await send(message)

        await app(scope, receive, observe)

    transport = httpx.ASGITransport(app=observed_app, raise_app_exceptions=False)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/write")

    expected_status = 500 if commit_fails else 201
    assert response.status_code == expected_status
    assert events == ["commit", f"response:{expected_status}"]
    session.commit.assert_awaited_once()
    session.__aexit__.assert_awaited_once()
    if commit_fails:
        session.rollback.assert_awaited_once()
    else:
        session.rollback.assert_not_awaited()


@pytest.mark.asyncio
@pytest.mark.parametrize("failure", [None, RuntimeError, CancelledError])
async def test_lifespan_releases_database_after_exit(monkeypatch, failure):
    initialize = Mock()
    close = AsyncMock()
    monkeypatch.setattr(sessionmanager, "init", initialize)
    monkeypatch.setattr(sessionmanager, "close", close)

    if failure is None:
        async with lifespan(FastAPI()):
            initialize.assert_called_once()
            close.assert_not_awaited()
    else:
        with pytest.raises(failure):
            async with lifespan(FastAPI()):
                raise failure("injected lifespan failure")

    close.assert_awaited_once()


@pytest.mark.asyncio
async def test_lifespan_releases_partially_initialized_database(monkeypatch):
    initialize = Mock(side_effect=RuntimeError("injected initialization failure"))
    close = AsyncMock()
    monkeypatch.setattr(sessionmanager, "init", initialize)
    monkeypatch.setattr(sessionmanager, "close", close)

    with pytest.raises(RuntimeError, match="injected initialization failure"):
        async with lifespan(FastAPI()):
            pytest.fail("The application started after initialization failed")

    close.assert_awaited_once()
