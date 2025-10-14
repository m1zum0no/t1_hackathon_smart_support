import asyncio
import secrets
import string

from fastapi import status
from httpx import AsyncClient, Response
from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import User
from src.utils import get_hashed_password, verify_password


# Authenticate user based on username/email and password
async def authenticate_user(db_session: AsyncSession, login_identifier: str, password: str) -> User | None:
    # Introduce a small delay to mitigate user enumeration attacks
    await asyncio.sleep(0.1)

    user: User | None = await get_user_by_login_identifier(db_session, login_identifier=login_identifier)

    if not user:
        return None

    # if user is found check password
    if not verify_password(plain_password=password, hashed_password=user.password):
        return None

    return user


async def get_user_by_login_identifier(db_session: AsyncSession, *, login_identifier: str) -> User | None:
    query = select(User).where(or_(User.email == login_identifier, User.username == login_identifier))
    result = await db_session.execute(query)
    user: User | None = result.scalar_one_or_none()

    return user


async def get_user_by_email(db_session: AsyncSession, *, email: str) -> User | None:
    query = select(User).where(and_(User.email == email, User.is_deleted.is_(False)))
    result = await db_session.execute(query)
    user: User | None = result.scalar_one_or_none()

    return user




async def update_user_last_login(db_session: AsyncSession, *, user: User) -> None:
    user.last_login = func.now()
    await db_session.commit()
