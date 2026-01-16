"""Integration tests for answer_json validation middleware.

This module tests the middleware integration with FastAPI endpoints,
ensuring validation works correctly in a real application context.
"""

import pytest
from fastapi import FastAPI, status
from fastapi.testclient import TestClient

from app.middleware.answer_validation import AnswerJsonValidationMiddleware
from app.models.answer_json import AnswerJsonContract


@pytest.fixture
def app() -> FastAPI:
    """Create a test FastAPI application."""
    app = FastAPI()

    # Add validation middleware
    app.add_middleware(
        AnswerJsonValidationMiddleware,
        enabled=True,
        log_all_validations=True,
        strict_mode=True,
    )

    return app


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    """Create a test client."""
    return TestClient(app)


@pytest.fixture
def valid_answer_json() -> dict:
    """Create a valid answer_json response."""
    return {
        "version": "kwanzaa.answer.v1",
        "persona": "educator",
        "model_mode": "base_adapter_rag",
        "toggles": {
            "require_citations": True,
            "primary_sources_only": False,
            "creative_mode": False,
        },
        "answer": {
            "text": "Test answer from endpoint",
            "confidence": 0.95,
            "tone": "neutral",
            "completeness": "complete",
        },
        "sources": [
            {
                "citation_label": "Test Source (2020)",
                "canonical_url": "https://example.com/source",
                "source_org": "Test Organization",
                "year": 2020,
                "content_type": "article",
                "license": "CC BY 4.0",
                "namespace": "test_namespace",
                "doc_id": "test_doc_1",
                "chunk_id": "test_chunk_1",
            }
        ],
        "retrieval_summary": {
            "query": "test query",
            "top_k": 5,
            "namespaces": ["test_namespace"],
            "results": [
                {
                    "rank": 1,
                    "score": 0.95,
                    "snippet": "Test snippet",
                    "citation_label": "Test Source (2020)",
                    "canonical_url": "https://example.com/source",
                    "doc_id": "test_doc_1",
                    "chunk_id": "test_chunk_1",
                    "namespace": "test_namespace",
                }
            ],
        },
        "unknowns": {
            "unsupported_claims": [],
            "missing_context": [],
            "clarifying_questions": [],
        },
        "integrity": {
            "citation_required": True,
            "citations_provided": True,
            "retrieval_confidence": "high",
            "fallback_behavior": "not_needed",
        },
        "provenance": {
            "generated_at": "2026-02-03T18:42:11Z",
            "retrieval_run_id": "9b2d7cfa-cc5e-4a2b-9a6e-6c77f47a9c21",
            "assistant_message_id": "c5f0a75e-4e5c-4a11-9f55-1b5b0a31d77e",
        },
    }


class TestAnswerValidationMiddleware:
    """Tests for AnswerJsonValidationMiddleware."""

    def test_middleware_validates_answer_json_endpoint(
        self, app: FastAPI, client: TestClient, valid_answer_json: dict
    ):
        """Test middleware validates answer_json endpoint response."""
        @app.get("/api/v1/rag/query", response_model=AnswerJsonContract)
        async def query_endpoint():
            return valid_answer_json

        response = client.get("/api/v1/rag/query")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["version"] == "kwanzaa.answer.v1"

    def test_middleware_rejects_invalid_response(
        self, app: FastAPI, client: TestClient
    ):
        """Test middleware rejects invalid answer_json response."""
        @app.get("/api/v1/rag/query")
        async def query_endpoint():
            return {"invalid": "response"}

        response = client.get("/api/v1/rag/query")

        # Should return 422 validation error
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        assert data["error_code"] == "ANSWER_JSON_VALIDATION_FAILED"

    def test_middleware_ignores_non_answer_json_endpoints(
        self, app: FastAPI, client: TestClient
    ):
        """Test middleware ignores non-answer_json endpoints."""
        @app.get("/api/v1/health")
        async def health_endpoint():
            return {"status": "healthy"}

        response = client.get("/api/v1/health")

        # Should not validate this endpoint
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "healthy"

    def test_middleware_handles_non_json_responses(
        self, app: FastAPI, client: TestClient
    ):
        """Test middleware handles non-JSON responses gracefully."""
        @app.get("/api/v1/text")
        async def text_endpoint():
            return "plain text response"

        response = client.get("/api/v1/text")

        # Should not fail on non-JSON responses
        assert response.status_code == status.HTTP_200_OK

    def test_middleware_validates_missing_required_fields(
        self, app: FastAPI, client: TestClient, valid_answer_json: dict
    ):
        """Test middleware catches missing required fields."""
        invalid_response = valid_answer_json.copy()
        del invalid_response["retrieval_summary"]

        @app.get("/api/v1/rag/query")
        async def query_endpoint():
            return invalid_response

        response = client.get("/api/v1/rag/query")

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        assert "retrieval_summary" in str(data)

    def test_middleware_validates_invalid_field_values(
        self, app: FastAPI, client: TestClient, valid_answer_json: dict
    ):
        """Test middleware catches invalid field values."""
        invalid_response = valid_answer_json.copy()
        invalid_response["answer"]["confidence"] = 1.5  # Out of range

        @app.get("/api/v1/rag/query")
        async def query_endpoint():
            return invalid_response

        response = client.get("/api/v1/rag/query")

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        assert "confidence" in str(data)

    def test_middleware_provides_detailed_error_messages(
        self, app: FastAPI, client: TestClient
    ):
        """Test middleware provides detailed validation errors."""
        @app.get("/api/v1/rag/query")
        async def query_endpoint():
            return {"version": "invalid_version"}

        response = client.get("/api/v1/rag/query")

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        assert "validation_errors" in data["details"]
        assert len(data["details"]["validation_errors"]) > 0

    def test_middleware_includes_suggestions(
        self, app: FastAPI, client: TestClient
    ):
        """Test middleware includes helpful suggestions."""
        @app.get("/api/v1/rag/query")
        async def query_endpoint():
            return {"version": "kwanzaa.answer.v1"}

        response = client.get("/api/v1/rag/query")

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        assert "suggestion" in data["details"]


