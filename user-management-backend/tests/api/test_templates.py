import pytest
from httpx import AsyncClient
from fastapi import status

from app.main import app

@pytest.mark.asyncio
async def test_get_templates_empty():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/templates")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"templates": [], "total": 0, "skip": 0, "limit": 100}