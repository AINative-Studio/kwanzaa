"""Complete RAG retrieval pipeline orchestration.

This service orchestrates the full RAG pipeline:
1. Query Processing - Parse query and apply persona settings
2. Retrieval - Semantic search via ZeroDB vector store
3. Ranking/Reranking - Optional cross-encoder reranking
4. Context Injection - Format chunks for LLM context
5. Retrieval Summary - Capture metrics for answer_json contract
"""

import time
from typing import Any, Dict, List, Optional, Tuple

from app.core.config import settings
from app.db.zerodb import ZeroDBClient
from app.models.retrieval import (
    ContextString,
    PersonaThresholds,
    RAGPipelineResponse,
    RAGQueryRequest,
    RetrievalChunk,
    RetrievalStatistics,
)
from app.models.search import SearchResult
from app.services.embedding import EmbeddingService
from app.services.reranker import RerankingService


class RAGPipeline:
    """Complete RAG retrieval pipeline with query processing, retrieval, ranking, and context injection.

    This service implements the full RAG flow with the following principles:
    - Persona-driven configuration (Kujichagulia)
    - Provenance-first retrieval (Imani)
    - Transparent execution (Ujima)
    - Flexible reranking for precision improvement
    """

    def __init__(
        self,
        embedding_service: Optional[EmbeddingService] = None,
        reranking_service: Optional[RerankingService] = None,
        zerodb_client: Optional[ZeroDBClient] = None,
    ) -> None:
        """Initialize the RAG pipeline.

        Args:
            embedding_service: Service for generating embeddings
            reranking_service: Service for cross-encoder reranking
            zerodb_client: Client for ZeroDB vector operations
        """
        self.embedding_service = embedding_service or EmbeddingService()
        self.reranking_service = reranking_service or RerankingService()
        self.zerodb_client = zerodb_client or ZeroDBClient()

    async def process(self, request: RAGQueryRequest) -> RAGPipelineResponse:
        """Execute the complete RAG pipeline.

        This is the main entry point that orchestrates all pipeline stages:
        1. Query processing with persona defaults
        2. Vector retrieval from ZeroDB
        3. Optional reranking for precision
        4. Context string formatting
        5. Statistics collection

        Args:
            request: RAG query request with query and configuration

        Returns:
            RAGPipelineResponse with retrieved chunks and metadata

        Raises:
            ValueError: If request is invalid
            RuntimeError: If pipeline execution fails
        """
        pipeline_start = time.time()

        # Stage 1: Query Processing
        query, persona_config, namespaces, filters = await self._process_query(request)

        # Stage 2: Retrieval
        chunks, embedding_time_ms, search_time_ms = await self._retrieve_chunks(
            query=query,
            namespaces=namespaces,
            filters=filters,
            top_k=persona_config["max_results"],
            threshold=persona_config["similarity_threshold"],
        )

        # Stage 3: Reranking (optional)
        rerank_time_ms = 0
        reranking_enabled = request.enable_reranking
        if reranking_enabled is None:
            reranking_enabled = persona_config["rerank"]

        if reranking_enabled and len(chunks) > 0:
            chunks, rerank_time_ms = await self._rerank_chunks(
                query=query,
                chunks=chunks,
                top_n=request.rerank_top_n or persona_config.get("rerank_top_n", 5),
            )

        # Stage 4: Context Injection
        context_string = None
        if request.include_context_string and len(chunks) > 0:
            context_string = await self._format_context_string(chunks)

        # Stage 5: Statistics Collection
        total_time_ms = int((time.time() - pipeline_start) * 1000)
        statistics = self._build_statistics(
            chunks=chunks,
            namespaces=namespaces,
            filters=filters,
            embedding_time_ms=embedding_time_ms,
            search_time_ms=search_time_ms,
            rerank_time_ms=rerank_time_ms,
            total_time_ms=total_time_ms,
            reranking_enabled=reranking_enabled,
        )

        # Build persona thresholds object
        persona_thresholds = PersonaThresholds(
            similarity_threshold=persona_config["similarity_threshold"],
            max_results=persona_config["max_results"],
            min_results=persona_config["min_results"],
            rerank=persona_config["rerank"],
        )

        # Build and return response
        return RAGPipelineResponse(
            status="success",
            query=query,
            persona=request.persona_key or "educator",
            chunks=chunks,
            context_string=context_string,
            statistics=statistics,
            persona_thresholds=persona_thresholds,
            reranking_enabled=reranking_enabled,
            embedding_model=self.embedding_service.model_name,
            rerank_model=self.reranking_service.model_name if reranking_enabled else None,
        )

    async def _process_query(
        self, request: RAGQueryRequest
    ) -> Tuple[str, Dict[str, Any], List[str], Optional[Dict[str, Any]]]:
        """Process query and apply persona-specific settings.

        Args:
            request: RAG query request

        Returns:
            Tuple of (query, persona_config, namespaces, filters)
        """
        query = request.query.strip()

        # Get persona configuration
        persona_key = request.persona_key or "educator"
        try:
            persona_config = settings.get_persona_config(persona_key)
        except ValueError:
            # Fallback to educator if invalid persona
            persona_config = settings.get_persona_config("educator")

        # Extract RAG-specific config
        rag_config = persona_config.get("rag", {})
        persona_settings = {
            "similarity_threshold": rag_config.get(
                "similarity_threshold", settings.DEFAULT_SIMILARITY_THRESHOLD
            ),
            "max_results": rag_config.get("max_results", settings.DEFAULT_SEARCH_LIMIT),
            "min_results": rag_config.get("min_results", 1),
            "rerank": rag_config.get("rerank", False),
        }

        # Override with request-specific settings
        if request.similarity_threshold is not None:
            persona_settings["similarity_threshold"] = request.similarity_threshold
        if request.top_k is not None:
            persona_settings["max_results"] = request.top_k

        # Determine namespaces
        namespaces = request.namespaces
        if not namespaces:
            namespaces = rag_config.get("namespaces", [settings.DEFAULT_NAMESPACE])

        # Process filters
        filters = request.filters

        return query, persona_settings, namespaces, filters

    async def _retrieve_chunks(
        self,
        query: str,
        namespaces: List[str],
        filters: Optional[Dict[str, Any]],
        top_k: int,
        threshold: float,
    ) -> Tuple[List[RetrievalChunk], int, int]:
        """Retrieve chunks from ZeroDB vector store.

        Args:
            query: Query text
            namespaces: Namespaces to search
            filters: Metadata filters
            top_k: Number of results to retrieve
            threshold: Similarity threshold

        Returns:
            Tuple of (chunks, embedding_time_ms, search_time_ms)
        """
        # Generate query embedding
        query_embedding, embedding_time_ms = await self.embedding_service.generate_embedding(
            query
        )

        # Perform vector search across all namespaces
        all_chunks = []
        total_search_time_ms = 0

        for namespace in namespaces:
            search_start = time.time()

            try:
                raw_results = await self.zerodb_client.search_vectors(
                    query_vector=query_embedding,
                    namespace=namespace,
                    filter_metadata=filters,
                    limit=top_k,
                    threshold=threshold,
                )

                search_time_ms = int((time.time() - search_start) * 1000)
                total_search_time_ms += search_time_ms

                # Convert raw results to RetrievalChunk objects
                for result in raw_results:
                    chunk = self._convert_to_retrieval_chunk(result, namespace)
                    all_chunks.append(chunk)

            except Exception as e:
                # Log error but continue with other namespaces
                print(f"Error searching namespace {namespace}: {str(e)}")
                continue

        # Sort all chunks by score (descending) and assign ranks
        all_chunks.sort(key=lambda x: x.score, reverse=True)

        # Limit to top_k and assign ranks
        top_chunks = []
        for rank, chunk in enumerate(all_chunks[:top_k], start=1):
            chunk_dict = chunk.model_dump()
            chunk_dict["rank"] = rank
            top_chunks.append(RetrievalChunk(**chunk_dict))

        return top_chunks, embedding_time_ms, total_search_time_ms

    def _convert_to_retrieval_chunk(
        self, raw_result: Dict[str, Any], namespace: str
    ) -> RetrievalChunk:
        """Convert raw ZeroDB result to RetrievalChunk.

        Args:
            raw_result: Raw result from ZeroDB
            namespace: Namespace that was searched

        Returns:
            RetrievalChunk object
        """
        metadata = raw_result.get("metadata", {})

        return RetrievalChunk(
            chunk_id=raw_result.get("id") or raw_result.get("chunk_id", "unknown"),
            doc_id=metadata.get("doc_id", "unknown"),
            namespace=namespace,
            content=raw_result.get("document") or raw_result.get("content", ""),
            score=float(raw_result.get("score", 0.0)),
            rank=1,  # Will be updated later
            citation_label=metadata.get("citation_label", "Unknown Source"),
            canonical_url=metadata.get("canonical_url", ""),
            source_org=metadata.get("source_org", "Unknown"),
            year=metadata.get("year", 2000),
            content_type=metadata.get("content_type", "unknown"),
            license=metadata.get("license", "Unknown"),
            tags=metadata.get("tags", []),
        )

    async def _rerank_chunks(
        self, query: str, chunks: List[RetrievalChunk], top_n: int
    ) -> Tuple[List[RetrievalChunk], int]:
        """Apply cross-encoder reranking to chunks.

        Args:
            query: Query text
            chunks: Chunks to rerank
            top_n: Number of top results to return

        Returns:
            Tuple of (reranked chunks, rerank_time_ms)
        """
        if not chunks:
            return [], 0

        reranked_chunks, rerank_time_ms = await self.reranking_service.rerank(
            query=query,
            chunks=chunks,
            top_n=top_n,
            combine_scores=True,
            semantic_weight=0.5,
            rerank_weight=0.5,
        )

        return reranked_chunks, rerank_time_ms

    async def _format_context_string(self, chunks: List[RetrievalChunk]) -> ContextString:
        """Format chunks into context string for LLM injection.

        This creates a structured context string with:
        - Source citations
        - Content snippets
        - Metadata (year, source_org, content_type)
        - Relevance scores

        Args:
            chunks: Chunks to format

        Returns:
            ContextString object with formatted text
        """
        if not chunks:
            return ContextString(
                formatted_context="",
                num_chunks=0,
                total_tokens=0,
                max_chunk_score=0.0,
            )

        context_parts = []
        context_parts.append("# Retrieved Context\n")
        context_parts.append(
            f"The following {len(chunks)} sources were retrieved for this query:\n"
        )

        for chunk in chunks:
            context_parts.append(f"\n## Source {chunk.rank}: {chunk.citation_label}")
            context_parts.append(f"**Relevance Score:** {chunk.final_score or chunk.score:.3f}")
            context_parts.append(f"**Year:** {chunk.year}")
            context_parts.append(f"**Source Organization:** {chunk.source_org}")
            context_parts.append(f"**Content Type:** {chunk.content_type}")
            context_parts.append(f"**URL:** {chunk.canonical_url}")

            if chunk.tags:
                context_parts.append(f"**Tags:** {', '.join(chunk.tags)}")

            context_parts.append(f"\n**Content:**\n{chunk.content}\n")
            context_parts.append("---\n")

        formatted_context = "\n".join(context_parts)

        # Rough token estimation (1 token ≈ 4 characters)
        estimated_tokens = len(formatted_context) // 4

        max_score = max((c.final_score or c.score) for c in chunks)

        return ContextString(
            formatted_context=formatted_context,
            num_chunks=len(chunks),
            total_tokens=estimated_tokens,
            max_chunk_score=max_score,
        )

    def _build_statistics(
        self,
        chunks: List[RetrievalChunk],
        namespaces: List[str],
        filters: Optional[Dict[str, Any]],
        embedding_time_ms: int,
        search_time_ms: int,
        rerank_time_ms: int,
        total_time_ms: int,
        reranking_enabled: bool,
    ) -> RetrievalStatistics:
        """Build retrieval statistics for transparency.

        Args:
            chunks: Retrieved chunks
            namespaces: Namespaces searched
            filters: Filters applied
            embedding_time_ms: Embedding generation time
            search_time_ms: Vector search time
            rerank_time_ms: Reranking time
            total_time_ms: Total pipeline time
            reranking_enabled: Whether reranking was applied

        Returns:
            RetrievalStatistics object
        """
        if not chunks:
            return RetrievalStatistics(
                total_retrieved=0,
                total_reranked=0,
                total_returned=0,
                top_score=0.0,
                average_score=0.0,
                namespaces_searched=namespaces,
                filters_applied=filters,
                embedding_time_ms=embedding_time_ms,
                search_time_ms=search_time_ms,
                rerank_time_ms=rerank_time_ms,
                total_time_ms=total_time_ms,
            )

        scores = [chunk.score for chunk in chunks]
        top_score = max(scores)
        average_score = sum(scores) / len(scores)

        return RetrievalStatistics(
            total_retrieved=len(chunks),
            total_reranked=len(chunks) if reranking_enabled else 0,
            total_returned=len(chunks),
            top_score=top_score,
            average_score=average_score,
            namespaces_searched=namespaces,
            filters_applied=filters,
            embedding_time_ms=embedding_time_ms,
            search_time_ms=search_time_ms,
            rerank_time_ms=rerank_time_ms,
            total_time_ms=total_time_ms,
        )

    async def close(self) -> None:
        """Close the ZeroDB client connection."""
        await self.zerodb_client.close()

    async def __aenter__(self) -> "RAGPipeline":
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.close()
