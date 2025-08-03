import pytest
from httpx import AsyncClient
from fastapi import status

from app.main import app

@pytest.mark.asyncio
async def test_get_components_empty():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/components")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"components": [], "total": 0, "skip": 0, "limit": 100}

@pytest.mark.asyncio
async def test_create_component():
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

        # Now, create a component
        response = await ac.post(
            "/components",
            headers=headers,
            json={
                "title": "Test Component",
                "description": "This is a test component.",
                "category": "Test",
                "tags": ["test", "component"],
                "type": "Test",
                "language": "Python",
                "difficulty_level": "Easy",
                "plan_type": "Free",
            },
        )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["title"] == "Test Component"