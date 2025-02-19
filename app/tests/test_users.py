import random
import string

import pytest
from httpx import AsyncClient
from starlette import status


@pytest.mark.asyncio
async def test_create_user(client: AsyncClient) -> None:
    user_data = {
        "username": "Momo",
        "email": "user@example.com",
        "password": "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10)),
    }
    response = await client.post("/users/", json=user_data)
    assert response.status_code == 200, response.json()

    assert response.json() == {
        "id": 1,
        "username": "Momo",
        "email": "user@example.com",
        "is_active": False,
        "role_id": 4,
    }  # noqa: E501


@pytest.mark.asyncio
async def test_list_users(auth_client: AsyncClient, create_test_users):
    test_users = await create_test_users(count=4)
    response = await auth_client.get("/users/")
    assert response.status_code == 200, response.json()
    users = response.json()
    assert isinstance(users, list)
    assert len(users) == len(test_users) + 1  # Authentication user should be added


@pytest.mark.parametrize(
    "credentials,status_code,expected_resp",
    [
        (
            {
                "email": "testuser0@example.com",
                "password": "password0",
            },
            status.HTTP_200_OK,
            "access_token",
        ),
        (
            {
                "email": "inactive_testuser0@example.com",
                "password": "password0",
            },
            status.HTTP_400_BAD_REQUEST,
            {"detail": "User account is not active"},
        ),
        (
            {
                "email": "testuser0@example.com",
                "password": "wrongpassword",
            },
            status.HTTP_401_UNAUTHORIZED,
            {"detail": "Invalid credentials"},
        ),
        (
            {
                "email": "testuser1@example.com",
                "password": "password1",
            },
            status.HTTP_404_NOT_FOUND,
            {"detail": "User not found"},
        ),
    ],
)
@pytest.mark.asyncio
async def test_login(
    client: AsyncClient,
    create_test_users,
    credentials: dict,
    status_code: int,
    expected_resp: str | dict,
):
    await create_test_users(count=1)
    await create_test_users(count=1, is_active=False)
    response = await client.post("/users/login", json=credentials)
    assert response.status_code == status_code, response.json()
    if isinstance(expected_resp, str):
        assert expected_resp in response.json(), response.json()
    else:
        assert expected_resp == response.json(), response.json()


@pytest.mark.asyncio
async def test_activate_user_account(auth_client: AsyncClient, create_test_users):
    users = await create_test_users(count=1, is_active=False)
    response = await auth_client.put(f"/users/activate/{users[0].id}")
    assert response.status_code == 200, response.json()
    assert response.json()["is_active"] is True


@pytest.mark.asyncio
async def test_deactivate_user_account(auth_client: AsyncClient, create_test_users):
    users = await create_test_users(count=1)
    response = await auth_client.put(f"/users/deactivate/{users[0].id}")
    assert response.status_code == 200, response.json()
    assert response.json()["is_active"] is False
