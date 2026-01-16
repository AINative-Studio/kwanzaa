"""Citation enforcement service.

This service implements citation enforcement logic that refuses to answer
when citations are required but retrieval is insufficient. Enforces Imani
(Faith) through honest communication when we cannot provide cited answers.
"""

import logging
from typing import Dict, List, Optional

from app.models.answer_json import RetrievalResult, Toggles
from app.models.refusal import (
    PersonaThresholds,
    RefusalContext,
    RefusalDecision,
    RefusalReason,
    RefusalSuggestion,
)
from app.models.search import SearchResult
from app.utils.citation_validator import (
    count_primary_sources,
    count_primary_sources_from_search,
    detect_query_type,
    generate_gap_descriptions,
    generate_gap_descriptions_from_search,
    has_citeable_content,
    has_citeable_content_from_search,
    validate_min_sources,
    validate_min_sources_from_search,
    validate_similarity_scores,
    validate_similarity_scores_from_search,
)

logger = logging.getLogger(__name__)


class CitationEnforcer:
    """Enforces citation requirements and decides when to refuse answering.

    This class implements the core citation enforcement logic, checking
    whether retrieved content is sufficient for answering with proper citations.
    """

    def __init__(self, enable_logging: bool = True):
        """Initialize citation enforcer.

        Args:
            enable_logging: Whether to log refusal events (default: True)
        """
        self.enable_logging = enable_logging
        self._refusal_events: List[Dict] = []

    def evaluate_retrieval(
        self,
        query: str,
        results: List[RetrievalResult],
        persona: Optional[str] = None,
        toggles: Optional[Toggles] = None,
        custom_thresholds: Optional[PersonaThresholds] = None,
    ) -> RefusalDecision:
        """Evaluate whether retrieval results are sufficient for answering.

        This is the main entry point for citation enforcement.

        Args:
            query: Original query text
            results: Retrieval results from vector search
            persona: Persona identifier (educator, researcher, etc.)
            toggles: User-controlled behavior toggles
            custom_thresholds: Custom thresholds (overrides persona defaults)

        Returns:
            RefusalDecision with full context and suggestions
        """
        # Determine thresholds
        thresholds = self._get_thresholds(
            persona=persona,
            toggles=toggles,
            custom_thresholds=custom_thresholds,
        )

        # Detect query type
        query_type = detect_query_type(query)

        # Check if citations are required
        if not thresholds.citations_required and query_type == "creative":
            # Creative queries without citation requirements can proceed
            return RefusalDecision(
                should_refuse=False,
                refusal_message=None,
                specific_gaps=[],
                suggestions=[],
            )

        # Validate retrieval results
        decision = self._validate_retrieval_results(
            query=query,
            results=results,
            thresholds=thresholds,
            query_type=query_type,
        )

        # Log refusal event if configured
        if decision.should_refuse and self.enable_logging:
            self._log_refusal_event(
                query=query,
                decision=decision,
                persona=persona,
                query_type=query_type,
            )

        return decision

    def evaluate_search_results(
        self,
        query: str,
        results: List[SearchResult],
        persona: Optional[str] = None,
        toggles: Optional[Toggles] = None,
        custom_thresholds: Optional[PersonaThresholds] = None,
    ) -> RefusalDecision:
        """Evaluate search results for citation sufficiency.

        Args:
            query: Original query text
            results: Search results
            persona: Persona identifier
            toggles: User-controlled toggles
            custom_thresholds: Custom thresholds

        Returns:
            RefusalDecision
        """
        # Determine thresholds
        thresholds = self._get_thresholds(
            persona=persona,
            toggles=toggles,
            custom_thresholds=custom_thresholds,
        )

        # Detect query type
        query_type = detect_query_type(query)

        # Check if citations are required
        if not thresholds.citations_required and query_type == "creative":
            return RefusalDecision(
                should_refuse=False,
                refusal_message=None,
                specific_gaps=[],
                suggestions=[],
            )

        # Validate search results
        decision = self._validate_search_results(
            query=query,
            results=results,
            thresholds=thresholds,
            query_type=query_type,
        )

        # Log refusal event if configured
        if decision.should_refuse and self.enable_logging:
            self._log_refusal_event(
                query=query,
                decision=decision,
                persona=persona,
                query_type=query_type,
            )

        return decision

    def _get_thresholds(
        self,
        persona: Optional[str],
        toggles: Optional[Toggles],
        custom_thresholds: Optional[PersonaThresholds],
    ) -> PersonaThresholds:
        """Get appropriate thresholds for evaluation.

        Priority:
        1. Custom thresholds (if provided)
        2. Toggles (if provided)
        3. Persona defaults
        4. Creator defaults (most permissive)

        Args:
            persona: Persona identifier
            toggles: User toggles
            custom_thresholds: Custom thresholds

        Returns:
            PersonaThresholds to use for evaluation
        """
        # Use custom thresholds if provided
        if custom_thresholds is not None:
            return custom_thresholds

        # Get persona defaults or use creator as fallback
        if persona:
            try:
                thresholds = PersonaThresholds.for_persona(persona)
            except ValueError:
                logger.warning(f"Unknown persona: {persona}, using creator defaults")
                thresholds = PersonaThresholds.creator_defaults()
        else:
            thresholds = PersonaThresholds.creator_defaults()

        # Apply toggles if provided
        if toggles:
            if toggles.require_citations:
                thresholds.citations_required = True
            if toggles.primary_sources_only:
                thresholds.primary_sources_only = True

        return thresholds

    def _validate_retrieval_results(
        self,
        query: str,
        results: List[RetrievalResult],
        thresholds: PersonaThresholds,
        query_type: str,
    ) -> RefusalDecision:
        """Validate retrieval results against thresholds.

        Args:
            query: Original query
            results: Retrieval results
            thresholds: Thresholds to apply
            query_type: Type of query

        Returns:
            RefusalDecision
        """
        # Check 1: Are there any results?
        if not results:
            return self._create_refusal(
                reason=RefusalReason.INSUFFICIENT_RETRIEVAL,
                query=query,
                thresholds=thresholds,
                query_type=query_type,
                actual_similarity=0.0,
                sources_found=0,
                primary_sources_found=0,
                results=results,
            )

        # Check 2: Do results have citeable content?
        has_content, missing_fields = has_citeable_content(results)
        if not has_content:
            return self._create_refusal(
                reason=RefusalReason.NO_CITEABLE_CONTENT,
                query=query,
                thresholds=thresholds,
                query_type=query_type,
                actual_similarity=0.0,
                sources_found=0,
                primary_sources_found=0,
                results=results,
                additional_gaps=missing_fields,
            )

        # Check 3: Do results meet similarity threshold?
        passes_threshold, best_score = validate_similarity_scores(
            results=results,
            threshold=thresholds.similarity_threshold,
        )

        if not passes_threshold:
            return self._create_refusal(
                reason=RefusalReason.LOW_SIMILARITY_SCORE,
                query=query,
                thresholds=thresholds,
                query_type=query_type,
                actual_similarity=best_score,
                sources_found=len(results),
                primary_sources_found=count_primary_sources(results),
                results=results,
            )

        # Check 4: Are there enough unique sources?
        meets_min, sources_found = validate_min_sources(
            results=results,
            min_required=thresholds.min_sources,
        )

        if not meets_min:
            return self._create_refusal(
                reason=RefusalReason.BELOW_MIN_SOURCES,
                query=query,
                thresholds=thresholds,
                query_type=query_type,
                actual_similarity=best_score,
                sources_found=sources_found,
                primary_sources_found=count_primary_sources(results),
                results=results,
            )

        # Check 5: If primary sources required, are there enough?
        if thresholds.primary_sources_only:
            primary_count = count_primary_sources(results)
            if primary_count == 0:
                return self._create_refusal(
                    reason=RefusalReason.NO_PRIMARY_SOURCES,
                    query=query,
                    thresholds=thresholds,
                    query_type=query_type,
                    actual_similarity=best_score,
                    sources_found=sources_found,
                    primary_sources_found=0,
                    results=results,
                )

        # All checks passed - can proceed with answer
        return RefusalDecision(
            should_refuse=False,
            refusal_message=None,
            specific_gaps=[],
            suggestions=[],
        )

    def _validate_search_results(
        self,
        query: str,
        results: List[SearchResult],
        thresholds: PersonaThresholds,
        query_type: str,
    ) -> RefusalDecision:
        """Validate search results against thresholds.

        Args:
            query: Original query
            results: Search results
            thresholds: Thresholds to apply
            query_type: Type of query

        Returns:
            RefusalDecision
        """
        # Check 1: Are there any results?
        if not results:
            return self._create_search_refusal(
                reason=RefusalReason.INSUFFICIENT_RETRIEVAL,
                query=query,
                thresholds=thresholds,
                query_type=query_type,
                actual_similarity=0.0,
                sources_found=0,
                primary_sources_found=0,
                results=results,
            )

        # Check 2: Do results have citeable content?
        has_content, missing_fields = has_citeable_content_from_search(results)
        if not has_content:
            return self._create_search_refusal(
                reason=RefusalReason.NO_CITEABLE_CONTENT,
                query=query,
                thresholds=thresholds,
                query_type=query_type,
                actual_similarity=0.0,
                sources_found=0,
                primary_sources_found=0,
                results=results,
                additional_gaps=missing_fields,
            )

        # Check 3: Do results meet similarity threshold?
        passes_threshold, best_score = validate_similarity_scores_from_search(
            results=results,
            threshold=thresholds.similarity_threshold,
        )

        if not passes_threshold:
            return self._create_search_refusal(
                reason=RefusalReason.LOW_SIMILARITY_SCORE,
                query=query,
                thresholds=thresholds,
                query_type=query_type,
                actual_similarity=best_score,
                sources_found=len(results),
                primary_sources_found=count_primary_sources_from_search(results),
                results=results,
            )

        # Check 4: Are there enough unique sources?
        meets_min, sources_found = validate_min_sources_from_search(
            results=results,
            min_required=thresholds.min_sources,
        )

        if not meets_min:
            return self._create_search_refusal(
                reason=RefusalReason.BELOW_MIN_SOURCES,
                query=query,
                thresholds=thresholds,
                query_type=query_type,
                actual_similarity=best_score,
                sources_found=sources_found,
                primary_sources_found=count_primary_sources_from_search(results),
                results=results,
            )

        # Check 5: If primary sources required, are there enough?
        if thresholds.primary_sources_only:
            primary_count = count_primary_sources_from_search(results)
            if primary_count == 0:
                return self._create_search_refusal(
                    reason=RefusalReason.NO_PRIMARY_SOURCES,
                    query=query,
                    thresholds=thresholds,
                    query_type=query_type,
                    actual_similarity=best_score,
                    sources_found=sources_found,
                    primary_sources_found=0,
                    results=results,
                )

        # All checks passed
        return RefusalDecision(
            should_refuse=False,
            refusal_message=None,
            specific_gaps=[],
            suggestions=[],
        )

    def _create_refusal(
        self,
        reason: RefusalReason,
        query: str,
        thresholds: PersonaThresholds,
        query_type: str,
        actual_similarity: float,
        sources_found: int,
        primary_sources_found: int,
        results: List[RetrievalResult],
        additional_gaps: Optional[List[str]] = None,
    ) -> RefusalDecision:
        """Create a refusal decision with context and suggestions.

        Args:
            reason: Reason for refusal
            query: Original query
            thresholds: Thresholds used
            query_type: Type of query
            actual_similarity: Best similarity score achieved
            sources_found: Number of sources found
            primary_sources_found: Number of primary sources found
            results: Retrieval results
            additional_gaps: Additional gap descriptions

        Returns:
            RefusalDecision
        """
        context = RefusalContext(
            reason=reason,
            persona=thresholds.persona,
            similarity_threshold=thresholds.similarity_threshold,
            actual_similarity=actual_similarity,
            min_sources_required=thresholds.min_sources,
            sources_found=sources_found,
            primary_sources_required=thresholds.primary_sources_only,
            primary_sources_found=primary_sources_found,
            query_type=query_type,
        )

        # Generate refusal message
        refusal_message = self._generate_refusal_message(reason, context)

        # Generate specific gaps
        gaps = generate_gap_descriptions(
            query=query,
            results=results,
            threshold=thresholds.similarity_threshold,
            best_score=actual_similarity,
        )

        if additional_gaps:
            gaps.extend(additional_gaps)

        # Generate suggestions
        suggestions = self._generate_suggestions(reason, query, thresholds)

        return RefusalDecision(
            should_refuse=True,
            context=context,
            refusal_message=refusal_message,
            specific_gaps=gaps,
            suggestions=suggestions,
        )

    def _create_search_refusal(
        self,
        reason: RefusalReason,
        query: str,
        thresholds: PersonaThresholds,
        query_type: str,
        actual_similarity: float,
        sources_found: int,
        primary_sources_found: int,
        results: List[SearchResult],
        additional_gaps: Optional[List[str]] = None,
    ) -> RefusalDecision:
        """Create a refusal decision from search results.

        Args:
            reason: Reason for refusal
            query: Original query
            thresholds: Thresholds used
            query_type: Type of query
            actual_similarity: Best similarity score achieved
            sources_found: Number of sources found
            primary_sources_found: Number of primary sources found
            results: Search results
            additional_gaps: Additional gap descriptions

        Returns:
            RefusalDecision
        """
        context = RefusalContext(
            reason=reason,
            persona=thresholds.persona,
            similarity_threshold=thresholds.similarity_threshold,
            actual_similarity=actual_similarity,
            min_sources_required=thresholds.min_sources,
            sources_found=sources_found,
            primary_sources_required=thresholds.primary_sources_only,
            primary_sources_found=primary_sources_found,
            query_type=query_type,
        )

        refusal_message = self._generate_refusal_message(reason, context)

        gaps = generate_gap_descriptions_from_search(
            query=query,
            results=results,
            threshold=thresholds.similarity_threshold,
            best_score=actual_similarity,
        )

        if additional_gaps:
            gaps.extend(additional_gaps)

        suggestions = self._generate_suggestions(reason, query, thresholds)

        return RefusalDecision(
            should_refuse=True,
            context=context,
            refusal_message=refusal_message,
            specific_gaps=gaps,
            suggestions=suggestions,
        )

    def _generate_refusal_message(
        self,
        reason: RefusalReason,
        context: RefusalContext,
    ) -> str:
        """Generate a clear, helpful refusal message.

        Args:
            reason: Reason for refusal
            context: Refusal context

        Returns:
            Human-readable refusal message
        """
        if reason == RefusalReason.INSUFFICIENT_RETRIEVAL:
            return (
                "I cannot provide a cited answer to this query because no relevant "
                "documents were found in the current corpus. To maintain accuracy "
                "and trust, I must refuse rather than provide an uncited response."
            )
        elif reason == RefusalReason.LOW_SIMILARITY_SCORE:
            return (
                f"I cannot provide a cited answer because the retrieved documents "
                f"have low relevance (best: {context.actual_similarity:.2f}, "
                f"required: {context.similarity_threshold:.2f}). To maintain "
                f"accuracy, I must refuse rather than cite insufficient sources."
            )
        elif reason == RefusalReason.NO_PRIMARY_SOURCES:
            return (
                "I cannot provide a cited answer because no primary sources were "
                "found in the retrieval results, and primary sources are required "
                f"for {context.persona} persona queries."
            )
        elif reason == RefusalReason.BELOW_MIN_SOURCES:
            return (
                f"I cannot provide a cited answer because only "
                f"{context.sources_found} source(s) were found, but "
                f"{context.min_sources_required} are required for confident citation."
            )
        elif reason == RefusalReason.NO_CITEABLE_CONTENT:
            return (
                "I cannot provide a cited answer because the retrieved content "
                "lacks necessary citation metadata (URLs, labels, or content). "
                "Citations require complete provenance information."
            )
        else:
            return (
                "I cannot provide a cited answer due to insufficient retrieval results. "
                "To maintain trust and accuracy, I must refuse rather than provide "
                "uncited information."
            )

    def _generate_suggestions(
        self,
        reason: RefusalReason,
        query: str,
        thresholds: PersonaThresholds,
    ) -> List[RefusalSuggestion]:
        """Generate actionable suggestions for improving the query.

        Args:
            reason: Reason for refusal
            query: Original query
            thresholds: Thresholds used

        Returns:
            List of RefusalSuggestion objects
        """
        suggestions = []

        if reason == RefusalReason.INSUFFICIENT_RETRIEVAL:
            suggestions.append(
                RefusalSuggestion(
                    suggestion_type="refine_query",
                    description="Try rephrasing your query with different keywords",
                    example="Instead of specific names, try broader topic areas",
                )
            )
            suggestions.append(
                RefusalSuggestion(
                    suggestion_type="expand_corpus",
                    description="The corpus may need expansion to cover this topic",
                    example="Consider ingesting additional documents on this subject",
                )
            )
        elif reason == RefusalReason.LOW_SIMILARITY_SCORE:
            suggestions.append(
                RefusalSuggestion(
                    suggestion_type="refine_query",
                    description="Rephrase your query to better match document content",
                    example="Use terminology that appears in historical documents",
                )
            )
        elif reason == RefusalReason.NO_PRIMARY_SOURCES:
            suggestions.append(
                RefusalSuggestion(
                    suggestion_type="adjust_filters",
                    description="Consider allowing secondary sources",
                    example="Disable primary_sources_only toggle",
                )
            )
            suggestions.append(
                RefusalSuggestion(
                    suggestion_type="expand_corpus",
                    description="Ingest primary source documents on this topic",
                    example="Add speeches, letters, or official documents",
                )
            )
        elif reason == RefusalReason.BELOW_MIN_SOURCES:
            suggestions.append(
                RefusalSuggestion(
                    suggestion_type="refine_query",
                    description="Broaden your query to match more documents",
                    example="Use more general terms or remove specific constraints",
                )
            )

        return suggestions

    def _log_refusal_event(
        self,
        query: str,
        decision: RefusalDecision,
        persona: Optional[str],
        query_type: str,
    ) -> None:
        """Log a refusal event for analysis.

        Args:
            query: Original query
            decision: Refusal decision
            persona: Persona used
            query_type: Type of query
        """
        if not decision.context:
            return

        event = {
            "query": query,
            "persona": persona,
            "query_type": query_type,
            "reason": decision.context.reason.value,
            "similarity_threshold": decision.context.similarity_threshold,
            "actual_similarity": decision.context.actual_similarity,
            "min_sources_required": decision.context.min_sources_required,
            "sources_found": decision.context.sources_found,
            "primary_sources_required": decision.context.primary_sources_required,
            "primary_sources_found": decision.context.primary_sources_found,
        }

        self._refusal_events.append(event)

        # Log to standard logger
        logger.info(
            f"Citation refusal: {decision.context.reason.value} - "
            f"Query: '{query}' - Persona: {persona}"
        )

    def get_refusal_events(self) -> List[Dict]:
        """Get all logged refusal events.

        Returns:
            List of refusal event dictionaries
        """
        return self._refusal_events.copy()

    def clear_refusal_events(self) -> None:
        """Clear all logged refusal events."""
        self._refusal_events.clear()
