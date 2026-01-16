"""Cross-encoder reranking service for RAG pipeline.

This service provides semantic reranking using cross-encoder models
to improve retrieval precision by computing query-document relevance scores.
"""

import time
from typing import List, Optional, Tuple

from sentence_transformers import CrossEncoder

from app.core.config import settings
from app.models.retrieval import (
    RerankRequest,
    RerankResponse,
    RerankResult,
    RetrievalChunk,
)


class RerankingService:
    """Service for cross-encoder reranking of retrieved chunks.

    This service uses cross-encoder models to compute precise relevance scores
    between the query and retrieved documents, enabling better ranking than
    pure vector similarity alone.
    """

    def __init__(self, model_name: Optional[str] = None) -> None:
        """Initialize the reranking service.

        Args:
            model_name: Name of the cross-encoder model to use.
                       Defaults to settings.RERANK_MODEL.
        """
        self.model_name = model_name or settings.RERANK_MODEL
        self._model: Optional[CrossEncoder] = None

    @property
    def model(self) -> CrossEncoder:
        """Lazy load the cross-encoder model.

        Returns:
            Loaded CrossEncoder model
        """
        if self._model is None:
            self._model = CrossEncoder(self.model_name, max_length=512)
        return self._model

    async def rerank(
        self,
        query: str,
        chunks: List[RetrievalChunk],
        top_n: int = 5,
        combine_scores: bool = True,
        semantic_weight: float = 0.5,
        rerank_weight: float = 0.5,
    ) -> Tuple[List[RetrievalChunk], int]:
        """Rerank retrieved chunks using cross-encoder model.

        This method computes cross-encoder scores for each query-chunk pair
        and optionally combines them with the original semantic scores.

        Args:
            query: User query text
            chunks: List of retrieved chunks to rerank
            top_n: Number of top results to return after reranking
            combine_scores: Whether to combine semantic + rerank scores
            semantic_weight: Weight for original semantic score (0.0-1.0)
            rerank_weight: Weight for rerank score (0.0-1.0)

        Returns:
            Tuple of (reranked chunks list, reranking time in ms)

        Raises:
            ValueError: If inputs are invalid
        """
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")

        if not chunks:
            raise ValueError("Chunks list cannot be empty")

        if top_n < 1:
            raise ValueError("top_n must be at least 1")

        if combine_scores:
            if not (0.0 <= semantic_weight <= 1.0):
                raise ValueError("semantic_weight must be between 0.0 and 1.0")
            if not (0.0 <= rerank_weight <= 1.0):
                raise ValueError("rerank_weight must be between 0.0 and 1.0")

        start_time = time.time()

        # Prepare query-document pairs for cross-encoder
        pairs = [[query, chunk.content] for chunk in chunks]

        # Compute cross-encoder scores
        # Note: CrossEncoder.predict is synchronous but fast
        rerank_scores = self.model.predict(pairs)

        # Normalize rerank scores to [0, 1] range
        # Cross-encoder scores are typically logits, we'll use sigmoid
        import numpy as np

        rerank_scores_normalized = 1 / (1 + np.exp(-np.array(rerank_scores)))

        # Combine scores and create reranked chunks
        reranked_chunks = []
        for idx, chunk in enumerate(chunks):
            rerank_score = float(rerank_scores_normalized[idx])

            # Calculate final score
            if combine_scores:
                final_score = (
                    semantic_weight * chunk.score + rerank_weight * rerank_score
                )
            else:
                final_score = rerank_score

            # Create updated chunk with rerank scores
            chunk_dict = chunk.model_dump()
            chunk_dict["rerank_score"] = rerank_score
            chunk_dict["final_score"] = final_score

            reranked_chunks.append(RetrievalChunk(**chunk_dict))

        # Sort by final score (descending)
        reranked_chunks.sort(key=lambda x: x.final_score or 0, reverse=True)

        # Update ranks after reordering
        for rank, chunk in enumerate(reranked_chunks[:top_n], start=1):
            chunk_dict = chunk.model_dump()
            chunk_dict["rank"] = rank
            reranked_chunks[rank - 1] = RetrievalChunk(**chunk_dict)

        # Return top_n results
        top_chunks = reranked_chunks[:top_n]

        rerank_time_ms = int((time.time() - start_time) * 1000)

        return top_chunks, rerank_time_ms

    async def rerank_with_request(self, request: RerankRequest) -> RerankResponse:
        """Rerank chunks using a RerankRequest object.

        This is a convenience method that wraps the main rerank() method
        and returns a structured RerankResponse.

        Args:
            request: RerankRequest with query and chunks

        Returns:
            RerankResponse with reranked results
        """
        reranked_chunks, rerank_time_ms = await self.rerank(
            query=request.query,
            chunks=request.chunks,
            top_n=request.top_n,
        )

        # Build RerankResult objects
        results = []
        for new_rank, chunk in enumerate(reranked_chunks, start=1):
            # Find original rank
            original_rank = next(
                (
                    c.rank
                    for c in request.chunks
                    if c.chunk_id == chunk.chunk_id
                ),
                new_rank,
            )
            original_score = next(
                (
                    c.score
                    for c in request.chunks
                    if c.chunk_id == chunk.chunk_id
                ),
                0.0,
            )

            results.append(
                RerankResult(
                    chunk_id=chunk.chunk_id,
                    original_rank=original_rank,
                    original_score=original_score,
                    rerank_score=chunk.rerank_score or 0.0,
                    final_score=chunk.final_score or 0.0,
                    new_rank=new_rank,
                )
            )

        return RerankResponse(
            status="success",
            results=results,
            rerank_model=self.model_name,
            rerank_time_ms=rerank_time_ms,
            total_processed=len(request.chunks),
            total_returned=len(reranked_chunks),
        )

    def get_model_info(self) -> dict:
        """Get information about the loaded reranking model.

        Returns:
            Dict containing model information
        """
        return {
            "model_name": self.model_name,
            "model_type": "cross-encoder",
            "max_length": getattr(self.model, "max_length", None),
        }
