from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.hashing import get_password_hash, verify_password
from app.models.users import User
from app.schemas.users import UserCreate, UserLogin, UserUpdate


async def create_user(db: AsyncSession, user: UserCreate) -> User:
    hashed_password = get_password_hash(user.password)
    new_user = User(email=user.email, username=user.username, hashed_password=hashed_password, is_active=False)
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


async def activate_user(db: AsyncSession, user_id: int) -> User:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = True
    await db.commit()
    await db.refresh(user)
    return user


async def authenticate_user(db: AsyncSession, user: UserLogin) -> User:
    result = await db.execute(select(User).where(User.email == user.email))
    db_user = result.scalars().first()
    if not user or not verify_password(user.password, db_user.hashed_password):
        return None
    return db_user
