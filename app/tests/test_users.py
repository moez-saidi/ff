import random
import string

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.users import User


@pytest.mark.asyncio
async def test_create_user(client: AsyncClient, db_session: AsyncSession) -> None:
    user_data = {
        "username": "Momo",
        "email": "user@example.com",
        "password": "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10)),
    }
    response = await client.post("/users/", json=user_data)
    assert response.status_code == 200
    db_user = await db_session.execute(select(User).where(User.email == user_data["email"]))
    db_user = db_user.scalar_one_or_none()

    assert db_user is not None
    assert db_user.username == user_data["username"]
    assert db_user.email == user_data["email"]


@pytest.mark.asyncio
async def test_list_users(client: AsyncClient, create_test_users):
    test_users = await create_test_users(4)
    response = await client.get("/users/")
    assert response.status_code == 200
    users = response.json()
    assert isinstance(users, list)
    assert len(users) == len(test_users)


# @pytest.mark.asyncio
# async def test_login(client: AsyncClient, create_test_users):
#     await create_test_users(1)
#     response = await client.get("/users/")
#     assert response.status_code == 200
#     print(response.json())
#     login_data = {
#         "email": "testuser0@example.com",
#         "password": "password0",
#     }
#     response = await client.post("/login", data=login_data)
#     assert response.status_code == 200
#     assert response.json() == {}
#     assert "access_token" in response.json()
