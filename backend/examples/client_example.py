#!/usr/bin/env python3
"""
Example client for Kwanzaa Semantic Search API.

This script demonstrates how to use the semantic search API
for various use cases and persona configurations.
"""

import asyncio
import json
from typing import Any, Dict, List, Optional

import httpx


class KwanzaaSearchClient:
    """Client for Kwanzaa Semantic Search API."""

    def __init__(self, base_url: str = "http://localhost:8000") -> None:
        """Initialize the client.

        Args:
            base_url: Base URL of the API
        """
        self.base_url = base_url
        self.api_base = f"{base_url}/api/v1/search"

    async def semantic_search(
        self,
        query: str,
        namespace: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 10,
        threshold: float = 0.7,
        persona_key: Optional[str] = None,
        include_embeddings: bool = False,
    ) -> Dict[str, Any]:
        """Perform semantic search.

        Args:
            query: Search query text
            namespace: Vector namespace
            filters: Provenance filters
            limit: Maximum results
            threshold: Minimum similarity score
            persona_key: Persona configuration
            include_embeddings: Include embeddings in response

        Returns:
            Search response

        Raises:
            httpx.HTTPError: If request fails
        """
        payload = {
            "query": query,
            "limit": limit,
            "threshold": threshold,
            "include_embeddings": include_embeddings,
        }

        if namespace:
            payload["namespace"] = namespace
        if filters:
            payload["filters"] = filters
        if persona_key:
            payload["persona_key"] = persona_key

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.api_base}/semantic",
                json=payload,
                timeout=30.0,
            )
            response.raise_for_status()
            return response.json()

    async def generate_embedding(self, text: str) -> Dict[str, Any]:
        """Generate embedding for text.

        Args:
            text: Text to embed

        Returns:
            Embedding response

        Raises:
            httpx.HTTPError: If request fails
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.api_base}/embed",
                params={"text": text},
                timeout=30.0,
            )
            response.raise_for_status()
            return response.json()

    async def list_namespaces(self) -> List[Dict[str, Any]]:
        """List available namespaces.

        Returns:
            List of namespace metadata

        Raises:
            httpx.HTTPError: If request fails
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.api_base}/namespaces",
                timeout=30.0,
            )
            response.raise_for_status()
            data = response.json()
            return data.get("namespaces", [])

    def print_results(self, response: Dict[str, Any], verbose: bool = False) -> None:
        """Pretty print search results.

        Args:
            response: Search response
            verbose: Include detailed metadata
        """
        print("\n" + "=" * 80)
        print("SEARCH RESULTS")
        print("=" * 80)

        # Query info
        query_info = response["query"]
        print(f"\nQuery: {query_info['text']}")
        print(f"Namespace: {query_info['namespace']}")
        print(f"Threshold: {query_info['threshold']}")
        print(f"Limit: {query_info['limit']}")

        if query_info.get("filters_applied"):
            print(f"Filters: {json.dumps(query_info['filters_applied'], indent=2)}")

        # Results
        print(f"\nTotal Results: {response['total_results']}")
        print("\n" + "-" * 80)

        for result in response["results"]:
            print(f"\nRank {result['rank']}: {result['metadata']['citation_label']}")
            print(f"Score: {result['score']:.3f}")
            print(f"URL: {result['metadata']['canonical_url']}")
            print(f"Year: {result['metadata']['year']}")
            print(f"Type: {result['metadata']['content_type']}")
            print(f"Source: {result['metadata']['source_org']}")

            if result['metadata'].get('tags'):
                print(f"Tags: {', '.join(result['metadata']['tags'])}")

            content = result['content']
            if len(content) > 200:
                content = content[:200] + "..."
            print(f"\nContent: {content}")

            if verbose:
                print(f"Chunk ID: {result['chunk_id']}")
                print(f"Doc ID: {result['doc_id']}")
                print(f"Namespace: {result['namespace']}")

            print("-" * 80)

        # Metadata
        metadata = response["search_metadata"]
        print(f"\nExecution Time: {metadata['execution_time_ms']}ms")
        print(f"Embedding Time: {metadata['query_embedding_time_ms']}ms")
        print(f"Search Time: {metadata['search_time_ms']}ms")
        print(f"Model: {metadata['embedding_model']}")
        print("\n" + "=" * 80 + "\n")


async def example_basic_search() -> None:
    """Example: Basic semantic search."""
    print("\n### Example 1: Basic Semantic Search ###")

    client = KwanzaaSearchClient()

    response = await client.semantic_search(
        query="What did the Civil Rights Act of 1964 prohibit?",
        limit=5,
    )

    client.print_results(response)


