"""Tests for data models."""

import pytest
from pydantic import ValidationError

from app.models.search import (
    ChunkMetadata,
    ProvenanceFilters,
    SearchRequest,
    SearchResult,
)


class TestProvenanceFilters:
    """Tests for ProvenanceFilters model."""

    def test_create_valid_filters(self) -> None:
        """Test creating valid provenance filters."""
        filters = ProvenanceFilters(
            year_gte=1960,
            year_lte=1970,
            source_org=["National Archives"],
            content_type=["speech", "letter"],
            tags=["civil_rights"],
        )

        assert filters.year_gte == 1960
        assert filters.year_lte == 1970
        assert filters.source_org == ["National Archives"]
        assert filters.content_type == ["speech", "letter"]
        assert filters.tags == ["civil_rights"]

    def test_exact_year_filter(self) -> None:
        """Test exact year filter."""
        filters = ProvenanceFilters(year=1964)
        assert filters.year == 1964

    def test_year_range_validation_invalid(self) -> None:
        """Test that year_lte < year_gte raises error."""
        with pytest.raises(ValidationError) as exc_info:
            ProvenanceFilters(year_gte=1970, year_lte=1960)

        assert "year_lte must be greater than or equal to year_gte" in str(exc_info.value)

    def test_year_range_validation_valid(self) -> None:
        """Test valid year range."""
        filters = ProvenanceFilters(year_gte=1960, year_lte=1970)
        assert filters.year_gte == 1960
        assert filters.year_lte == 1970

    def test_empty_list_validation(self) -> None:
        """Test that empty lists are rejected."""
        with pytest.raises(ValidationError):
            ProvenanceFilters(source_org=[])

        with pytest.raises(ValidationError):
            ProvenanceFilters(content_type=[])

        with pytest.raises(ValidationError):
            ProvenanceFilters(tags=[])

    def test_year_bounds_validation(self) -> None:
        """Test year bounds validation."""
        # Valid years
        ProvenanceFilters(year=1600)
        ProvenanceFilters(year=2100)

        # Invalid years
        with pytest.raises(ValidationError):
            ProvenanceFilters(year=1599)

        with pytest.raises(ValidationError):
            ProvenanceFilters(year=2101)

    def test_to_metadata_filter(self) -> None:
        """Test conversion to ZeroDB metadata filter format."""
        filters = ProvenanceFilters(
            year_gte=1960,
            year_lte=1970,
            source_org=["National Archives", "Library of Congress"],
            content_type=["speech"],
            tags=["civil_rights"],
        )

        metadata_filter = filters.to_metadata_filter()

        assert metadata_filter["year_gte"] == 1960
        assert metadata_filter["year_lte"] == 1970
        assert metadata_filter["source_org"] == {"$in": ["National Archives", "Library of Congress"]}
        assert metadata_filter["content_type"] == {"$in": ["speech"]}
        assert metadata_filter["tags"] == {"$contains_any": ["civil_rights"]}

    def test_to_metadata_filter_exact_year(self) -> None:
        """Test metadata filter with exact year."""
        filters = ProvenanceFilters(year=1964)
        metadata_filter = filters.to_metadata_filter()

        assert metadata_filter["year"] == 1964
        assert "year_gte" not in metadata_filter
        assert "year_lte" not in metadata_filter


class TestSearchRequest:
    """Tests for SearchRequest model."""

    def test_create_valid_request(self) -> None:
        """Test creating valid search request."""
        request = SearchRequest(
            query="What did the Civil Rights Act of 1964 prohibit?",
            namespace="kwanzaa_primary_sources",
            limit=10,
            threshold=0.7,
        )

        assert request.query == "What did the Civil Rights Act of 1964 prohibit?"
        assert request.namespace == "kwanzaa_primary_sources"
        assert request.limit == 10
        assert request.threshold == 0.7

    def test_query_validation_empty(self) -> None:
        """Test that empty query is rejected."""
        with pytest.raises(ValidationError):
            SearchRequest(query="")

        with pytest.raises(ValidationError):
            SearchRequest(query="   ")

    def test_query_validation_too_long(self) -> None:
        """Test that query > 1000 chars is rejected."""
        with pytest.raises(ValidationError):
            SearchRequest(query="a" * 1001)

    def test_query_whitespace_trimming(self) -> None:
        """Test that query whitespace is trimmed."""
        request = SearchRequest(query="  test query  ")
        assert request.query == "test query"

    def test_limit_validation(self) -> None:
        """Test limit validation."""
        # Valid limits
        SearchRequest(query="test", limit=1)
        SearchRequest(query="test", limit=100)

        # Invalid limits
        with pytest.raises(ValidationError):
            SearchRequest(query="test", limit=0)

        with pytest.raises(ValidationError):
            SearchRequest(query="test", limit=101)

    def test_threshold_validation(self) -> None:
        """Test threshold validation."""
        # Valid thresholds
        SearchRequest(query="test", threshold=0.0)
        SearchRequest(query="test", threshold=1.0)
        SearchRequest(query="test", threshold=0.5)

        # Invalid thresholds
        with pytest.raises(ValidationError):
            SearchRequest(query="test", threshold=-0.1)

        with pytest.raises(ValidationError):
            SearchRequest(query="test", threshold=1.1)

    def test_persona_key_validation(self) -> None:
        """Test persona_key validation."""
        # Valid personas
        for persona in ["educator", "researcher", "creator", "builder"]:
            SearchRequest(query="test", persona_key=persona)

        # Invalid persona
        with pytest.raises(ValidationError):
            SearchRequest(query="test", persona_key="invalid_persona")

    def test_request_with_filters(self) -> None:
        """Test request with provenance filters."""
        request = SearchRequest(
            query="test",
            filters=ProvenanceFilters(
                year_gte=1960,
                year_lte=1970,
                content_type=["speech"],
            ),
        )

        assert request.filters is not None
        assert request.filters.year_gte == 1960
        assert request.filters.year_lte == 1970
        assert request.filters.content_type == ["speech"]

    def test_default_values(self) -> None:
        """Test default values for optional fields."""
        request = SearchRequest(query="test")

        assert request.namespace is None
        assert request.filters is None
        assert request.limit == 10
        assert request.threshold == 0.7
        assert request.include_embeddings is False
        assert request.persona_key is None


