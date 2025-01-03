import random
import string

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_create_user(async_test_client: AsyncClient, db_session: AsyncSession):
    user_data = {
        "username": "Momo",
        "email": "user@example.com",
        "password": "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10)),
    }
    response = await async_test_client.post("/users/", json=user_data)
    assert response.status_code == 200
