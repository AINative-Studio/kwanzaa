"""Pytest configuration and fixtures."""

import os
from typing import AsyncGenerator, Dict, Generator, List
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

# Set test environment variables
os.environ["DATABASE_URL"] = "postgresql+asyncpg://localhost/kwanzaa_test"
os.environ["ZERODB_PROJECT_ID"] = "test-project-id"
os.environ["ZERODB_API_KEY"] = "test-api-key"


@pytest.fixture
def mock_embedding() -> List[float]:
    """Generate a mock embedding vector."""
    return [0.1] * 1536


@pytest.fixture
def mock_search_results() -> List[Dict]:
    """Generate mock search results from ZeroDB."""
    return [
        {
            "id": "nara_cra_1964::chunk::3",
            "score": 0.93,
            "document": "An Act to enforce the constitutional right to vote...",
            "metadata": {
                "doc_id": "nara_cra_1964",
                "namespace": "kwanzaa_primary_sources",
                "citation_label": "National Archives (1964) — Civil Rights Act",
                "canonical_url": "https://www.archives.gov/milestone-documents/civil-rights-act",
                "source_org": "National Archives",
                "year": 1964,
                "content_type": "proclamation",
                "license": "Public Domain",
                "tags": ["civil_rights", "legislation"],
            },
        },
        {
            "id": "loc_legis_cra_1964::chunk::1",
            "score": 0.81,
            "document": "The Civil Rights Act of 1964 outlawed major forms...",
            "metadata": {
                "doc_id": "loc_legis_cra_1964",
                "namespace": "kwanzaa_primary_sources",
                "citation_label": "Library of Congress (1964) — Legislative Summary",
                "canonical_url": "https://www.loc.gov/item/legis-summary-cra-1964",
                "source_org": "Library of Congress",
                "year": 1964,
                "content_type": "legal_document",
                "license": "Public Domain",
                "tags": ["civil_rights", "legislation", "history"],
            },
        },
    ]


@pytest.fixture
def sample_search_request() -> Dict:
    """Sample search request payload."""
    return {
        "query": "What did the Civil Rights Act of 1964 prohibit?",
        "namespace": "kwanzaa_primary_sources",
        "filters": {
            "year_gte": 1960,
            "year_lte": 1970,
            "content_type": ["proclamation", "legal_document"],
        },
        "limit": 10,
        "threshold": 0.7,
    }


@pytest.fixture
def sample_persona_request() -> Dict:
    """Sample search request with persona."""
    return {
        "query": "explain the voting rights act to students",
        "persona_key": "educator",
    }


@pytest.fixture
def mock_zerodb_client() -> MagicMock:
    """Mock ZeroDB client."""
    client = MagicMock()
    client.search_vectors = AsyncMock()
    client.upsert_vector = AsyncMock()
    client.get_vector = AsyncMock()
    return client


@pytest.fixture
def mock_embedding_service() -> MagicMock:
    """Mock embedding service."""
    service = MagicMock()
    service.generate_embedding = AsyncMock()
    return service
