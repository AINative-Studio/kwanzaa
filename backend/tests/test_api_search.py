"""Tests for search API endpoints."""

from typing import Dict, List
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.search import SearchResponse

client = TestClient(app)


class TestSearchAPI:
    """Tests for search API endpoints."""

    @pytest.mark.integration
    @patch("app.api.v1.endpoints.search.get_zerodb_client")
    @patch("app.api.v1.endpoints.search.get_search_service")
    async def test_semantic_search_success(
        self,
        mock_get_search_service: MagicMock,
        mock_get_zerodb_client: MagicMock,
        sample_search_request: Dict,
        mock_search_results: List[Dict],
    ) -> None:
        """Test successful semantic search."""
        # Setup mocks
        mock_search_service = MagicMock()
        mock_search_service.search = AsyncMock()

        # Create expected response
        from app.models.search import (
            ChunkMetadata,
            SearchMetadata,
            SearchQuery,
            SearchResult,
        )

        expected_response = SearchResponse(
            status="success",
            query=SearchQuery(
                text=sample_search_request["query"],
                namespace=sample_search_request["namespace"],
                filters_applied={},
                limit=sample_search_request["limit"],
                threshold=sample_search_request["threshold"],
            ),
            results=[
                SearchResult(
                    rank=1,
                    score=0.93,
                    chunk_id="test::chunk::1",
                    doc_id="test",
                    namespace="test",
                    content="test content",
                    metadata=ChunkMetadata(
                        citation_label="Test",
                        canonical_url="https://example.com",
                        source_org="Test Org",
                        year=2000,
                        content_type="test",
                        license="Public Domain",
                    ),
                )
            ],
            total_results=1,
            search_metadata=SearchMetadata(
                execution_time_ms=50,
                embedding_model="test-model",
                query_embedding_time_ms=10,
                search_time_ms=40,
            ),
        )

        mock_search_service.search.return_value = expected_response
        mock_get_search_service.return_value = mock_search_service
        mock_get_zerodb_client.return_value = MagicMock()

        # Make request
        response = client.post("/api/v1/search/semantic", json=sample_search_request)

        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["query"]["text"] == sample_search_request["query"]
        assert data["total_results"] == 1
        assert len(data["results"]) == 1

    @pytest.mark.integration
    def test_semantic_search_invalid_query(self) -> None:
        """Test search with invalid query."""
        response = client.post(
            "/api/v1/search/semantic",
            json={
                "query": "",  # Empty query
            },
        )

        assert response.status_code == 422  # Validation error

    @pytest.mark.integration
    def test_semantic_search_invalid_limit(self) -> None:
        """Test search with invalid limit."""
        response = client.post(
            "/api/v1/search/semantic",
            json={
                "query": "test query",
                "limit": 101,  # Exceeds max
            },
        )

        assert response.status_code == 422  # Validation error

    @pytest.mark.integration
    def test_semantic_search_invalid_threshold(self) -> None:
        """Test search with invalid threshold."""
        response = client.post(
            "/api/v1/search/semantic",
            json={
                "query": "test query",
                "threshold": 1.5,  # Exceeds max
            },
        )

        assert response.status_code == 422  # Validation error

    @pytest.mark.integration
    def test_semantic_search_invalid_persona(self) -> None:
        """Test search with invalid persona key."""
        response = client.post(
            "/api/v1/search/semantic",
            json={
                "query": "test query",
                "persona_key": "invalid_persona",
            },
        )

        assert response.status_code == 422  # Validation error

    @pytest.mark.integration
    @patch("app.api.v1.endpoints.search.get_embedding_service")
    async def test_generate_embedding_success(
        self,
        mock_get_embedding_service: MagicMock,
        mock_embedding: List[float],
    ) -> None:
        """Test successful embedding generation."""
        # Setup mock
        mock_service = MagicMock()
        mock_service.generate_embedding = AsyncMock(return_value=(mock_embedding, 10))
        mock_service.model_name = "test-model"
        mock_get_embedding_service.return_value = mock_service

        # Make request
        response = client.post(
            "/api/v1/search/embed",
            params={"text": "test text"},
        )

        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["text"] == "test text"
        assert data["dimensions"] == 1536
        assert data["model"] == "test-model"

    @pytest.mark.integration
    @patch("app.api.v1.endpoints.search.get_zerodb_client")
    async def test_list_namespaces_success(
        self,
        mock_get_zerodb_client: MagicMock,
    ) -> None:
        """Test successful namespace listing."""
        # Setup mock
        mock_client = MagicMock()
        mock_client.list_namespaces = AsyncMock(
            return_value=[
                {
                    "name": "kwanzaa_primary_sources",
                    "display_name": "Primary Sources",
                    "description": "Primary historical documents",
                    "document_count": 1000,
                    "chunk_count": 5000,
                }
            ]
        )
        mock_get_zerodb_client.return_value = mock_client

        # Make request
        response = client.get("/api/v1/search/namespaces")

        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert len(data["namespaces"]) == 1
        assert data["namespaces"][0]["name"] == "kwanzaa_primary_sources"


class TestRootEndpoints:
    """Tests for root and health endpoints."""

    @pytest.mark.integration
    def test_root_endpoint(self) -> None:
        """Test root endpoint."""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Kwanzaa API"
        assert "version" in data
        assert data["status"] == "operational"

    @pytest.mark.integration
    def test_health_check(self) -> None:
        """Test health check endpoint."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
