import pytest
from httpx import AsyncClient, ASGITransport
from fastapi import status

from app.main import app

@pytest.mark.asyncio
async def test_get_subscription_plans():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/subscriptions/plans")
    assert response.status_code == status.HTTP_200_OK
    assert "plans" in response.json()