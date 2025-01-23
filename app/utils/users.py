from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.hashing import get_password_hash
from app.models.users import User
from app.schemas.users import UserCreate, UserUpdate


def set_user_model(user: UserCreate) -> User:
    return User(
        username=user.username,
        email=user.email,
        hashed_password=get_password_hash(user.password),
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
    hashed_password = get_password_hash(user.password)
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.username = user.username
    user.hashed_password = hashed_password
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
    return result.scalars().first()


async def get_user_by_id(db: AsyncSession, user_id: int) -> User:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalars().first()


async def get_users(db: AsyncSession) -> User:
    result = await db.execute(select(User))
    return result.scalars().all()
