import pytest
from httpx import AsyncClient
from app.core.config import settings


@pytest.mark.asyncio
async def test_root_health_endpoint(async_client: AsyncClient):
    """Test the direct GET /health endpoint."""
    response = await async_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["app_name"] == settings.APP_NAME
    assert "subsystems" in data
    assert "postgresql" in data["subsystems"]
    assert "mongodb" in data["subsystems"]
    assert "redis" in data["subsystems"]


@pytest.mark.asyncio
async def test_api_v1_health_endpoint(async_client: AsyncClient):
    """Test the versioned GET /api/v1/health endpoint."""
    response = await async_client.get(f"{settings.API_V1_STR}/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["environment"] == settings.ENVIRONMENT


@pytest.mark.asyncio
async def test_domain_boundary_placeholders(async_client: AsyncClient):
    """Test that domain module boundaries are registered under /api/v1."""
    domains = [
        "auth",
        "users",
        "courses",
        "modules",
        "lessons",
        "enrollment",
        "progress",
        "assessment",
        "analytics",
        "notifications",
        "audit",
    ]
    for domain in domains:
        response = await async_client.get(f"{settings.API_V1_STR}/{domain}/status")
        assert response.status_code == 200
        data = response.json()
        assert data["domain"] == domain
        assert data["status"] == "registered"
