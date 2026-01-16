"""Comprehensive tests for citation enforcement logic.

This module tests the citation enforcement system that refuses to answer
when citations are required but retrieval is insufficient.
"""

import pytest

from app.models.answer_json import RetrievalResult, Toggles
from app.models.refusal import (
    PersonaThresholds,
    RefusalReason,
)
from app.models.search import ChunkMetadata, SearchResult
from app.services.citation_enforcer import CitationEnforcer
from app.utils.citation_validator import (
    count_primary_sources,
    count_primary_sources_from_search,
    count_sources,
    count_sources_from_search,
    detect_query_type,
    generate_gap_descriptions,
    has_citeable_content,
    has_citeable_content_from_search,
    validate_min_sources,
    validate_similarity_scores,
)


# Test Fixtures


@pytest.fixture
def sample_retrieval_results() -> list:
    """Create sample retrieval results for testing."""
    return [
        RetrievalResult(
            rank=1,
            score=0.92,
            snippet="Martin Luther King Jr. delivered his famous speech...",
            citation_label="National Archives (1963) — I Have a Dream Speech",
            canonical_url="https://archives.gov/mlk-speech",
            doc_id="nara_mlk_1963",
            chunk_id="nara_mlk_1963::chunk::1",
            namespace="kwanzaa_primary_sources",
        ),
        RetrievalResult(
            rank=2,
            score=0.85,
            snippet="The Civil Rights Act was signed into law...",
            citation_label="National Archives (1964) — Civil Rights Act",
            canonical_url="https://archives.gov/civil-rights-act",
            doc_id="nara_cra_1964",
            chunk_id="nara_cra_1964::chunk::1",
            namespace="kwanzaa_primary_sources",
        ),
    ]


@pytest.fixture
def sample_search_results() -> list:
    """Create sample search results for testing."""
    return [
        SearchResult(
            rank=1,
            score=0.92,
            chunk_id="nara_mlk_1963::chunk::1",
            doc_id="nara_mlk_1963",
            namespace="kwanzaa_primary_sources",
            content="Martin Luther King Jr. delivered his famous speech...",
            metadata=ChunkMetadata(
                citation_label="National Archives (1963) — I Have a Dream Speech",
                canonical_url="https://archives.gov/mlk-speech",
                source_org="National Archives",
                year=1963,
                content_type="speech",
                license="Public Domain",
                tags=["civil_rights", "mlk"],
            ),
        ),
        SearchResult(
            rank=2,
            score=0.85,
            chunk_id="nara_cra_1964::chunk::1",
            doc_id="nara_cra_1964",
            namespace="kwanzaa_primary_sources",
            content="The Civil Rights Act was signed into law...",
            metadata=ChunkMetadata(
                citation_label="National Archives (1964) — Civil Rights Act",
                canonical_url="https://archives.gov/civil-rights-act",
                source_org="National Archives",
                year=1964,
                content_type="legal_document",
                license="Public Domain",
                tags=["civil_rights", "legislation"],
            ),
        ),
    ]


@pytest.fixture
def low_score_results() -> list:
    """Create low-score retrieval results."""
    return [
        RetrievalResult(
            rank=1,
            score=0.65,
            snippet="Some tangentially related content...",
            citation_label="Source (2020) — Document",
            canonical_url="https://example.com/doc",
            doc_id="doc_123",
            chunk_id="doc_123::chunk::1",
            namespace="kwanzaa_secondary_sources",
        ),
    ]


@pytest.fixture
def citation_enforcer() -> CitationEnforcer:
    """Create a citation enforcer instance."""
    return CitationEnforcer(enable_logging=True)


# Citation Validator Tests


