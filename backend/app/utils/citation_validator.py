"""Citation validation utilities.

This module provides utilities for validating citation quality and determining
whether retrieved content is sufficient for answering with citations.
"""

from typing import Dict, List, Optional, Tuple

from app.models.answer_json import RetrievalResult
from app.models.search import SearchResult


def validate_similarity_scores(
    results: List[RetrievalResult],
    threshold: float,
) -> Tuple[bool, float]:
    """Validate that retrieval results meet minimum similarity threshold.

    Args:
        results: List of retrieval results
        threshold: Minimum similarity threshold (0.0-1.0)

    Returns:
        Tuple of (passes_threshold, best_score)
        - passes_threshold: True if at least one result meets threshold
        - best_score: The highest similarity score found
    """
    if not results:
        return False, 0.0

    best_score = max(result.score for result in results)
    passes_threshold = best_score >= threshold

    return passes_threshold, best_score


def validate_similarity_scores_from_search(
    results: List[SearchResult],
    threshold: float,
) -> Tuple[bool, float]:
    """Validate that search results meet minimum similarity threshold.

    Args:
        results: List of search results
        threshold: Minimum similarity threshold (0.0-1.0)

    Returns:
        Tuple of (passes_threshold, best_score)
        - passes_threshold: True if at least one result meets threshold
        - best_score: The highest similarity score found
    """
    if not results:
        return False, 0.0

    best_score = max(result.score for result in results)
    passes_threshold = best_score >= threshold

    return passes_threshold, best_score


def count_sources(results: List[RetrievalResult]) -> int:
    """Count unique sources in retrieval results.

    Args:
        results: List of retrieval results

    Returns:
        Number of unique sources (by doc_id)
    """
    if not results:
        return 0

    unique_sources = set(result.doc_id for result in results)
    return len(unique_sources)


def count_sources_from_search(results: List[SearchResult]) -> int:
    """Count unique sources in search results.

    Args:
        results: List of search results

    Returns:
        Number of unique sources (by doc_id)
    """
    if not results:
        return 0

    unique_sources = set(result.doc_id for result in results)
    return len(unique_sources)


def validate_min_sources(
    results: List[RetrievalResult],
    min_required: int,
) -> Tuple[bool, int]:
    """Validate that minimum number of unique sources are present.

    Args:
        results: List of retrieval results
        min_required: Minimum number of unique sources required

    Returns:
        Tuple of (meets_minimum, sources_found)
        - meets_minimum: True if enough sources are present
        - sources_found: Number of unique sources found
    """
    sources_found = count_sources(results)
    meets_minimum = sources_found >= min_required

    return meets_minimum, sources_found


def validate_min_sources_from_search(
    results: List[SearchResult],
    min_required: int,
) -> Tuple[bool, int]:
    """Validate that minimum number of unique sources are present.

    Args:
        results: List of search results
        min_required: Minimum number of unique sources required

    Returns:
        Tuple of (meets_minimum, sources_found)
        - meets_minimum: True if enough sources are present
        - sources_found: Number of unique sources found
    """
    sources_found = count_sources_from_search(results)
    meets_minimum = sources_found >= min_required

    return meets_minimum, sources_found


def count_primary_sources(
    results: List[RetrievalResult],
    primary_content_types: Optional[List[str]] = None,
) -> int:
    """Count primary sources in retrieval results.

    Args:
        results: List of retrieval results
        primary_content_types: List of content types considered primary sources
            Default: ["speech", "letter", "proclamation", "legal_document",
                     "executive_order", "treaty", "diary", "memoir"]

    Returns:
        Number of primary sources found
    """
    if primary_content_types is None:
        primary_content_types = [
            "speech",
            "letter",
            "proclamation",
            "legal_document",
            "executive_order",
            "treaty",
            "diary",
            "memoir",
            "autobiography",
            "interview",
            "testimony",
        ]

    if not results:
        return 0

    primary_count = 0
    seen_docs = set()

    for result in results:
        # Only count each document once
        if result.doc_id in seen_docs:
            continue

        # Check if this is a primary source
        # We need to check the citation_label or snippet for content type hints
        # In a real implementation, this would check metadata
        citation_lower = result.citation_label.lower()
        if any(ct in citation_lower for ct in primary_content_types):
            primary_count += 1
            seen_docs.add(result.doc_id)

    return primary_count


def count_primary_sources_from_search(
    results: List[SearchResult],
    primary_content_types: Optional[List[str]] = None,
) -> int:
    """Count primary sources in search results.

    Args:
        results: List of search results
        primary_content_types: List of content types considered primary sources

    Returns:
        Number of primary sources found
    """
    if primary_content_types is None:
        primary_content_types = [
            "speech",
            "letter",
            "proclamation",
            "legal_document",
            "executive_order",
            "treaty",
            "diary",
            "memoir",
            "autobiography",
            "interview",
            "testimony",
        ]

    if not results:
        return 0

    primary_count = 0
    seen_docs = set()

    for result in results:
        # Only count each document once
        if result.doc_id in seen_docs:
            continue

        # Check content_type from metadata
        if result.metadata.content_type in primary_content_types:
            primary_count += 1
            seen_docs.add(result.doc_id)

    return primary_count


