"""
©AngelaMos | 2026
test_python_security.py
"""

import asyncio
import os
from uuid import uuid4

import pytest
import pytest_asyncio
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from auth.RefreshToken import RefreshToken
from auth.repository import RefreshTokenRepository
from auth.service import AuthService
from core.Base import Base
from core.exceptions import InvalidCredentials, TokenRevokedError
from core.security import create_refresh_token, hash_token
from user.repository import UserRepository


@pytest_asyncio.fixture
async def sessions():
    url = os.environ.get("TEST_POSTGRES_URL")
    if not url:
        pytest.skip("TEST_POSTGRES_URL must name a disposable PostgreSQL database")
    schema = f"template_test_{uuid4().hex}"
    admin = create_async_engine(url)
    async with admin.begin() as connection:
        await connection.execute(text(f'CREATE SCHEMA "{schema}"'))
    engine = create_async_engine(
        url, connect_args={"server_settings": {"search_path": schema}},
    )
    try:
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)
        yield async_sessionmaker(engine, expire_on_commit=False)
    finally:
        await engine.dispose()
        async with admin.begin() as connection:
            await connection.execute(text(f'DROP SCHEMA "{schema}" CASCADE'))
        await admin.dispose()


async def seed_session(sessions):
    async with sessions.begin() as session:
        user = await UserRepository.create_user(
            session, email=f"{uuid4().hex}@example.com", hashed_password="unused",
        )
        family = uuid4()
        raw, digest, expires = create_refresh_token(user.id, family)
        await RefreshTokenRepository.create_token(
            session, user_id=user.id, family_id=family, token_hash=digest,
            expires_at=expires, token_version=user.token_version,
        )
        return raw, user.id, family


async def rotate(sessions, raw):
    async with sessions() as session:
        try:
            return await AuthService(session).refresh_tokens(raw)
        except Exception:
            await session.rollback()
            raise


@pytest.mark.asyncio
async def test_replay_revocation_survives_request_rollback(sessions):
    raw, _, _ = await seed_session(sessions)
    _, successor = await rotate(sessions, raw)
    with pytest.raises(TokenRevokedError):
        await rotate(sessions, raw)
    with pytest.raises(TokenRevokedError):
        await rotate(sessions, successor)


@pytest.mark.asyncio
async def test_concurrent_refresh_cannot_branch(sessions):
    raw, _, family = await seed_session(sessions)
    results = await asyncio.gather(
        rotate(sessions, raw), rotate(sessions, raw), return_exceptions=True,
    )
    assert sum(isinstance(result, tuple) for result in results) == 1
    assert sum(isinstance(result, TokenRevokedError) for result in results) == 1
    async with sessions() as session:
        tokens = list(await session.scalars(
            select(RefreshToken).where(RefreshToken.family_id == family),
        ))
        assert len(tokens) == 2
        assert all(token.is_revoked for token in tokens)


@pytest.mark.asyncio
async def test_replay_racing_descendant_revokes_entire_family(sessions):
    raw, _, family = await seed_session(sessions)
    _, successor = await rotate(sessions, raw)
    await asyncio.gather(
        rotate(sessions, raw), rotate(sessions, successor), return_exceptions=True,
    )
    async with sessions() as session:
        tokens = list(await session.scalars(
            select(RefreshToken).where(RefreshToken.family_id == family),
        ))
        assert all(token.is_revoked for token in tokens)


@pytest.mark.asyncio
async def test_failed_successor_insert_rolls_back_consumption(sessions, monkeypatch):
    raw, _, _ = await seed_session(sessions)

    async def fail_creation(*_args, **_kwargs):
        raise RuntimeError("injected insert failure")

    monkeypatch.setattr(RefreshTokenRepository, "create_token", fail_creation)
    with pytest.raises(RuntimeError, match="injected insert failure"):
        await rotate(sessions, raw)
    async with sessions() as session:
        stored = await session.scalar(
            select(RefreshToken).where(RefreshToken.token_hash == hash_token(raw)),
        )
        assert stored is not None and not stored.is_revoked


@pytest.mark.asyncio
async def test_token_version_change_prevents_refresh_resurrection(sessions):
    raw, user_id, _ = await seed_session(sessions)
    async with sessions.begin() as session:
        user = await UserRepository.get_by_id(session, user_id)
        await UserRepository.increment_token_version(session, user)
    with pytest.raises(TokenRevokedError):
        await rotate(sessions, raw)


@pytest.mark.asyncio
async def test_logout_of_consumed_cookie_revokes_successor(sessions):
    raw, _, _ = await seed_session(sessions)
    _, successor = await rotate(sessions, raw)
    async with sessions.begin() as session:
        await AuthService(session).logout(raw)
    with pytest.raises(TokenRevokedError):
        await rotate(sessions, successor)


@pytest.mark.asyncio
async def test_password_change_blocks_stale_rehash_and_old_sessions(sessions):
    raw, user_id, _ = await seed_session(sessions)
    async with sessions() as stale_session:
        stale_user = await UserRepository.get_by_id(stale_session, user_id)
        async with sessions.begin() as session:
            user = await UserRepository.get_by_id(session, user_id)
            await UserRepository.update_password(session, user, "replacement")
            assert user.token_version == 1
        with pytest.raises(InvalidCredentials):
            await UserRepository.update_password(
                stale_session, stale_user, "stale", invalidate_sessions=False,
            )
        await stale_session.rollback()
    with pytest.raises(TokenRevokedError):
        await rotate(sessions, raw)
    async with sessions.begin() as session:
        user = await UserRepository.get_by_id(session, user_id)
        await UserRepository.update_password(
            session, user, "rehash", invalidate_sessions=False,
        )
        assert user.token_version == 1