class TestCitationValidator:
    """Tests for citation validator utilities."""

    def test_validate_similarity_scores_passes(self, sample_retrieval_results):
        """Test that good scores pass validation."""
        passes, best = validate_similarity_scores(sample_retrieval_results, 0.80)
        assert passes is True
        assert best == 0.92

    def test_validate_similarity_scores_fails(self, low_score_results):
        """Test that low scores fail validation."""
        passes, best = validate_similarity_scores(low_score_results, 0.80)
        assert passes is False
        assert best == 0.65

    def test_validate_similarity_scores_empty(self):
        """Test empty results."""
        passes, best = validate_similarity_scores([], 0.80)
        assert passes is False
        assert best == 0.0

    def test_count_sources(self, sample_retrieval_results):
        """Test counting unique sources."""
        count = count_sources(sample_retrieval_results)
        assert count == 2

    def test_count_sources_duplicates(self):
        """Test counting sources with duplicates."""
        results = [
            RetrievalResult(
                rank=1,
                score=0.9,
                snippet="Content",
                citation_label="Label",
                canonical_url="http://example.com",
                doc_id="doc_1",
                chunk_id="doc_1::chunk::1",
                namespace="ns",
            ),
            RetrievalResult(
                rank=2,
                score=0.8,
                snippet="Content 2",
                citation_label="Label",
                canonical_url="http://example.com",
                doc_id="doc_1",  # Same doc_id
                chunk_id="doc_1::chunk::2",
                namespace="ns",
            ),
        ]
        count = count_sources(results)
        assert count == 1

    def test_validate_min_sources_passes(self, sample_retrieval_results):
        """Test minimum source validation passes."""
        meets_min, found = validate_min_sources(sample_retrieval_results, 2)
        assert meets_min is True
        assert found == 2

    def test_validate_min_sources_fails(self, sample_retrieval_results):
        """Test minimum source validation fails."""
        meets_min, found = validate_min_sources(sample_retrieval_results, 5)
        assert meets_min is False
        assert found == 2

    def test_has_citeable_content_valid(self, sample_retrieval_results):
        """Test citeable content validation with valid results."""
        has_content, missing = has_citeable_content(sample_retrieval_results)
        assert has_content is True
        assert len(missing) == 0

    def test_has_citeable_content_missing_fields(self):
        """Test citeable content with missing fields."""
        results = [
            RetrievalResult(
                rank=1,
                score=0.9,
                snippet=" ",  # Whitespace-only snippet
                citation_label="Label",
                canonical_url="http://example.com",
                doc_id="doc_1",
                chunk_id="doc_1::chunk::1",
                namespace="ns",
            ),
        ]
        # Validator correctly detects whitespace-only content as invalid
        has_content, missing = has_citeable_content(results)
        assert has_content is False
        assert len(missing) > 0
        assert "snippet" in missing[0].lower() or "content" in missing[0].lower()

    def test_detect_query_type_factual(self):
        """Test detecting factual queries."""
        query = "What is the Civil Rights Act of 1964?"
        query_type = detect_query_type(query)
        assert query_type == "factual"

    def test_detect_query_type_creative(self):
        """Test detecting creative queries."""
        query = "Imagine a world where Martin Luther King Jr. was president"
        query_type = detect_query_type(query)
        assert query_type == "creative"

    def test_detect_query_type_analytical(self):
        """Test detecting analytical queries."""
        query = "Compare the Civil Rights Act of 1964 and the Voting Rights Act"
        query_type = detect_query_type(query)
        assert query_type == "analytical"

    def test_generate_gap_descriptions_no_results(self):
        """Test gap generation with no results."""
        gaps = generate_gap_descriptions(
            query="Test query",
            results=[],
            threshold=0.80,
            best_score=0.0,
        )
        assert len(gaps) > 0
        assert any("no relevant documents" in gap.lower() for gap in gaps)

    def test_generate_gap_descriptions_low_score(self, low_score_results):
        """Test gap generation with low scores."""
        gaps = generate_gap_descriptions(
            query="Test query",
            results=low_score_results,
            threshold=0.80,
            best_score=0.65,
        )
        assert len(gaps) > 0
        assert any("low relevance" in gap.lower() for gap in gaps)


class TestSearchResultValidation:
    """Tests for search result validation."""

    def test_count_primary_sources_from_search(self, sample_search_results):
        """Test counting primary sources from search results."""
        count = count_primary_sources_from_search(sample_search_results)
        assert count == 2  # Both are primary sources (speech and legal_document)

    def test_has_citeable_content_from_search(self, sample_search_results):
        """Test citeable content validation for search results."""
        has_content, missing = has_citeable_content_from_search(sample_search_results)
        assert has_content is True
        assert len(missing) == 0


# Persona Thresholds Tests


