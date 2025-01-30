from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.core.hashing import verify_password
from app.models.roles import RolePrivilege
from app.schemas.tokens import Token
from app.schemas.users import UserCreate, UserLogin, UserResponse, UserUpdate
from app.utils.users import (
    activate_user,
    create_access_token,
    create_user,
    deactivate_user,
    get_user_by_email,
    get_user_by_id,
    get_users,
    require_roles,
    update_user,
)

router = APIRouter(prefix="/users", tags=["users"])


@router.get(
    "/",
    response_model=list[UserResponse],
    dependencies=[
        Depends(
            require_roles(
                [
                    RolePrivilege.ANY,
                ]
            )
        )
    ],
)
async def get_users_api(db: Annotated[AsyncSession, Depends(get_db_session)]):
    return await get_users(db)


@router.post("/", response_model=UserResponse)
async def create_user_api(
    user: UserCreate,
    db: Annotated[AsyncSession, Depends(get_db_session)],
):
    return await create_user(db, user)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    dependencies=[
        Depends(
            require_roles(
                [
                    RolePrivilege.ANY,
                ]
            )
        )
    ],
)
async def get_user_api(user_id: int, db: Annotated[AsyncSession, Depends(get_db_session)]):
    return await get_user_by_id(db, user_id)


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    dependencies=[
        Depends(
            require_roles(
                [
                    RolePrivilege.EDITOR,
                ]
            )
        )
    ],
)
async def put_user_api(user_id: int, user: UserUpdate, db: Annotated[AsyncSession, Depends(get_db_session)]):
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return await update_user(db, user_id, user)


@router.put(
    "/activate/{user_id}",
    response_model=UserResponse,
    dependencies=[
        Depends(
            require_roles(
                [
                    RolePrivilege.ADMIN,
                ]
            )
        )
    ],
)
async def activate_user_api(user_id: int, db: Annotated[AsyncSession, Depends(get_db_session)]):
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return await activate_user(db, user)


@router.put(
    "/deactivate/{user_id}",
    response_model=UserResponse,
    dependencies=[
        Depends(
            require_roles(
                [
                    RolePrivilege.ADMIN,
                ]
            )
        )
    ],
)
async def deactivate_user_api(user_id: int, db: Annotated[AsyncSession, Depends(get_db_session)]):
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return await deactivate_user(db, user)


@router.post("/login")
async def login_api(
    user: UserLogin,
    db: Annotated[AsyncSession, Depends(get_db_session)],
):
    user_ = await get_user_by_email(db, user.email)
    if not user_:
        raise HTTPException(status_code=404, detail="User not found")
    if user_.is_active is False:
        raise HTTPException(status_code=400, detail="Inactive user")
    if not verify_password(user.password, user_.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    access_token = create_access_token(user_)
    return Token(access_token=access_token)
