"""
Tests for the Australian Property Associates FastAPI application.

Tests cover API endpoints for properties, deals, offers, and health checks.
"""

from __future__ import annotations

import pytest
from httpx import AsyncClient, ASGITransport

from nexusprop.api.main import app


# ═══════════════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════════════


@pytest.fixture
async def client():
    """Async HTTP client for testing the FastAPI app with lifespan."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


# ═══════════════════════════════════════════════════════════════════
# HEALTH & ROOT TESTS
# ═══════════════════════════════════════════════════════════════════


class TestHealthEndpoints:
    """Health check and root endpoint tests."""

    @pytest.mark.anyio
    async def test_root(self, client):
        """Root endpoint returns branding info."""
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Australian Property Associates"
        assert "Digital Property Associate" in data["tagline"]

    @pytest.mark.anyio
    async def test_health_check(self, client):
        """Health check returns status and service info."""
        # Ensure DB is initialised for health check
        from nexusprop.db import init_db
        init_db(":memory:")

        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "services" in data

    @pytest.mark.anyio
    async def test_config_endpoint(self, client):
        """Config endpoint returns non-sensitive settings."""
        response = await client.get("/api/v1/config")
        assert response.status_code == 200
        data = response.json()
        assert "scoring" in data
        assert "market_defaults" in data
        assert data["scoring"]["bargain_score_min"] > 0


# ═══════════════════════════════════════════════════════════════════
# PROPERTIES API TESTS
# ═══════════════════════════════════════════════════════════════════


class TestPropertiesAPI:
    """Properties endpoint tests."""

    @pytest.mark.anyio
    async def test_list_properties_empty(self, client):
        """List properties returns empty initially."""
        response = await client.get("/api/v1/properties/")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["properties"] == []

    @pytest.mark.anyio
    async def test_search_properties_post(self, client):
        """POST search endpoint works with body."""
        response = await client.post("/api/v1/properties/search", json={
            "suburbs": ["Sydney"],
            "states": ["NSW"],
            "limit": 10,
        })
        assert response.status_code == 200
        data = response.json()
        assert "total" in data

    @pytest.mark.anyio
    async def test_get_nonexistent_property(self, client):
        """404 for non-existent property."""
        response = await client.get("/api/v1/properties/nonexistent-id")
        assert response.status_code == 404


# ═══════════════════════════════════════════════════════════════════
# DEALS API TESTS
# ═══════════════════════════════════════════════════════════════════


class TestDealsAPI:
    """Deals endpoint tests."""

    @pytest.mark.anyio
    async def test_list_deals_empty(self, client):
        """List deals returns empty initially."""
        response = await client.get("/api/v1/deals/")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0

    @pytest.mark.anyio
    async def test_analyze_nonexistent_property(self, client):
        """Analysing a non-existent property returns 404."""
        response = await client.post("/api/v1/deals/analyze", json={
            "property_id": "nonexistent-id",
            "strategy": "BTL",
        })
        assert response.status_code == 404

    @pytest.mark.anyio
    async def test_quick_roi(self, client):
        """Quick ROI calculation."""
        response = await client.post(
            "/api/v1/deals/quick-roi?purchase_price=650000&weekly_rent=550&state=NSW"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["gross_yield"] > 0
        assert data["stamp_duty"] > 0
        assert "verdict" in data


# ═══════════════════════════════════════════════════════════════════
# OFFERS API TESTS
# ═══════════════════════════════════════════════════════════════════


class TestOffersAPI:
    """Offers endpoint tests."""

    @pytest.mark.anyio
    async def test_list_offers_empty(self, client):
        """List offers returns empty initially."""
        response = await client.get("/api/v1/offers/")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0

    @pytest.mark.anyio
    async def test_generate_offer_nonexistent_deal(self, client):
        """Generating offer for non-existent deal returns 404."""
        response = await client.post("/api/v1/offers/generate", json={
            "deal_id": "nonexistent",
            "buyer_name": "John Smith",
            "buyer_budget_max": 600000,
        })
        assert response.status_code == 404


# ═══════════════════════════════════════════════════════════════════
# WEBHOOK API TESTS
# ═══════════════════════════════════════════════════════════════════


class TestWebhooksAPI:
    """Webhook endpoint tests."""

    @pytest.mark.anyio
    async def test_list_pipeline_runs_empty(self, client):
        """List pipeline runs returns empty initially."""
        response = await client.get("/api/v1/webhooks/pipeline-runs")
        assert response.status_code == 200
        data = response.json()
        assert data["runs"] == []

    @pytest.mark.anyio
    async def test_pipeline_status_not_found(self, client):
        """404 for non-existent pipeline run."""
        response = await client.get("/api/v1/webhooks/pipeline-status/nonexistent")
        assert response.status_code == 404