def has_citeable_content(results: List[RetrievalResult]) -> Tuple[bool, List[str]]:
    """Check if results contain citeable content.

    Citeable content must have:
    - Non-empty citation label
    - Valid canonical URL
    - Non-empty snippet or content

    Args:
        results: List of retrieval results

    Returns:
        Tuple of (has_content, missing_fields)
        - has_content: True if at least one result has complete citation info
        - missing_fields: List of fields that are missing or invalid
    """
    if not results:
        return False, ["No results returned from retrieval"]

    missing_fields = []
    has_valid_citation = False

    for idx, result in enumerate(results):
        result_issues = []

        # Check citation label
        if not result.citation_label or result.citation_label.strip() == "":
            result_issues.append(f"Result {idx+1}: Missing citation_label")

        # Check canonical URL
        if not result.canonical_url or result.canonical_url.strip() == "":
            result_issues.append(f"Result {idx+1}: Missing canonical_url")

        # Check snippet content
        if not result.snippet or result.snippet.strip() == "":
            result_issues.append(f"Result {idx+1}: Missing snippet/content")

        # If this result has all required fields, we have at least one valid citation
        if not result_issues:
            has_valid_citation = True
        else:
            missing_fields.extend(result_issues)

    return has_valid_citation, missing_fields


def has_citeable_content_from_search(
    results: List[SearchResult],
) -> Tuple[bool, List[str]]:
    """Check if search results contain citeable content.

    Args:
        results: List of search results

    Returns:
        Tuple of (has_content, missing_fields)
    """
    if not results:
        return False, ["No results returned from retrieval"]

    missing_fields = []
    has_valid_citation = False

    for idx, result in enumerate(results):
        result_issues = []

        # Check citation label from metadata
        if (
            not result.metadata.citation_label
            or result.metadata.citation_label.strip() == ""
        ):
            result_issues.append(f"Result {idx+1}: Missing citation_label")

        # Check canonical URL
        if (
            not result.metadata.canonical_url
            or result.metadata.canonical_url.strip() == ""
        ):
            result_issues.append(f"Result {idx+1}: Missing canonical_url")

        # Check content
        if not result.content or result.content.strip() == "":
            result_issues.append(f"Result {idx+1}: Missing content")

        # If this result has all required fields, we have at least one valid citation
        if not result_issues:
            has_valid_citation = True
        else:
            missing_fields.extend(result_issues)

    return has_valid_citation, missing_fields


def detect_query_type(query: str) -> str:
    """Detect whether query is factual, creative, or analytical.

    Args:
        query: Query text

    Returns:
        Query type: "factual", "creative", or "analytical"
    """
    query_lower = query.lower().strip()

    # Creative indicators
    creative_keywords = [
        "imagine",
        "create",
        "design",
        "write",
        "compose",
        "generate",
        "invent",
        "brainstorm",
        "could you",
        "what if",
    ]

    # Analytical indicators
    analytical_keywords = [
        "analyze",
        "compare",
        "contrast",
        "evaluate",
        "assess",
        "critique",
        "interpret",
        "explain why",
        "how does",
        "relationship between",
    ]

    # Factual indicators
    factual_keywords = [
        "what is",
        "when did",
        "who was",
        "where is",
        "which",
        "define",
        "list",
        "how many",
        "what are",
    ]

    # Check each category
    if any(keyword in query_lower for keyword in creative_keywords):
        return "creative"
    elif any(keyword in query_lower for keyword in analytical_keywords):
        return "analytical"
    elif any(keyword in query_lower for keyword in factual_keywords):
        return "factual"
    else:
        # Default to factual if uncertain
        return "factual"


def generate_gap_descriptions(
    query: str,
    results: List[RetrievalResult],
    threshold: float,
    best_score: float,
) -> List[str]:
    """Generate specific gap descriptions for unknowns array.

    Args:
        query: Original query
        results: Retrieval results
        threshold: Required similarity threshold
        best_score: Best similarity score achieved

    Returns:
        List of specific gap descriptions
    """
    gaps = []

    if not results:
        gaps.append(
            f"No relevant documents found in the corpus for query: '{query}'"
        )
        gaps.append(
            "The current corpus may not contain information about this topic"
        )
    elif best_score < threshold:
        gaps.append(
            f"Retrieved documents have low relevance (best: {best_score:.2f}, "
            f"required: {threshold:.2f})"
        )
        gaps.append(
            "Available documents do not sufficiently address the specific query"
        )

    source_count = count_sources(results)
    if source_count < 2:
        gaps.append(
            f"Only {source_count} unique source(s) found - insufficient for "
            "confident citation"
        )

    return gaps


def generate_gap_descriptions_from_search(
    query: str,
    results: List[SearchResult],
    threshold: float,
    best_score: float,
) -> List[str]:
    """Generate specific gap descriptions from search results.

    Args:
        query: Original query
        results: Search results
        threshold: Required similarity threshold
        best_score: Best similarity score achieved

    Returns:
        List of specific gap descriptions
    """
    gaps = []

    if not results:
        gaps.append(
            f"No relevant documents found in the corpus for query: '{query}'"
        )
        gaps.append(
            "The current corpus may not contain information about this topic"
        )
    elif best_score < threshold:
        gaps.append(
            f"Retrieved documents have low relevance (best: {best_score:.2f}, "
            f"required: {threshold:.2f})"
        )
        gaps.append(
            "Available documents do not sufficiently address the specific query"
        )

    source_count = count_sources_from_search(results)
    if source_count < 2:
        gaps.append(
            f"Only {source_count} unique source(s) found - insufficient for "
            "confident citation"
        )

    return gaps
