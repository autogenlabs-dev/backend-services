import pytest
from httpx import AsyncClient, ASGITransport
from fastapi import status

from app.main import app

@pytest.mark.asyncio
async def test_get_organizations():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # First, register a user to get an auth token
        await ac.post(
            "/auth/register",
            json={
                "email": "testuser@example.com",
                "password": "password",
                "first_name": "Test",
                "last_name": "User",
            },
        )
        # Then, log in to get a token
        response = await ac.post(
            "/auth/login-json",
            json={"email": "testuser@example.com", "password": "password"},
        )
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Now, get the organizations
        response = await ac.get("/organizations", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert "organizations" in response.json()