class TestPersonaThresholds:
    """Tests for persona threshold configurations."""

    def test_educator_defaults(self):
        """Test educator persona defaults."""
        thresholds = PersonaThresholds.educator_defaults()
        assert thresholds.persona == "educator"
        assert thresholds.citations_required is True
        assert thresholds.similarity_threshold == 0.80
        assert thresholds.min_sources == 2
        assert thresholds.strict_mode is True

    def test_researcher_defaults(self):
        """Test researcher persona defaults."""
        thresholds = PersonaThresholds.researcher_defaults()
        assert thresholds.persona == "researcher"
        assert thresholds.citations_required is True
        assert thresholds.similarity_threshold == 0.75
        assert thresholds.min_sources == 3
        assert thresholds.primary_sources_only is True

    def test_creator_defaults(self):
        """Test creator persona defaults."""
        thresholds = PersonaThresholds.creator_defaults()
        assert thresholds.persona == "creator"
        assert thresholds.citations_required is False
        assert thresholds.similarity_threshold == 0.60
        assert thresholds.strict_mode is False

    def test_builder_defaults(self):
        """Test builder persona defaults."""
        thresholds = PersonaThresholds.builder_defaults()
        assert thresholds.persona == "builder"
        assert thresholds.citations_required is False
        assert thresholds.similarity_threshold == 0.65

    def test_for_persona_valid(self):
        """Test getting thresholds for valid persona."""
        thresholds = PersonaThresholds.for_persona("educator")
        assert thresholds.persona == "educator"

    def test_for_persona_invalid(self):
        """Test getting thresholds for invalid persona."""
        with pytest.raises(ValueError, match="Unknown persona"):
            PersonaThresholds.for_persona("invalid")


# Citation Enforcer Tests


