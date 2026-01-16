"""Embedding generation service."""

import time
from typing import List, Optional

from sentence_transformers import SentenceTransformer

from app.core.config import settings


class EmbeddingService:
    """Service for generating text embeddings.

    This service uses sentence-transformers to generate embeddings
    for semantic search queries and document chunks.
    """

    def __init__(self, model_name: Optional[str] = None) -> None:
        """Initialize the embedding service.

        Args:
            model_name: Name of the sentence-transformers model to use.
                       Defaults to settings.EMBEDDING_MODEL.
        """
        self.model_name = model_name or settings.EMBEDDING_MODEL
        self._model: Optional[SentenceTransformer] = None

    @property
    def model(self) -> SentenceTransformer:
        """Lazy load the embedding model.

        Returns:
            Loaded SentenceTransformer model
        """
        if self._model is None:
            self._model = SentenceTransformer(self.model_name)
        return self._model

    async def generate_embedding(self, text: str) -> tuple[List[float], int]:
        """Generate embedding for a single text.

        Args:
            text: Input text to embed

        Returns:
            Tuple of (embedding vector, generation time in ms)

        Raises:
            ValueError: If text is empty or too long
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")

        # Enforce reasonable text length limit
        if len(text) > 10000:
            raise ValueError("Text is too long (max 10000 characters)")

        start_time = time.time()

        # Generate embedding (this runs synchronously but we're in an async context)
        embedding = self.model.encode(text, convert_to_numpy=True)

        # Convert to list and ensure correct dimensions
        embedding_list = embedding.tolist()

        if len(embedding_list) != settings.EMBEDDING_DIMENSIONS:
            # Pad or truncate to match expected dimensions
            if len(embedding_list) < settings.EMBEDDING_DIMENSIONS:
                embedding_list.extend([0.0] * (settings.EMBEDDING_DIMENSIONS - len(embedding_list)))
            else:
                embedding_list = embedding_list[: settings.EMBEDDING_DIMENSIONS]

        generation_time_ms = int((time.time() - start_time) * 1000)

        return embedding_list, generation_time_ms

    async def generate_batch_embeddings(
        self, texts: List[str]
    ) -> tuple[List[List[float]], int]:
        """Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed

        Returns:
            Tuple of (list of embedding vectors, total generation time in ms)

        Raises:
            ValueError: If any text is invalid
        """
        if not texts:
            raise ValueError("Text list cannot be empty")

        # Validate all texts
        for text in texts:
            if not text or not text.strip():
                raise ValueError("All texts must be non-empty")
            if len(text) > 10000:
                raise ValueError("Text is too long (max 10000 characters)")

        start_time = time.time()

        # Generate embeddings in batches
        embeddings = self.model.encode(
            texts,
            batch_size=settings.EMBEDDING_BATCH_SIZE,
            convert_to_numpy=True,
        )

        # Convert to list of lists
        embeddings_list = [emb.tolist() for emb in embeddings]

        # Ensure correct dimensions for all embeddings
        normalized_embeddings = []
        for emb in embeddings_list:
            if len(emb) != settings.EMBEDDING_DIMENSIONS:
                if len(emb) < settings.EMBEDDING_DIMENSIONS:
                    emb.extend([0.0] * (settings.EMBEDDING_DIMENSIONS - len(emb)))
                else:
                    emb = emb[: settings.EMBEDDING_DIMENSIONS]
            normalized_embeddings.append(emb)

        generation_time_ms = int((time.time() - start_time) * 1000)

        return normalized_embeddings, generation_time_ms

    def get_model_info(self) -> dict:
        """Get information about the loaded model.

        Returns:
            Dict containing model information
        """
        return {
            "model_name": self.model_name,
            "dimensions": settings.EMBEDDING_DIMENSIONS,
            "max_seq_length": getattr(self.model, "max_seq_length", None),
        }
