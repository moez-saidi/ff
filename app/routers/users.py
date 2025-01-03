from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.core.jwt import create_access_token
from app.schemas.tokens import Token
from app.schemas.users import UserCreate, UserLogin, UserResponse, UserUpdate
from app.utils.users import activate_user, authenticate_user, create_user, update_user

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/create", response_model=UserResponse)
async def create_new_user(user: UserCreate, db: AsyncSession = Depends(get_db_session)):  # noqa: B008
    return await create_user(db, user)


@router.put("/update/{user_id}", response_model=UserResponse)
async def update_existing_user(user_id: int, user: UserUpdate, db: AsyncSession = Depends(get_db_session)):  # noqa: B008
    return await update_user(db, user_id, user)


@router.post("/activate/{user_id}", response_model=UserResponse)
async def activate_existing_user(user_id: int, db: AsyncSession = Depends(get_db_session)):  # noqa: B008
    return await activate_user(db, user_id)


@router.post("/login")
async def login(user: UserLogin, db: AsyncSession = Depends(get_db_session)):  # noqa: B008
    user_ = await authenticate_user(db, user)
    if not user_:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    access_token = create_access_token(user_)
    return Token(access_token=access_token)
