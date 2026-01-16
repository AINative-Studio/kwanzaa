"""Semantic search service with ZeroDB integration."""

import time
from typing import Any, Dict, List, Optional

from app.core.config import settings
from app.models.search import (
    ChunkMetadata,
    ProvenanceFilters,
    SearchMetadata,
    SearchQuery,
    SearchRequest,
    SearchResponse,
    SearchResult,
)
from app.models.query_template import (
    PersonaType,
    TemplateSelectionRequest,
)
from app.services.embedding import EmbeddingService
from app.services.query_templates import QueryTemplateService


class SearchService:
    """Service for semantic search with provenance filters.

    This service implements Kwanzaa's core search principles:
    - Provenance-first retrieval (Imani)
    - Persona-driven configuration (Kujichagulia)
    - Transparent search execution (Ujima)
    """

    def __init__(
        self,
        embedding_service: Optional[EmbeddingService] = None,
        template_service: Optional[QueryTemplateService] = None,
    ) -> None:
        """Initialize the search service.

        Args:
            embedding_service: Service for generating embeddings.
                              If None, creates a new instance.
            template_service: Service for query template processing.
                             If None, creates a new instance.
        """
        self.embedding_service = embedding_service or EmbeddingService()
        self.template_service = template_service or QueryTemplateService()

    def _apply_persona_defaults(self, request: SearchRequest) -> SearchRequest:
        """Apply persona-specific defaults to search request.

        Args:
            request: Original search request

        Returns:
            Modified request with persona defaults applied
        """
        if not request.persona_key:
            return request

        try:
            persona_config = settings.get_persona_config(request.persona_key)

            # Apply persona threshold if not explicitly set
            if request.threshold == settings.DEFAULT_SIMILARITY_THRESHOLD:
                request.threshold = persona_config["threshold"]

            # Apply persona namespaces if namespace not explicitly set
            if not request.namespace:
                namespaces = persona_config["namespaces"]
                # Use first namespace as default for single-namespace search
                request.namespace = namespaces[0] if namespaces else settings.DEFAULT_NAMESPACE

        except ValueError:
            # Invalid persona_key, leave request unchanged
            pass

        return request

    async def search(
        self,
        request: SearchRequest,
        zerodb_search_func: Any,
    ) -> SearchResponse:
        """Perform semantic search with provenance filters.

        This is the main entry point for semantic search. It:
        1. Applies persona defaults if specified
        2. Generates query embedding
        3. Performs vector search with metadata filtering
        4. Processes and ranks results
        5. Returns structured response with provenance metadata

        Args:
            request: Search request with query and filters
            zerodb_search_func: Async function for ZeroDB vector search
                               Expected signature: async (query_vector, namespace, filter_metadata,
                                                          limit, threshold) -> List[Dict]

        Returns:
            SearchResponse with results and metadata

        Raises:
            ValueError: If request is invalid
            RuntimeError: If search execution fails
        """
        start_time = time.time()

        # Apply persona defaults
        request = self._apply_persona_defaults(request)

        # Set namespace to default if not specified
        namespace = request.namespace or settings.DEFAULT_NAMESPACE

        # Generate query embedding
        query_embedding, embedding_time_ms = await self.embedding_service.generate_embedding(
            request.query
        )

        # Prepare metadata filters
        metadata_filter = {}
        if request.filters:
            metadata_filter = request.filters.to_metadata_filter()

        # Perform vector search
        search_start = time.time()
        try:
            raw_results = await zerodb_search_func(
                query_vector=query_embedding,
                namespace=namespace,
                filter_metadata=metadata_filter if metadata_filter else None,
                limit=request.limit or settings.DEFAULT_SEARCH_LIMIT,
                threshold=request.threshold or settings.DEFAULT_SIMILARITY_THRESHOLD,
            )
        except Exception as e:
            raise RuntimeError(f"Vector search failed: {str(e)}") from e

        search_time_ms = int((time.time() - search_start) * 1000)

        # Process results
        search_results = self._process_results(
            raw_results=raw_results,
            namespace=namespace,
            include_embeddings=request.include_embeddings or False,
        )

        # Calculate total execution time
        execution_time_ms = int((time.time() - start_time) * 1000)

        # Build response
        return SearchResponse(
            status="success",
            query=SearchQuery(
                text=request.query,
                namespace=namespace,
                filters_applied=metadata_filter if metadata_filter else None,
                limit=request.limit or settings.DEFAULT_SEARCH_LIMIT,
                threshold=request.threshold or settings.DEFAULT_SIMILARITY_THRESHOLD,
            ),
            results=search_results,
            total_results=len(search_results),
            search_metadata=SearchMetadata(
                execution_time_ms=execution_time_ms,
                embedding_model=self.embedding_service.model_name,
                query_embedding_time_ms=embedding_time_ms,
                search_time_ms=search_time_ms,
            ),
        )

    def _process_results(
        self,
        raw_results: List[Dict[str, Any]],
        namespace: str,
        include_embeddings: bool = False,
    ) -> List[SearchResult]:
        """Process raw ZeroDB results into structured SearchResult objects.

        Args:
            raw_results: Raw results from ZeroDB vector search
            namespace: Namespace that was searched
            include_embeddings: Whether to include embeddings in results

        Returns:
            List of SearchResult objects with validated metadata

        Raises:
            ValueError: If result format is invalid
        """
        processed_results = []

        for rank, result in enumerate(raw_results, start=1):
            try:
                # Extract core fields
                chunk_id = result.get("id") or result.get("chunk_id")
                if not chunk_id:
                    raise ValueError("Result missing 'id' or 'chunk_id'")

                score = result.get("score")
                if score is None:
                    raise ValueError("Result missing 'score'")

                content = result.get("document") or result.get("content") or ""

                # Extract metadata
                metadata_dict = result.get("metadata", {})
                doc_id = metadata_dict.get("doc_id") or chunk_id.split("::")[0]

                # Validate required metadata fields
                required_fields = [
                    "citation_label",
                    "canonical_url",
                    "source_org",
                    "year",
                    "content_type",
                    "license",
                ]
                for field in required_fields:
                    if field not in metadata_dict:
                        raise ValueError(f"Result metadata missing required field: {field}")

                # Build ChunkMetadata
                chunk_metadata = ChunkMetadata(
                    citation_label=metadata_dict["citation_label"],
                    canonical_url=metadata_dict["canonical_url"],
                    source_org=metadata_dict["source_org"],
                    year=metadata_dict["year"],
                    content_type=metadata_dict["content_type"],
                    license=metadata_dict["license"],
                    tags=metadata_dict.get("tags", []),
                )

                # Extract embedding if requested
                embedding = None
                if include_embeddings:
                    embedding = result.get("vector_embedding") or result.get("embedding")

                # Build SearchResult
                search_result = SearchResult(
                    rank=rank,
                    score=float(score),
                    chunk_id=chunk_id,
                    doc_id=doc_id,
                    namespace=namespace,
                    content=content,
                    metadata=chunk_metadata,
                    embedding=embedding,
                )

                processed_results.append(search_result)

            except (ValueError, KeyError) as e:
                # Log error but continue processing other results
                # In production, use proper logging
                print(f"Error processing result {rank}: {str(e)}")
                continue

        return processed_results

    async def generate_embedding(self, text: str) -> tuple[List[float], str]:
        """Generate embedding for text.

        Utility method for testing/debugging.

        Args:
            text: Text to embed

        Returns:
            Tuple of (embedding vector, model name)

        Raises:
            ValueError: If text is invalid
        """
        embedding, _ = await self.embedding_service.generate_embedding(text)
        return embedding, self.embedding_service.model_name

    async def search_with_template(
        self,
        query: str,
        persona: PersonaType,
        zerodb_search_func: Any,
        template_overrides: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Perform semantic search using a query template.

        This method integrates the query template system with search execution:
        1. Applies persona-specific template to query
        2. Expands query based on template rules
        3. Applies metadata filters and retrieval parameters
        4. Executes search with template configuration
        5. Returns results with template metadata

        Args:
            query: User query text
            persona: Persona type for template selection
            zerodb_search_func: Async function for ZeroDB vector search
            template_overrides: Optional parameter overrides
            context: Additional context for query processing

        Returns:
            Dictionary with search results and template information:
            {
                "search_response": SearchResponse object,
                "template_metadata": Template application metadata,
                "query_expansion": Query expansion details
            }

        Raises:
            ValueError: If persona is invalid or template not found
            RuntimeError: If search execution fails
        """
        start_time = time.time()

        # Apply query template
        template_request = TemplateSelectionRequest(
            query=query,
            persona=persona,
            template_overrides=template_overrides,
            context=context,
        )

        template_response = self.template_service.apply_template(template_request)
        template_app = template_response.application

        # Build search request from template application
        search_request = SearchRequest(
            query=template_app.expanded_query,
            namespace=template_app.namespaces[0],  # Use primary namespace
            filters=self._parse_template_filters(template_app.metadata_filters),
            limit=template_app.result_limit,
            threshold=template_app.similarity_threshold,
            include_embeddings=False,
        )

        # Execute search
        search_response = await self.search(search_request, zerodb_search_func)

        # Calculate total processing time
        total_time_ms = int((time.time() - start_time) * 1000)

        # Build comprehensive response
        return {
            "search_response": search_response,
            "template_metadata": {
                "persona": template_app.persona.value,
                "template_used": template_app.template_used,
                "nguzo_saba_principle": template_response.template_metadata.get(
                    "nguzo_saba_principle", ""
                ),
                "expansion_strategy": template_response.template_metadata.get(
                    "expansion_strategy", ""
                ),
            },
            "query_expansion": {
                "original_query": template_app.original_query,
                "expanded_query": template_app.expanded_query,
                "expansion_terms": template_app.expansion_terms,
                "terms_added_count": len(template_app.expansion_terms),
            },
            "retrieval_configuration": {
                "namespaces": template_app.namespaces,
                "similarity_threshold": template_app.similarity_threshold,
                "result_limit": template_app.result_limit,
                "min_results": template_app.min_results,
                "rerank": template_app.rerank,
            },
            "context_formatting": {
                "citation_style": template_app.context_formatting.citation_style,
                "include_citations": template_app.context_formatting.include_citations,
                "show_provenance": template_app.context_formatting.show_provenance,
            },
            "performance": {
                "total_time_ms": total_time_ms,
                "search_time_ms": search_response.search_metadata.execution_time_ms,
                "template_application_time_ms": total_time_ms
                - search_response.search_metadata.execution_time_ms,
            },
        }

    def _parse_template_filters(
        self, template_filters: Dict[str, Any]
    ) -> Optional[ProvenanceFilters]:
        """Parse template metadata filters into ProvenanceFilters.

        Args:
            template_filters: Metadata filters from template application

        Returns:
            ProvenanceFilters object or None if no filters
        """
        if not template_filters:
            return None

        # Extract provenance filter fields
        filter_data = {}

        # Handle year filters
        if "year_gte" in template_filters:
            filter_data["year_gte"] = template_filters["year_gte"]
        if "year_lte" in template_filters:
            filter_data["year_lte"] = template_filters["year_lte"]
        if "year" in template_filters:
            filter_data["year"] = template_filters["year"]

        # Handle content_type (convert from $in format)
        if "content_type" in template_filters:
            if isinstance(template_filters["content_type"], dict):
                filter_data["content_type"] = template_filters["content_type"].get("$in", [])
            else:
                filter_data["content_type"] = [template_filters["content_type"]]

        # Handle source_org
        if "source_org" in template_filters:
            if isinstance(template_filters["source_org"], dict):
                filter_data["source_org"] = template_filters["source_org"].get("$in", [])
            else:
                filter_data["source_org"] = [template_filters["source_org"]]

        # Handle tags
        if "tags" in template_filters:
            if isinstance(template_filters["tags"], dict):
                # Could be $all, $contains_any, etc.
                filter_data["tags"] = (
                    template_filters["tags"].get("$all")
                    or template_filters["tags"].get("$contains_any")
                    or []
                )
            else:
                filter_data["tags"] = template_filters["tags"]

        # Create ProvenanceFilters if we have any data
        if filter_data:
            return ProvenanceFilters(**filter_data)

        return None
