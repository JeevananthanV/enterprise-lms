import pytest
from httpx import AsyncClient
from app.core.config import settings


@pytest.mark.asyncio
async def test_application_startup(async_client: AsyncClient):
    """Test that the application starts and serves the root metadata endpoint."""
    response = await async_client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "running"
    assert data["app_name"] == settings.APP_NAME
    assert "version" in data
    assert "docs_url" in data