async def example_filtered_search() -> None:
    """Example: Search with provenance filters."""
    print("\n### Example 2: Search with Provenance Filters ###")

    client = KwanzaaSearchClient()

    response = await client.semantic_search(
        query="civil rights legislation",
        namespace="kwanzaa_primary_sources",
        filters={
            "year_gte": 1960,
            "year_lte": 1970,
            "content_type": ["proclamation", "legal_document"],
            "source_org": ["National Archives"],
        },
        limit=10,
        threshold=0.75,
    )

    client.print_results(response)


async def example_persona_search() -> None:
    """Example: Persona-driven search."""
    print("\n### Example 3: Persona-Driven Search ###")

    client = KwanzaaSearchClient()

    # Educator persona (higher threshold, primary sources)
    print("\n--- Educator Persona ---")
    response = await client.semantic_search(
        query="explain the voting rights act to students",
        persona_key="educator",
    )

    client.print_results(response)

    # Creator persona (lower threshold, all namespaces)
    print("\n--- Creator Persona ---")
    response = await client.semantic_search(
        query="inspiring quotes about civil rights",
        persona_key="creator",
    )

    client.print_results(response)


async def example_multi_tag_search() -> None:
    """Example: Search with multiple tags."""
    print("\n### Example 4: Multi-Tag Filter Search ###")

    client = KwanzaaSearchClient()

    response = await client.semantic_search(
        query="black scientists and inventors",
        namespace="kwanzaa_black_stem",
        filters={
            "tags": ["science", "biography"],
            "year_gte": 1900,
        },
        limit=20,
        threshold=0.65,
    )

    client.print_results(response)


async def example_embedding_generation() -> None:
    """Example: Generate embedding."""
    print("\n### Example 5: Embedding Generation ###")

    client = KwanzaaSearchClient()

    response = await client.generate_embedding(
        "What is the significance of the Civil Rights Act?"
    )

    print(f"\nText: {response['text']}")
    print(f"Model: {response['model']}")
    print(f"Dimensions: {response['dimensions']}")
    print(f"Generation Time: {response['generation_time_ms']}ms")
    print(f"Embedding (first 10 dims): {response['embedding'][:10]}")


async def example_list_namespaces() -> None:
    """Example: List namespaces."""
    print("\n### Example 6: List Available Namespaces ###")

    client = KwanzaaSearchClient()

    namespaces = await client.list_namespaces()

    print("\nAvailable Namespaces:")
    for ns in namespaces:
        print(f"\n- {ns['name']}")
        print(f"  Display: {ns.get('display_name', 'N/A')}")
        print(f"  Description: {ns.get('description', 'N/A')}")
        print(f"  Documents: {ns.get('document_count', 'N/A')}")
        print(f"  Chunks: {ns.get('chunk_count', 'N/A')}")


async def example_error_handling() -> None:
    """Example: Error handling."""
    print("\n### Example 7: Error Handling ###")

    client = KwanzaaSearchClient()

    # Test invalid query
    try:
        print("\n--- Testing Invalid Query (Empty) ---")
        await client.semantic_search(query="")
    except httpx.HTTPStatusError as e:
        error = e.response.json()
        print(f"Error Code: {error['error_code']}")
        print(f"Message: {error['message']}")
        if 'details' in error:
            print(f"Details: {json.dumps(error['details'], indent=2)}")

    # Test invalid limit
    try:
        print("\n--- Testing Invalid Limit ---")
        await client.semantic_search(query="test", limit=101)
    except httpx.HTTPStatusError as e:
        error = e.response.json()
        print(f"Error Code: {error['error_code']}")
        print(f"Message: {error['message']}")

    # Test invalid persona
    try:
        print("\n--- Testing Invalid Persona ---")
        await client.semantic_search(query="test", persona_key="invalid")
    except httpx.HTTPStatusError as e:
        error = e.response.json()
        print(f"Error Code: {error['error_code']}")
        print(f"Message: {error['message']}")


async def main() -> None:
    """Run all examples."""
    print("\n" + "=" * 80)
    print("KWANZAA SEMANTIC SEARCH - CLIENT EXAMPLES")
    print("=" * 80)

    examples = [
        ("Basic Search", example_basic_search),
        ("Filtered Search", example_filtered_search),
        ("Persona Search", example_persona_search),
        ("Multi-Tag Search", example_multi_tag_search),
        ("Embedding Generation", example_embedding_generation),
        ("List Namespaces", example_list_namespaces),
        ("Error Handling", example_error_handling),
    ]

    for name, example_func in examples:
        try:
            await example_func()
        except Exception as e:
            print(f"\n{name} failed: {type(e).__name__}: {str(e)}")
            print("(This is expected if the server is not running)")

    print("\n" + "=" * 80)
    print("EXAMPLES COMPLETE")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
