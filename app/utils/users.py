import os
from datetime import UTC, datetime, timedelta
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.database import get_db_session
from app.core.hashing import get_password_hash
from app.models.roles import RolePrivilege
from app.models.users import User
from app.schemas.tokens import TokenData
from app.schemas.users import UserCreate, UserUpdate
from app.utils.exceptions import ForbiddenException, UnauthorizedException

SECRET_KEY = os.environ["SECRET_KEY"]
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
API_TOKEN_HEADER = HTTPBearer()


def set_user_model(user: UserCreate) -> User:
    return User(
        username=user.username,
        email=user.email,
        password=get_password_hash(user.password),
        is_active=False,
    )


async def create_user(db: AsyncSession, user: UserCreate) -> User:
    new_user = set_user_model(user)
    db.add(new_user)
    try:
        await db.commit()
        await db.refresh(new_user)
        return new_user
    except IntegrityError as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Invalid email") from e


async def update_user(db: AsyncSession, user_id: int, user: UserUpdate) -> User:
    password = get_password_hash(user.password)
    user.username = user.username
    user.password = password
    await db.commit()
    await db.refresh(user)
    return user


async def activate_user(db: AsyncSession, user: User) -> User:
    user.is_active = True
    await db.commit()
    await db.refresh(user)
    return user


async def deactivate_user(db: AsyncSession, user: User) -> User:
    user.is_active = False
    await db.commit()
    await db.refresh(user)
    return user


async def get_user_by_email(db: AsyncSession, email: str) -> User:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: int) -> User:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def get_users(db: AsyncSession) -> User:
    result = await db.execute(select(User))
    return result.scalars().all()


async def get_current_user(
    credentials: Annotated[HTTPBearer, Depends(API_TOKEN_HEADER)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> User:
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        token_data = TokenData(**payload)
        print(token_data)
        if token_data.email is None:
            raise UnauthorizedException()
        print(token_data.email)
    except jwt.InvalidTokenError as e:
        raise UnauthorizedException() from e
    user = await get_user_by_email(db, token_data.email)
    if user is None:
        raise UnauthorizedException()
    return user


def create_access_token(user: User) -> str:
    to_encode = {"id": user.id, "email": user.email, "username": user.username}
    expire = datetime.now(UTC) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def require_roles(allowed_roles: list[RolePrivilege]) -> User:
    """
    Enforces role-based access control for API endpoints

    Args:
        allowed_roles: One or more RolePrivilege granting access.
    """

    def role_permission_check(current_user: Annotated[User, Depends(get_current_user)]):
        if RolePrivilege.ANY in allowed_roles:
            return current_user
        if current_user.role_id not in allowed_roles:
            raise ForbiddenException()
        return current_user

    return role_permission_check
