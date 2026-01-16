"""Search API endpoints."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.errors import InvalidRequestError, ServiceUnavailableError
from app.db.zerodb import ZeroDBClient, ZeroDBError
from app.models.search import SearchRequest, SearchResponse
from app.services.embedding import EmbeddingService
from app.services.search import SearchService

router = APIRouter()

# Dependency injection
_embedding_service: EmbeddingService | None = None
_search_service: SearchService | None = None
_zerodb_client: ZeroDBClient | None = None


def get_embedding_service() -> EmbeddingService:
    """Get or create embedding service instance.

    Returns:
        EmbeddingService instance
    """
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service


def get_search_service(
    embedding_service: EmbeddingService = Depends(get_embedding_service),
) -> SearchService:
    """Get or create search service instance.

    Args:
        embedding_service: Embedding service dependency

    Returns:
        SearchService instance
    """
    global _search_service
    if _search_service is None:
        _search_service = SearchService(embedding_service=embedding_service)
    return _search_service


async def get_zerodb_client() -> ZeroDBClient:
    """Get ZeroDB client instance.

    Returns:
        ZeroDBClient instance

    Raises:
        HTTPException: If ZeroDB client cannot be initialized
    """
    global _zerodb_client
    try:
        if _zerodb_client is None:
            _zerodb_client = ZeroDBClient()
        return _zerodb_client
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"ZeroDB client initialization failed: {str(e)}",
        ) from e


@router.post(
    "/semantic",
    response_model=SearchResponse,
    status_code=status.HTTP_200_OK,
    summary="Perform semantic search",
    description="""
    Perform semantic search across the Kwanzaa corpus with provenance filters.

    This endpoint supports:
    - Natural language queries
    - Metadata filtering (year, source organization, content type, tags)
    - Persona-driven search with preset configurations
    - Namespace-specific search

    The response includes ranked results with:
    - Similarity scores
    - Full provenance metadata (citations, sources, licenses)
    - Search execution metadata
    """,
    responses={
        200: {
            "description": "Successful search",
            "content": {
                "application/json": {
                    "example": {
                        "status": "success",
                        "query": {
                            "text": "What did the Civil Rights Act of 1964 prohibit?",
                            "namespace": "kwanzaa_primary_sources",
                            "filters_applied": {
                                "year_gte": 1960,
                                "year_lte": 1970,
                            },
                            "limit": 10,
                            "threshold": 0.7,
                        },
                        "results": [
                            {
                                "rank": 1,
                                "score": 0.93,
                                "chunk_id": "nara_cra_1964::chunk::3",
                                "doc_id": "nara_cra_1964",
                                "namespace": "kwanzaa_primary_sources",
                                "content": "An Act to enforce the constitutional right to vote...",
                                "metadata": {
                                    "citation_label": "National Archives (1964) — Civil Rights Act",
                                    "canonical_url": "https://www.archives.gov/milestone-documents/civil-rights-act",
                                    "source_org": "National Archives",
                                    "year": 1964,
                                    "content_type": "proclamation",
                                    "license": "Public Domain",
                                    "tags": ["civil_rights", "legislation"],
                                },
                            }
                        ],
                        "total_results": 1,
                        "search_metadata": {
                            "execution_time_ms": 45,
                            "embedding_model": "BAAI/bge-small-en-v1.5",
                            "query_embedding_time_ms": 12,
                            "search_time_ms": 33,
                        },
                    }
                }
            },
        },
        400: {"description": "Invalid request parameters"},
        401: {"description": "Unauthorized - missing or invalid authentication"},
        429: {"description": "Rate limit exceeded"},
        500: {"description": "Internal server error"},
        503: {"description": "ZeroDB service unavailable"},
    },
    tags=["search"],
)
async def semantic_search(
    request: SearchRequest,
    search_service: SearchService = Depends(get_search_service),
    zerodb_client: ZeroDBClient = Depends(get_zerodb_client),
) -> SearchResponse:
    """Perform semantic search with provenance filters.

    Args:
        request: Search request with query and filters
        search_service: Search service dependency
        zerodb_client: ZeroDB client dependency

    Returns:
        SearchResponse with results and metadata

    Raises:
        HTTPException: If search fails
    """
    try:
        # Perform search using ZeroDB client
        response = await search_service.search(
            request=request,
            zerodb_search_func=zerodb_client.search_vectors,
        )

        return response

    except ValueError as e:
        # Invalid request or validation error
        raise InvalidRequestError(
            message=str(e),
            details={"field": "query" if "query" in str(e).lower() else "request"},
        ) from e

    except ZeroDBError as e:
        # ZeroDB service error
        raise ServiceUnavailableError(
            service_name="ZeroDB",
            message=str(e),
        ) from e

    except Exception as e:
        # Unexpected error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}",
        ) from e


@router.post(
    "/embed",
    status_code=status.HTTP_200_OK,
    summary="Generate text embedding",
    description="""
    Generate an embedding vector for the given text.

    This is a utility endpoint for testing and debugging. It returns the
    embedding vector that would be used for semantic search.
    """,
    responses={
        200: {"description": "Embedding generated successfully"},
        400: {"description": "Invalid text input"},
        500: {"description": "Embedding generation failed"},
    },
    tags=["search"],
)
async def generate_embedding(
    text: str,
    embedding_service: EmbeddingService = Depends(get_embedding_service),
) -> dict:
    """Generate embedding for text.

    Args:
        text: Text to embed
        embedding_service: Embedding service dependency

    Returns:
        Dict with embedding and metadata

    Raises:
        HTTPException: If embedding generation fails
    """
    try:
        embedding, generation_time_ms = await embedding_service.generate_embedding(text)

        return {
            "status": "success",
            "text": text,
            "embedding": embedding,
            "dimensions": len(embedding),
            "model": embedding_service.model_name,
            "generation_time_ms": generation_time_ms,
        }

    except ValueError as e:
        raise InvalidRequestError(
            message=str(e),
            details={"field": "text"},
        ) from e

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Embedding generation failed: {str(e)}",
        ) from e


@router.get(
    "/namespaces",
    status_code=status.HTTP_200_OK,
    summary="List available namespaces",
    description="""
    List all available vector namespaces and their metadata.

    This endpoint returns information about each namespace including:
    - Display name and description
    - Document and chunk counts
    - Available content types
    - Year range of content
    - Source organizations
    """,
    responses={
        200: {"description": "Namespaces retrieved successfully"},
        401: {"description": "Unauthorized"},
        503: {"description": "ZeroDB service unavailable"},
    },
    tags=["search"],
)
async def list_namespaces(
    zerodb_client: ZeroDBClient = Depends(get_zerodb_client),
) -> dict:
    """List available namespaces.

    Args:
        zerodb_client: ZeroDB client dependency

    Returns:
        Dict with namespace information

    Raises:
        HTTPException: If listing fails
    """
    try:
        namespaces = await zerodb_client.list_namespaces()

        return {
            "status": "success",
            "namespaces": namespaces,
        }

    except ZeroDBError as e:
        raise ServiceUnavailableError(
            service_name="ZeroDB",
            message=str(e),
        ) from e

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list namespaces: {str(e)}",
        ) from e
