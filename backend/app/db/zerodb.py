"""ZeroDB client wrapper for vector operations."""

from typing import Any, Dict, List, Optional

import httpx

from app.core.config import settings


class ZeroDBError(Exception):
    """Base exception for ZeroDB operations."""

    pass


class ZeroDBClient:
    """Client for interacting with ZeroDB vector database.

    This client wraps the ZeroDB MCP server functions for use in the FastAPI application.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        project_id: Optional[str] = None,
        api_url: Optional[str] = None,
    ) -> None:
        """Initialize ZeroDB client.

        Args:
            api_key: ZeroDB API key (defaults to settings.ZERODB_API_KEY)
            project_id: ZeroDB project ID (defaults to settings.ZERODB_PROJECT_ID)
            api_url: ZeroDB API URL (defaults to settings.ZERODB_API_URL)
        """
        self.api_key = api_key or settings.ZERODB_API_KEY
        self.project_id = project_id or settings.ZERODB_PROJECT_ID
        self.api_url = api_url or settings.ZERODB_API_URL

        if not self.api_key:
            raise ValueError("ZeroDB API key is required")
        if not self.project_id:
            raise ValueError("ZeroDB project ID is required")

        self.client = httpx.AsyncClient(
            base_url=self.api_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            timeout=30.0,
        )

    async def search_vectors(
        self,
        query_vector: List[float],
        namespace: str = "default",
        filter_metadata: Optional[Dict[str, Any]] = None,
        limit: int = 10,
        threshold: float = 0.7,
    ) -> List[Dict[str, Any]]:
        """Search for similar vectors using semantic similarity.

        This method wraps the ZeroDB vector search API to provide a clean interface
        for semantic search operations.

        Args:
            query_vector: Query embedding vector (1536 dimensions)
            namespace: Vector namespace to search
            filter_metadata: Optional metadata filters
            limit: Maximum number of results
            threshold: Minimum similarity score (0.0 to 1.0)

        Returns:
            List of search results with scores and metadata

        Raises:
            ZeroDBError: If search fails
        """
        try:
            payload = {
                "query_vector": query_vector,
                "namespace": namespace,
                "limit": limit,
                "threshold": threshold,
            }

            if filter_metadata:
                payload["filter_metadata"] = filter_metadata

            response = await self.client.post(
                f"/v1/projects/{self.project_id}/vectors/search",
                json=payload,
            )

            if response.status_code == 404:
                # Namespace doesn't exist or no vectors found
                return []

            response.raise_for_status()
            data = response.json()

            return data.get("results", [])

        except httpx.HTTPStatusError as e:
            raise ZeroDBError(f"ZeroDB search failed: {e.response.text}") from e
        except httpx.RequestError as e:
            raise ZeroDBError(f"ZeroDB request failed: {str(e)}") from e
        except Exception as e:
            raise ZeroDBError(f"Unexpected error during ZeroDB search: {str(e)}") from e

    async def upsert_vector(
        self,
        vector_embedding: List[float],
        document: str,
        metadata: Dict[str, Any],
        namespace: str = "default",
        vector_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Upsert a vector embedding with metadata.

        Args:
            vector_embedding: Vector embedding (1536 dimensions)
            document: Source document text
            metadata: Document metadata
            namespace: Vector namespace
            vector_id: Optional vector ID (for updates)

        Returns:
            Response with vector ID

        Raises:
            ZeroDBError: If upsert fails
        """
        try:
            payload = {
                "vector_embedding": vector_embedding,
                "document": document,
                "metadata": metadata,
                "namespace": namespace,
            }

            if vector_id:
                payload["vector_id"] = vector_id

            response = await self.client.post(
                f"/v1/projects/{self.project_id}/vectors/upsert",
                json=payload,
            )

            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as e:
            raise ZeroDBError(f"ZeroDB upsert failed: {e.response.text}") from e
        except httpx.RequestError as e:
            raise ZeroDBError(f"ZeroDB request failed: {str(e)}") from e
        except Exception as e:
            raise ZeroDBError(f"Unexpected error during ZeroDB upsert: {str(e)}") from e

    async def get_vector(
        self,
        vector_id: str,
        namespace: str = "default",
        include_embedding: bool = False,
    ) -> Optional[Dict[str, Any]]:
        """Retrieve a specific vector by ID.

        Args:
            vector_id: Vector ID
            namespace: Vector namespace
            include_embedding: Whether to include full embedding

        Returns:
            Vector data or None if not found

        Raises:
            ZeroDBError: If retrieval fails
        """
        try:
            response = await self.client.get(
                f"/v1/projects/{self.project_id}/vectors/{vector_id}",
                params={
                    "namespace": namespace,
                    "include_embedding": include_embedding,
                },
            )

            if response.status_code == 404:
                return None

            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            raise ZeroDBError(f"ZeroDB get failed: {e.response.text}") from e
        except httpx.RequestError as e:
            raise ZeroDBError(f"ZeroDB request failed: {str(e)}") from e
        except Exception as e:
            raise ZeroDBError(f"Unexpected error during ZeroDB get: {str(e)}") from e

    async def list_namespaces(self) -> List[Dict[str, Any]]:
        """List all namespaces in the project.

        Returns:
            List of namespace metadata

        Raises:
            ZeroDBError: If listing fails
        """
        try:
            response = await self.client.get(
                f"/v1/projects/{self.project_id}/namespaces",
            )

            response.raise_for_status()
            data = response.json()

            return data.get("namespaces", [])

        except httpx.HTTPStatusError as e:
            raise ZeroDBError(f"ZeroDB list namespaces failed: {e.response.text}") from e
        except httpx.RequestError as e:
            raise ZeroDBError(f"ZeroDB request failed: {str(e)}") from e
        except Exception as e:
            raise ZeroDBError(f"Unexpected error listing namespaces: {str(e)}") from e

    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()

    async def __aenter__(self) -> "ZeroDBClient":
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.close()
