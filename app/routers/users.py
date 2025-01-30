from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.core.hashing import verify_password
from app.models.roles import RolePrivilege
from app.schemas.tokens import Token
from app.schemas.users import UserCreate, UserLogin, UserResponse, UserUpdate
from app.utils.exceptions import BadRedquestException, NotFoundException, UnauthorizedException
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
    summary="List all users",
    description="Retrieve a list of all users. Requires ANY role privilege.",
    response_description="A list of user objects.",
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


@router.post(
    "/",
    response_model=UserResponse,
    summary="Create a new user",
    description="Create a new user with the provided details.",
    response_description="The created user object.",
)
async def create_user_api(
    user: UserCreate,
    db: Annotated[AsyncSession, Depends(get_db_session)],
):
    return await create_user(db, user)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get a user by ID",
    description="Retrieve a specific user by their ID. Requires ANY role privilege.",
    response_description="The requested user object.",
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
    summary="Update a user",
    description="Update an existing user's details. Requires EDITOR role privilege.",
    response_description="The updated user object.",
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
        raise NotFoundException(detail="User not found")
    return await update_user(db, user_id, user)


@router.put(
    "/activate/{user_id}",
    response_model=UserResponse,
    summary="Activate a user",
    description="Activate a deactivated user. Requires ADMIN role privilege.",
    response_description="The activated user object.",
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
        raise NotFoundException(detail="User not found")
    return await activate_user(db, user)


@router.put(
    "/deactivate/{user_id}",
    response_model=UserResponse,
    summary="Deactivate a user",
    description="Deactivate an active user. Requires ADMIN role privilege.",
    response_description="The deactivated user object.",
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
        raise NotFoundException(detail="User not found")
    return await deactivate_user(db, user)


@router.post(
    "/login",
    response_model=Token,
    summary="User login",
    description="Authenticate a user and generate an access token.",
    response_description="An access token for the authenticated user.",
)
async def login_api(
    user_data: UserLogin,
    db: Annotated[AsyncSession, Depends(get_db_session)],
):
    user = await get_user_by_email(db, user_data.email)
    if not user:
        raise NotFoundException(detail="User not found")
    if user.is_active is False:
        raise BadRedquestException(detail="User account is not active")
    if not verify_password(user_data.password, user.password):
        raise UnauthorizedException(detail="Invalid credentials")
    access_token = create_access_token(user)
    return Token(access_token=access_token)
