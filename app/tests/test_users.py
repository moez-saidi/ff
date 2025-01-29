import random
import string

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_user(client: AsyncClient) -> None:
    user_data = {
        "username": "Momo",
        "email": "user@example.com",
        "password": "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10)),
    }
    response = await client.post("/users/", json=user_data)
    assert response.status_code == 200, response.json()

    assert response.json() == {"id": 1, "username": "Momo", "email": "user@example.com", "is_active": False}


@pytest.mark.asyncio
async def test_list_users(auth_client: AsyncClient, create_test_users):
    test_users = await create_test_users(4)
    response = await auth_client.get("/users/")
    assert response.status_code == 200, response.json()
    users = response.json()
    assert isinstance(users, list)
    assert len(users) == len(test_users) + 1  # Authentication user should be added


@pytest.mark.asyncio
async def test_login(client: AsyncClient, create_test_users):
    await create_test_users(1)
    login_data = {
        "email": "testuser0@example.com",
        "password": "password0",
    }
    response = await client.post("/users/login", json=login_data)
    assert response.status_code == 200, response.json()
    assert "access_token" in response.json()


@pytest.mark.asyncio
async def test_activate_user_account(auth_client: AsyncClient, create_test_users):
    users = await create_test_users(1, is_active=False)
    response = await auth_client.put(f"/users/activate/{users[0].id}")
    assert response.status_code == 200, response.json()
    assert response.json()["is_active"] is True


@pytest.mark.asyncio
async def test_deactivate_user_account(auth_client: AsyncClient, create_test_users):
    users = await create_test_users(1)
    response = await auth_client.put(f"/users/deactivate/{users[0].id}")
    assert response.status_code == 200, response.json()
    assert response.json()["is_active"] is False
