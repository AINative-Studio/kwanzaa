"""
ZeroDB Integration Service

Handles vector storage and retrieval using ZeroDB.
Required by Issue #38 - ZeroDB Integration
"""

from typing import List, Dict, Any
import httpx
import os


class ZeroDBService:
    """Service for ZeroDB vector database operations."""

    def __init__(self):
        self.api_url = os.getenv("ZERODB_API_URL", "https://api.ainative.studio")
        self.project_id = os.getenv("ZERODB_PROJECT_ID")
        self.api_key = os.getenv("ZERODB_API_KEY")

    async def publish_chunks(
        self,
        document_id: str,
        namespace: str,
        chunks: List[Dict[str, Any]],
        metadata: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Publish document chunks to ZeroDB.

        Args:
            document_id: Unique document identifier
            namespace: Target namespace
            chunks: List of chunks with embeddings
            metadata: Document provenance metadata

        Returns:
            Publication result with vector IDs
        """
        vectors = []

        for chunk in chunks:
            vectors.append({
                "vector_embedding": chunk["embedding"],
                "document": chunk["text"],
                "metadata": {
                    **chunk["metadata"],
                    **metadata,
                    "namespace": namespace,
                    "document_id": document_id,
                },
                "namespace": namespace,
            })

        # Batch upsert to ZeroDB
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.api_url}/api/v1/vectors/batch-upsert",
                headers={
                    "Content-Type": "application/json",
                    "X-Project-ID": self.project_id,
                    "Authorization": f"Bearer {self.api_key}",
                },
                json={"vectors": vectors},
                timeout=60.0,
            )

            if response.status_code != 200:
                raise Exception(f"ZeroDB publication failed: {response.text}")

            result = response.json()
            return {
                "vector_count": len(result.get("vector_ids", [])),
                "vector_ids": result.get("vector_ids", []),
            }

    async def search_vectors(
        self,
        query_embedding: List[float],
        namespace: str = None,
        limit: int = 10,
        filter_metadata: Dict[str, Any] = None,
    ) -> List[Dict[str, Any]]:
        """Search for similar vectors in ZeroDB."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.api_url}/api/v1/vectors/search",
                headers={
                    "Content-Type": "application/json",
                    "X-Project-ID": self.project_id,
                    "Authorization": f"Bearer {self.api_key}",
                },
                json={
                    "query_vector": query_embedding,
                    "namespace": namespace,
                    "limit": limit,
                    "filter_metadata": filter_metadata,
                },
                timeout=30.0,
            )

            if response.status_code != 200:
                raise Exception(f"ZeroDB search failed: {response.text}")

            return response.json()
