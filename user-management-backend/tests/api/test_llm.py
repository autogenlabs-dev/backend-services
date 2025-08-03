import pytest
from httpx import AsyncClient, ASGITransport
from fastapi import status

from app.main import app

@pytest.mark.asyncio
async def test_get_llm_models():
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

        # Now, get the LLM models
        response = await ac.get("/llm/models", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert "models" in response.json()

@pytest.mark.asyncio
async def test_get_llm_providers():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/llm/providers")
    assert response.status_code == status.HTTP_200_OK
    assert "providers" in response.json()