class TestCitationEnforcer:
    """Tests for citation enforcer service."""

    def test_evaluate_retrieval_passes_educator(
        self,
        citation_enforcer,
        sample_retrieval_results,
    ):
        """Test that good results pass for educator persona."""
        decision = citation_enforcer.evaluate_retrieval(
            query="What was the Civil Rights Act?",
            results=sample_retrieval_results,
            persona="educator",
        )
        assert decision.should_refuse is False
        assert decision.refusal_message is None

    def test_evaluate_retrieval_passes_researcher(
        self,
        citation_enforcer,
        sample_retrieval_results,
    ):
        """Test that good results might fail for researcher (needs 3 sources)."""
        decision = citation_enforcer.evaluate_retrieval(
            query="What was the Civil Rights Act?",
            results=sample_retrieval_results,
            persona="researcher",
        )
        # Researcher requires 3 sources, we only have 2
        assert decision.should_refuse is True
        assert decision.context.reason == RefusalReason.BELOW_MIN_SOURCES

    def test_evaluate_retrieval_fails_no_results(self, citation_enforcer):
        """Test refusal when no results are returned."""
        decision = citation_enforcer.evaluate_retrieval(
            query="What is Kwanzaa?",
            results=[],
            persona="educator",
        )
        assert decision.should_refuse is True
        assert decision.context.reason == RefusalReason.INSUFFICIENT_RETRIEVAL
        assert len(decision.specific_gaps) > 0
        assert len(decision.suggestions) > 0

    def test_evaluate_retrieval_fails_low_scores(
        self,
        citation_enforcer,
        low_score_results,
    ):
        """Test refusal when similarity scores are too low."""
        decision = citation_enforcer.evaluate_retrieval(
            query="What is Kwanzaa?",
            results=low_score_results,
            persona="educator",
        )
        assert decision.should_refuse is True
        assert decision.context.reason == RefusalReason.LOW_SIMILARITY_SCORE
        assert decision.context.actual_similarity == 0.65
        assert decision.context.similarity_threshold == 0.80

    def test_evaluate_retrieval_fails_no_primary_sources(
        self,
        citation_enforcer,
        sample_retrieval_results,
    ):
        """Test refusal when primary sources are required but not found."""
        # Modify results to have no primary sources
        # Need multiple results to pass min_sources check (researcher needs 3)
        non_primary_results = [
            RetrievalResult(
                rank=1,
                score=0.92,
                snippet="Secondary source content...",
                citation_label="History Book (2020)",
                canonical_url="http://example.com",
                doc_id="book_123",
                chunk_id="book_123::chunk::1",
                namespace="kwanzaa_secondary_sources",
            ),
            RetrievalResult(
                rank=2,
                score=0.88,
                snippet="Another secondary source...",
                citation_label="Academic Article (2019)",
                canonical_url="http://example.com/article",
                doc_id="article_456",
                chunk_id="article_456::chunk::1",
                namespace="kwanzaa_secondary_sources",
            ),
            RetrievalResult(
                rank=3,
                score=0.85,
                snippet="Third secondary source...",
                citation_label="Journal Entry (2021)",
                canonical_url="http://example.com/journal",
                doc_id="journal_789",
                chunk_id="journal_789::chunk::1",
                namespace="kwanzaa_secondary_sources",
            ),
        ]

        decision = citation_enforcer.evaluate_retrieval(
            query="What was the Civil Rights Act?",
            results=non_primary_results,
            persona="researcher",  # Requires primary sources
        )
        assert decision.should_refuse is True
        assert decision.context.reason == RefusalReason.NO_PRIMARY_SOURCES

    def test_evaluate_retrieval_creative_without_citations(
        self,
        citation_enforcer,
    ):
        """Test that creative queries without citation requirements pass."""
        decision = citation_enforcer.evaluate_retrieval(
            query="Imagine a world where...",
            results=[],
            persona="creator",
        )
        # Creator persona doesn't require citations for creative queries
        assert decision.should_refuse is False

    def test_evaluate_retrieval_with_toggles(
        self,
        citation_enforcer,
        sample_retrieval_results,
    ):
        """Test evaluation with custom toggles."""
        toggles = Toggles(
            require_citations=True,
            primary_sources_only=False,
            creative_mode=False,
        )

        decision = citation_enforcer.evaluate_retrieval(
            query="What is Kwanzaa?",
            results=sample_retrieval_results,
            persona="creator",  # Normally doesn't require citations
            toggles=toggles,  # But toggles override
        )
        # Should pass because we have good results
        assert decision.should_refuse is False

    def test_evaluate_retrieval_below_min_sources(
        self,
        citation_enforcer,
        sample_retrieval_results,
    ):
        """Test refusal when below minimum source count."""
        # Researcher requires 3 sources
        decision = citation_enforcer.evaluate_retrieval(
            query="What is Kwanzaa?",
            results=sample_retrieval_results[:1],  # Only 1 result
            persona="researcher",
        )
        assert decision.should_refuse is True
        assert decision.context.reason == RefusalReason.BELOW_MIN_SOURCES
        assert decision.context.sources_found == 1
        assert decision.context.min_sources_required == 3

    def test_evaluate_retrieval_no_citeable_content(self, citation_enforcer):
        """Test refusal when results lack citeable content."""
        # Create results with whitespace-only fields that should fail validation
        incomplete_results = [
            RetrievalResult(
                rank=1,
                score=0.92,
                snippet=" ",  # Whitespace-only snippet
                citation_label="Label",
                canonical_url="http://example.com",
                doc_id="doc_1",
                chunk_id="doc_1::chunk::1",
                namespace="ns",
            ),
        ]

        decision = citation_enforcer.evaluate_retrieval(
            query="What is Kwanzaa?",
            results=incomplete_results,
            persona="educator",
        )
        # This might pass citeable content check due to Pydantic validation
        # but should fail on similarity or min sources
        assert decision.should_refuse is True
        # Could be NO_CITEABLE_CONTENT or BELOW_MIN_SOURCES depending on validation
        assert decision.context.reason in [
            RefusalReason.NO_CITEABLE_CONTENT,
            RefusalReason.BELOW_MIN_SOURCES,
        ]

    def test_evaluate_search_results(
        self,
        citation_enforcer,
        sample_search_results,
    ):
        """Test evaluation with search results."""
        decision = citation_enforcer.evaluate_search_results(
            query="What was the Civil Rights Act?",
            results=sample_search_results,
            persona="educator",
        )
        assert decision.should_refuse is False

    def test_refusal_event_logging(
        self,
        citation_enforcer,
    ):
        """Test that refusal events are logged."""
        citation_enforcer.evaluate_retrieval(
            query="What is Kwanzaa?",
            results=[],
            persona="educator",
        )

        events = citation_enforcer.get_refusal_events()
        assert len(events) == 1
        assert events[0]["query"] == "What is Kwanzaa?"
        assert events[0]["persona"] == "educator"
        assert events[0]["reason"] == RefusalReason.INSUFFICIENT_RETRIEVAL.value

    def test_clear_refusal_events(self, citation_enforcer):
        """Test clearing refusal events."""
        citation_enforcer.evaluate_retrieval(
            query="Test",
            results=[],
            persona="educator",
        )

        assert len(citation_enforcer.get_refusal_events()) == 1
        citation_enforcer.clear_refusal_events()
        assert len(citation_enforcer.get_refusal_events()) == 0


# Integration Tests


