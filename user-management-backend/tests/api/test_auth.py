import pytest
from httpx import AsyncClient
from fastapi import status

from app.main import app

@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/health")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "healthy"}

@pytest.mark.asyncio
async def test_user_registration():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post(
            "/auth/register",
            json={
                "email": "testuser@example.com",
                "password": "password",
                "first_name": "Test",
                "last_name": "User",
            },
        )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["user"]["email"] == "testuser@example.com"

@pytest.mark.asyncio
async def test_user_login():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post(
            "/auth/login-json",
            json={"email": "testuser@example.com", "password": "password"},
        )
    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()

@pytest.mark.asyncio
async def test_get_current_user_info():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        await ac.post(
            "/auth/register",
            json={
                "email": "testuser@example.com",
                "password": "password",
                "first_name": "Test",
                "last_name": "User",
            },
        )
        response = await ac.post(
            "/auth/login-json",
            json={"email": "testuser@example.com", "password": "password"},
        )
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        response = await ac.get("/auth/me", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["user"]["email"] == "testuser@example.com"