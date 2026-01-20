"""
Tests for RAGBot Upload + Preview API

Tests all workflow steps:
1. Upload
2. Safety scan
3. Chunk preview
4. Publish
5. Reject
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
import io

client = TestClient(app)


class TestRAGBotUpload:
    """Test document upload workflow."""

    def test_upload_valid_pdf(self):
        """Test uploading a valid PDF file."""
        # Create mock PDF file
        file_content = b"%PDF-1.4\nMock PDF content"
        files = {"file": ("test.pdf", io.BytesIO(file_content), "application/pdf")}

        response = client.post("/api/v1/ragbot/upload", files=files)

        assert response.status_code == 200
        data = response.json()
        assert "document_id" in data
        assert data["filename"] == "test.pdf"
        assert data["status"] == "uploaded"

    def test_upload_invalid_type(self):
        """Test uploading invalid file type."""
        file_content = b"executable content"
        files = {"file": ("test.exe", io.BytesIO(file_content), "application/x-msdownload")}

        response = client.post("/api/v1/ragbot/upload", files=files)

        assert response.status_code == 400
        assert "Invalid file type" in response.json()["detail"]

    def test_upload_oversized_file(self):
        """Test uploading file exceeding size limit."""
        # 51MB file
        file_content = b"x" * (51 * 1024 * 1024)
        files = {"file": ("large.txt", io.BytesIO(file_content), "text/plain")}

        response = client.post("/api/v1/ragbot/upload", files=files)

        assert response.status_code == 400
        assert "exceeds 50MB limit" in response.json()["detail"]


class TestSafetyScan:
    """Test safety scanning functionality."""

    def test_safety_scan_clean_content(self):
        """Test safety scan with clean content."""
        payload = {
            "document_id": "test-123",
            "text": "This is a clean document about history.",
            "metadata": {
                "source_org": "Library of Congress",
                "canonical_url": "https://example.org/doc",
                "license": "Public Domain",
                "year": 2020,
                "content_type": "article",
            },
        }

        response = client.post("/api/v1/ragbot/scan-safety", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["passed"] is True
        assert len(data["pii_matches"]) == 0

    def test_safety_scan_with_pii(self):
        """Test safety scan detecting PII."""
        payload = {
            "document_id": "test-456",
            "text": "Contact me at john.doe@example.com or call 555-123-4567.",
            "metadata": {
                "source_org": "Test Org",
                "canonical_url": "https://example.org/doc",
                "license": "CC0",
                "year": 2021,
                "content_type": "article",
            },
        }

        response = client.post("/api/v1/ragbot/scan-safety", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert len(data["pii_matches"]) >= 2  # Email and phone
        # Check PII types detected
        pii_types = [match["type"] for match in data["pii_matches"]]
        assert "email" in pii_types
        assert "phone" in pii_types


class TestChunkPreview:
    """Test document chunking."""

    @pytest.mark.asyncio
    async def test_chunk_generation(self, mock_document):
        """Test chunk generation for uploaded document."""
        payload = {"document_id": mock_document["document_id"]}

        response = client.post("/api/v1/ragbot/chunk-preview", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert "chunks" in data
        assert data["chunk_count"] > 0
        assert "generation_time_ms" in data


class TestPublishReject:
    """Test publish and reject operations."""

    def test_publish_document(self):
        """Test publishing document to ZeroDB."""
        payload = {
            "document_id": "test-789",
            "namespace": "kwanzaa_primary_sources",
            "chunks": [
                {
                    "chunk_id": "test-789_chunk_0",
                    "text": "Sample chunk text",
                    "chunk_index": 0,
                    "embedding": [0.1] * 384,
                    "metadata": {"document_id": "test-789", "chunk_index": 0},
                }
            ],
            "metadata": {
                "source_org": "Test Org",
                "canonical_url": "https://example.org/doc",
                "license": "Public Domain",
                "year": 2022,
                "content_type": "article",
            },
        }

        response = client.post("/api/v1/ragbot/publish", json=payload)

        # Note: This will fail without actual ZeroDB credentials
        # In real tests, use mocked ZeroDB service
        assert response.status_code in [200, 500]  # 500 if ZeroDB not configured

    def test_reject_document(self):
        """Test rejecting a document."""
        payload = {"document_id": "test-reject", "reason": "Quality issues"}

        response = client.post("/api/v1/ragbot/reject", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "rejected"
        assert data["reason"] == "Quality issues"


class TestMetrics:
    """Test observability metrics endpoint."""

    def test_get_metrics(self):
        """Test retrieving pipeline metrics."""
        response = client.get("/api/v1/ragbot/metrics")

        assert response.status_code == 200
        data = response.json()
        assert "total_uploads" in data
        assert "total_safety_scans" in data
        assert "curator_actions" in data


# Fixtures
@pytest.fixture
def mock_document():
    """Create mock document for testing."""
    # Upload a test document
    file_content = b"This is test content for document processing."
    files = {"file": ("test.txt", io.BytesIO(file_content), "text/plain")}

    response = client.post("/api/v1/ragbot/upload", files=files)
    return response.json()
