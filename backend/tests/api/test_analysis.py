import pytest
from httpx import AsyncClient
from unittest.mock import patch, MagicMock


class TestAnalysisEndpoints:
    async def test_create_analysis_with_valid_url(self, client: AsyncClient):
        with patch("app.api.routes.analysis.run_full_analysis") as mock_task:
            response = await client.post(
                "/api/v1/analyze",
                json={"url": "https://example.com"}
            )
            assert response.status_code == 202
            data = response.json()
            assert "id" in data
            assert data["status"] == "pending"
            assert data["url"] == "https://example.com"

    async def test_create_analysis_accepts_normalized_url(self, client: AsyncClient):
        with patch("app.api.routes.analysis.run_full_analysis") as mock_task:
            response = await client.post(
                "/api/v1/analyze",
                json={"url": "example.com"}
            )
            assert response.status_code == 202

    async def test_create_analysis_rejects_empty_url(self, client: AsyncClient):
        response = await client.post(
            "/api/v1/analyze",
            json={"url": ""}
        )
        assert response.status_code == 422

    async def test_get_analysis_not_found(self, client: AsyncClient):
        response = await client.get("/api/v1/analysis/00000000-0000-0000-0000-000000000000")
        assert response.status_code == 404

    async def test_get_analysis_invalid_uuid(self, client: AsyncClient):
        response = await client.get("/api/v1/analysis/invalid-uuid")
        assert response.status_code == 422


class TestAnalysisValidation:
    async def test_rejects_blocked_hosts(self, client: AsyncClient):
        response = await client.post(
            "/api/v1/analyze",
            json={"url": "http://localhost"}
        )
        assert response.status_code == 422

    async def test_accepts_optional_description(self, client: AsyncClient):
        with patch("app.api.routes.analysis.run_full_analysis") as mock_task:
            response = await client.post(
                "/api/v1/analyze",
                json={
                    "url": "https://example.com",
                    "description": "A test company"
                }
            )
            assert response.status_code == 202

    async def test_accepts_optional_industry(self, client: AsyncClient):
        with patch("app.api.routes.analysis.run_full_analysis") as mock_task:
            response = await client.post(
                "/api/v1/analyze",
                json={
                    "url": "https://example.com",
                    "industry": "Technology"
                }
            )
            assert response.status_code == 202
