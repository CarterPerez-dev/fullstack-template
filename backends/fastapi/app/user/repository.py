"""
ⒸAngelaMos | 2025
repository.py
"""
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from config import UserRole
from .User import User
from core.base_repository import BaseRepository
from core.exceptions import InvalidCredentials


class UserRepository(BaseRepository[User]):
    """
    Repository for User model database operations
    """
    model = User

    @classmethod
    async def get_by_email(
        cls,
        session: AsyncSession,
        email: str,
    ) -> User | None:
        """
        Get user by email address
        """
        result = await session.execute(
            select(User).where(User.email == email)
        )
        return result.scalars().first()

    @classmethod
    async def get_by_id(
        cls,
        session: AsyncSession,
        id: UUID,
    ) -> User | None:
        """
        Get user by ID
        """
        return await session.get(User, id)

    @classmethod
    async def email_exists(
        cls,
        session: AsyncSession,
        email: str,
    ) -> bool:
        """
        Check if email is already registered
        """
        result = await session.execute(
            select(User.id).where(User.email == email)
        )
        return result.scalars().first() is not None

    @classmethod
    async def create_user(
        cls,
        session: AsyncSession,
        email: str,
        hashed_password: str,
        full_name: str | None = None,
        role: UserRole = UserRole.USER,
    ) -> User:
        """
        Create a new user
        """
        user = User(
            email = email,
            hashed_password = hashed_password,
            full_name = full_name,
            role = role,
        )
        session.add(user)
        await session.flush()
        await session.refresh(user)
        return user

    @classmethod
    async def update_password(
        cls,
        session: AsyncSession,
        user: User,
        hashed_password: str,
        *,
        invalidate_sessions: bool = True,
    ) -> User:
        """
        Replace the verified password without overwriting a concurrent change.
        """
        result = await session.execute(
            update(User)
            .where(User.id == user.id, User.hashed_password == user.hashed_password)
            .values(
                hashed_password = hashed_password,
                token_version = User.token_version + int(invalidate_sessions),
            )
            .returning(User.id)
            .execution_options(synchronize_session = False)
        )
        if result.scalar_one_or_none() is None:
            raise InvalidCredentials()
        await session.refresh(user)
        return user

    @classmethod
    async def increment_token_version(
        cls,
        session: AsyncSession,
        user: User,
    ) -> User:
        """
        Invalidate all user tokens
        """
        await session.execute(
            update(User).where(User.id == user.id)
            .values(token_version = User.token_version + 1)
            .execution_options(synchronize_session = False)
        )
        await session.refresh(user)
        return user