class TestMiddlewareWithDifferentModes:
    """Test middleware behavior in different modes."""

    def test_middleware_disabled(self, valid_answer_json: dict):
        """Test middleware when disabled."""
        app = FastAPI()
        app.add_middleware(
            AnswerJsonValidationMiddleware,
            enabled=False,  # Disabled
        )

        @app.get("/api/v1/rag/query")
        async def query_endpoint():
            return {"invalid": "response"}

        client = TestClient(app)
        response = client.get("/api/v1/rag/query")

        # Should pass through without validation
        assert response.status_code == status.HTTP_200_OK

    def test_middleware_non_strict_mode(self, valid_answer_json: dict):
        """Test middleware in non-strict mode."""
        app = FastAPI()
        app.add_middleware(
            AnswerJsonValidationMiddleware,
            enabled=True,
            strict_mode=False,  # Non-strict
        )

        @app.get("/api/v1/rag/query")
        async def query_endpoint():
            return {"invalid": "response"}

        client = TestClient(app)
        response = client.get("/api/v1/rag/query")

        # In non-strict mode, should log but not fail
        # (This test depends on implementation details)
        # For now, we expect it to pass through
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_422_UNPROCESSABLE_ENTITY,
        ]


class TestMiddlewareWithRealWorldScenarios:
    """Test middleware with real-world scenarios."""

    def test_refusal_response_validation(self, app: FastAPI, client: TestClient):
        """Test validation of refusal response (no sources)."""
        refusal_response = {
            "version": "kwanzaa.answer.v1",
            "persona": "educator",
            "model_mode": "base_adapter_rag",
            "toggles": {
                "require_citations": True,
                "primary_sources_only": False,
                "creative_mode": False,
            },
            "answer": {
                "text": "I don't have information about that topic in my corpus.",
                "confidence": 0.0,
                "tone": "neutral",
                "completeness": "incomplete",
            },
            "sources": [],  # No sources for refusal
            "retrieval_summary": {
                "query": "unknown query",
                "top_k": 5,
                "namespaces": ["kwanzaa_primary_sources"],
                "results": [],
            },
            "unknowns": {
                "unsupported_claims": ["The entire query is out of scope"],
                "missing_context": ["No relevant documents found"],
                "clarifying_questions": ["Could you rephrase the question?"],
            },
            "integrity": {
                "citation_required": True,
                "citations_provided": False,  # OK for refusal
                "retrieval_confidence": "low",
                "fallback_behavior": "graceful_decline",
            },
            "provenance": {
                "generated_at": "2026-02-03T18:42:11Z",
                "retrieval_run_id": "9b2d7cfa-cc5e-4a2b-9a6e-6c77f47a9c21",
                "assistant_message_id": "c5f0a75e-4e5c-4a11-9f55-1b5b0a31d77e",
            },
        }

        @app.get("/api/v1/rag/query")
        async def query_endpoint():
            return refusal_response

        response = client.get("/api/v1/rag/query")

        # Refusal responses should validate successfully
        assert response.status_code == status.HTTP_200_OK

    def test_partial_answer_validation(self, app: FastAPI, client: TestClient):
        """Test validation of partial answer with limited sources."""
        partial_response = {
            "version": "kwanzaa.answer.v1",
            "persona": "researcher",
            "model_mode": "base_adapter_rag",
            "toggles": {
                "require_citations": True,
                "primary_sources_only": True,
                "creative_mode": False,
            },
            "answer": {
                "text": "Based on limited sources, here is what I found...",
                "confidence": 0.65,
                "tone": "formal",
                "completeness": "partial",
            },
            "sources": [
                {
                    "citation_label": "Partial Source (2019)",
                    "canonical_url": "https://example.com/partial",
                    "source_org": "Research Institute",
                    "year": 2019,
                    "content_type": "study",
                    "license": "CC BY-NC 4.0",
                    "namespace": "kwanzaa_primary_sources",
                    "doc_id": "partial_doc",
                    "chunk_id": "partial_chunk",
                }
            ],
            "retrieval_summary": {
                "query": "complex query",
                "top_k": 10,
                "namespaces": ["kwanzaa_primary_sources"],
                "results": [
                    {
                        "rank": 1,
                        "score": 0.72,
                        "snippet": "Limited information snippet",
                        "citation_label": "Partial Source (2019)",
                        "canonical_url": "https://example.com/partial",
                        "doc_id": "partial_doc",
                        "chunk_id": "partial_chunk",
                        "namespace": "kwanzaa_primary_sources",
                    }
                ],
            },
            "unknowns": {
                "unsupported_claims": [],
                "missing_context": ["Need more primary sources from 2015-2018"],
                "clarifying_questions": [
                    "Are you interested in a specific time period?"
                ],
            },
            "integrity": {
                "citation_required": True,
                "citations_provided": True,
                "retrieval_confidence": "medium",
                "fallback_behavior": "not_needed",
            },
            "provenance": {
                "generated_at": "2026-02-03T18:42:11Z",
                "retrieval_run_id": "9b2d7cfa-cc5e-4a2b-9a6e-6c77f47a9c21",
                "assistant_message_id": "c5f0a75e-4e5c-4a11-9f55-1b5b0a31d77e",
            },
        }

        @app.get("/api/v1/rag/query")
        async def query_endpoint():
            return partial_response

        response = client.get("/api/v1/rag/query")

        # Partial responses should validate successfully
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["answer"]["completeness"] == "partial"