class TestCitationEnforcementIntegration:
    """Integration tests for complete citation enforcement workflow."""

    def test_boundary_case_exact_threshold(self, citation_enforcer):
        """Test boundary case where score exactly meets threshold."""
        results = [
            RetrievalResult(
                rank=1,
                score=0.80,  # Exactly at threshold
                snippet="Content",
                citation_label="Label",
                canonical_url="http://example.com",
                doc_id="doc_1",
                chunk_id="doc_1::chunk::1",
                namespace="ns",
            ),
            RetrievalResult(
                rank=2,
                score=0.75,
                snippet="Content 2",
                citation_label="Label 2",
                canonical_url="http://example.com/2",
                doc_id="doc_2",
                chunk_id="doc_2::chunk::1",
                namespace="ns",
            ),
        ]

        decision = citation_enforcer.evaluate_retrieval(
            query="Test query",
            results=results,
            persona="educator",  # Threshold = 0.80
        )
        assert decision.should_refuse is False  # Should pass at exact threshold

    def test_refusal_message_quality(self, citation_enforcer):
        """Test that refusal messages are clear and helpful."""
        decision = citation_enforcer.evaluate_retrieval(
            query="What is Kwanzaa?",
            results=[],
            persona="educator",
        )

        assert decision.refusal_message is not None
        assert len(decision.refusal_message) > 50  # Should be substantive
        assert "cannot" in decision.refusal_message.lower()
        assert len(decision.specific_gaps) > 0
        assert len(decision.suggestions) > 0

        # Check suggestions have actionable content
        for suggestion in decision.suggestions:
            assert suggestion.description
            assert suggestion.suggestion_type in [
                "refine_query",
                "expand_corpus",
                "adjust_filters",
            ]

    def test_all_personas_have_correct_behavior(self, citation_enforcer):
        """Test that all personas behave correctly with empty results."""
        personas = ["educator", "researcher", "creator", "builder"]

        for persona in personas:
            decision = citation_enforcer.evaluate_retrieval(
                query="Factual question about history",
                results=[],
                persona=persona,
            )

            thresholds = PersonaThresholds.for_persona(persona)

            if thresholds.citations_required:
                assert decision.should_refuse is True
            # Note: creator and builder might not refuse for creative queries

    def test_custom_thresholds_override(self, citation_enforcer):
        """Test that custom thresholds override persona defaults."""
        custom = PersonaThresholds(
            persona="educator",  # Must be valid persona
            citations_required=True,
            similarity_threshold=0.95,  # Very high threshold
            min_sources=1,
            primary_sources_only=False,
            strict_mode=True,
        )

        results = [
            RetrievalResult(
                rank=1,
                score=0.85,  # Good but below custom threshold
                snippet="Content",
                citation_label="Label",
                canonical_url="http://example.com",
                doc_id="doc_1",
                chunk_id="doc_1::chunk::1",
                namespace="ns",
            ),
        ]

        decision = citation_enforcer.evaluate_retrieval(
            query="Test",
            results=results,
            custom_thresholds=custom,
        )

        assert decision.should_refuse is True
        assert decision.context.similarity_threshold == 0.95

    def test_no_silent_hallucinations(self, citation_enforcer):
        """Test that insufficient retrieval always refuses when citations required."""
        test_cases = [
            ([], "educator"),  # No results
            ([], "researcher"),  # No results
        ]

        for results, persona in test_cases:
            decision = citation_enforcer.evaluate_retrieval(
                query="Factual query requiring citation",
                results=results,
                persona=persona,
            )

            # Should always refuse with insufficient results
            assert decision.should_refuse is True
            assert decision.refusal_message is not None
            assert len(decision.specific_gaps) > 0


# Edge Cases


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_empty_query(self, citation_enforcer, sample_retrieval_results):
        """Test handling of empty query."""
        decision = citation_enforcer.evaluate_retrieval(
            query="",
            results=sample_retrieval_results,
            persona="educator",
        )
        # Should still evaluate based on results
        assert isinstance(decision.should_refuse, bool)

    def test_very_long_query(self, citation_enforcer, sample_retrieval_results):
        """Test handling of very long query."""
        long_query = "What is " * 100 + "the answer?"
        decision = citation_enforcer.evaluate_retrieval(
            query=long_query,
            results=sample_retrieval_results,
            persona="educator",
        )
        assert isinstance(decision.should_refuse, bool)

    def test_none_persona(self, citation_enforcer, sample_retrieval_results):
        """Test with None persona (should use defaults)."""
        decision = citation_enforcer.evaluate_retrieval(
            query="Test",
            results=sample_retrieval_results,
            persona=None,
        )
        # Should use creator defaults (most permissive)
        assert isinstance(decision.should_refuse, bool)

    def test_invalid_persona_handled(self, citation_enforcer, sample_retrieval_results):
        """Test that invalid persona is handled gracefully."""
        decision = citation_enforcer.evaluate_retrieval(
            query="Test",
            results=sample_retrieval_results,
            persona="invalid_persona",
        )
        # Should fall back to creator defaults
        assert isinstance(decision.should_refuse, bool)
