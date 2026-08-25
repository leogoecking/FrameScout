from unittest.mock import patch

import pytest


@pytest.mark.asyncio
async def test_health_endpoint_success(async_client):
    with patch("app.api.v1.health.check_db_connection", return_value=True):
        response = await async_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "api"
        assert data["database"] == "connected"
        assert "version" in data


@pytest.mark.asyncio
async def test_health_endpoint_db_disconnected(async_client):
    with patch("app.api.v1.health.check_db_connection", return_value=False):
        response = await async_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "degraded"
        assert data["database"] == "disconnected"


@pytest.mark.asyncio
async def test_liveness_endpoint(async_client):
    response = await async_client.get("/health/live")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "alive"


@pytest.mark.asyncio
async def test_readiness_endpoint(async_client):
    with patch("app.api.v1.health.check_db_connection", return_value=True):
        response = await async_client.get("/health/ready")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ready"

    with patch("app.api.v1.health.check_db_connection", return_value=False):
        response = await async_client.get("/health/ready")
        assert response.status_code == 503
        data = response.json()
        assert data["status"] == "unready"