class TestChunkMetadata:
    """Tests for ChunkMetadata model."""

    def test_create_valid_metadata(self) -> None:
        """Test creating valid chunk metadata."""
        metadata = ChunkMetadata(
            citation_label="National Archives (1964) — Civil Rights Act",
            canonical_url="https://www.archives.gov/milestone-documents/civil-rights-act",
            source_org="National Archives",
            year=1964,
            content_type="proclamation",
            license="Public Domain",
            tags=["civil_rights", "legislation"],
        )

        assert metadata.citation_label == "National Archives (1964) — Civil Rights Act"
        assert metadata.source_org == "National Archives"
        assert metadata.year == 1964
        assert metadata.content_type == "proclamation"
        assert metadata.license == "Public Domain"
        assert metadata.tags == ["civil_rights", "legislation"]

    def test_year_validation(self) -> None:
        """Test year validation."""
        # Valid years
        ChunkMetadata(
            citation_label="Test",
            canonical_url="https://example.com",
            source_org="Test Org",
            year=1600,
            content_type="test",
            license="Public Domain",
        )

        # Invalid years
        with pytest.raises(ValidationError):
            ChunkMetadata(
                citation_label="Test",
                canonical_url="https://example.com",
                source_org="Test Org",
                year=1599,
                content_type="test",
                license="Public Domain",
            )

    def test_extra_fields_allowed(self) -> None:
        """Test that extra metadata fields are allowed."""
        metadata = ChunkMetadata(
            citation_label="Test",
            canonical_url="https://example.com",
            source_org="Test Org",
            year=1964,
            content_type="test",
            license="Public Domain",
            custom_field="custom_value",
        )

        # Pydantic allows extra fields with Config.extra = "allow"
        assert metadata.model_extra.get("custom_field") == "custom_value"


class TestSearchResult:
    """Tests for SearchResult model."""

    def test_create_valid_result(self) -> None:
        """Test creating valid search result."""
        metadata = ChunkMetadata(
            citation_label="National Archives (1964) — Civil Rights Act",
            canonical_url="https://www.archives.gov/milestone-documents/civil-rights-act",
            source_org="National Archives",
            year=1964,
            content_type="proclamation",
            license="Public Domain",
            tags=["civil_rights"],
        )

        result = SearchResult(
            rank=1,
            score=0.93,
            chunk_id="nara_cra_1964::chunk::3",
            doc_id="nara_cra_1964",
            namespace="kwanzaa_primary_sources",
            content="An Act to enforce the constitutional right to vote...",
            metadata=metadata,
        )

        assert result.rank == 1
        assert result.score == 0.93
        assert result.chunk_id == "nara_cra_1964::chunk::3"
        assert result.doc_id == "nara_cra_1964"
        assert result.namespace == "kwanzaa_primary_sources"
        assert result.metadata.source_org == "National Archives"

    def test_rank_validation(self) -> None:
        """Test rank validation (must be >= 1)."""
        metadata = ChunkMetadata(
            citation_label="Test",
            canonical_url="https://example.com",
            source_org="Test",
            year=1964,
            content_type="test",
            license="Public Domain",
        )

        # Valid rank
        SearchResult(
            rank=1,
            score=0.9,
            chunk_id="test",
            doc_id="test",
            namespace="test",
            content="test",
            metadata=metadata,
        )

        # Invalid rank
        with pytest.raises(ValidationError):
            SearchResult(
                rank=0,
                score=0.9,
                chunk_id="test",
                doc_id="test",
                namespace="test",
                content="test",
                metadata=metadata,
            )

    def test_score_validation(self) -> None:
        """Test score validation (0.0 to 1.0)."""
        metadata = ChunkMetadata(
            citation_label="Test",
            canonical_url="https://example.com",
            source_org="Test",
            year=1964,
            content_type="test",
            license="Public Domain",
        )

        # Valid scores
        SearchResult(
            rank=1,
            score=0.0,
            chunk_id="test",
            doc_id="test",
            namespace="test",
            content="test",
            metadata=metadata,
        )
        SearchResult(
            rank=1,
            score=1.0,
            chunk_id="test",
            doc_id="test",
            namespace="test",
            content="test",
            metadata=metadata,
        )

        # Invalid scores
        with pytest.raises(ValidationError):
            SearchResult(
                rank=1,
                score=-0.1,
                chunk_id="test",
                doc_id="test",
                namespace="test",
                content="test",
                metadata=metadata,
            )

        with pytest.raises(ValidationError):
            SearchResult(
                rank=1,
                score=1.1,
                chunk_id="test",
                doc_id="test",
                namespace="test",
                content="test",
                metadata=metadata,
            )
