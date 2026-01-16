"""RAG Pipeline Usage Examples.

This module demonstrates how to use the RAG pipeline for retrieval-augmented generation.
"""

import asyncio
from typing import List

from app.models.retrieval import RAGQueryRequest, RAGPipelineResponse, RetrievalChunk
from app.services.rag_pipeline import RAGPipeline


async def example_basic_query():
    """Example 1: Basic query with educator persona."""
    print("\n" + "=" * 80)
    print("Example 1: Basic Query with Educator Persona")
    print("=" * 80)

    # Initialize pipeline
    async with RAGPipeline() as pipeline:
        # Create query request
        request = RAGQueryRequest(
            query="What were the Seven Principles of Kwanzaa?",
            persona_key="educator",
        )

        # Execute pipeline
        response = await pipeline.process(request)

        # Display results
        print(f"\nQuery: {response.query}")
        print(f"Persona: {response.persona}")
        print(f"Chunks Retrieved: {len(response.chunks)}")
        print(f"Top Score: {response.statistics.top_score:.3f}")
        print(f"Total Time: {response.statistics.total_time_ms}ms")
        print(f"Reranking Enabled: {response.reranking_enabled}")

        # Show top 3 results
        print("\nTop 3 Results:")
        for chunk in response.chunks[:3]:
            print(f"\n  Rank {chunk.rank}: {chunk.citation_label}")
            print(f"  Score: {chunk.final_score or chunk.score:.3f}")
            print(f"  Year: {chunk.year}")
            print(f"  Content: {chunk.content[:100]}...")


async def example_researcher_with_filters():
    """Example 2: Researcher persona with metadata filters."""
    print("\n" + "=" * 80)
    print("Example 2: Researcher Persona with Filters")
    print("=" * 80)

    async with RAGPipeline() as pipeline:
        # Query with temporal and content type filters
        request = RAGQueryRequest(
            query="Civil rights legislation and its impact",
            persona_key="researcher",
            filters={
                "year_gte": 1960,
                "year_lte": 1970,
                "content_type": ["legal_document", "speech"],
            },
            top_k=20,
            enable_reranking=True,
            rerank_top_n=10,
        )

        response = await pipeline.process(request)

        print(f"\nQuery: {response.query}")
        print(f"Namespaces Searched: {', '.join(response.statistics.namespaces_searched)}")
        print(f"Filters Applied: {response.statistics.filters_applied}")
        print(f"Total Retrieved: {response.statistics.total_retrieved}")
        print(f"After Reranking: {len(response.chunks)}")
        print(f"Average Score: {response.statistics.average_score:.3f}")

        # Show timing breakdown
        print("\nTiming Breakdown:")
        print(f"  Embedding: {response.statistics.embedding_time_ms}ms")
        print(f"  Search: {response.statistics.search_time_ms}ms")
        print(f"  Reranking: {response.statistics.rerank_time_ms}ms")
        print(f"  Total: {response.statistics.total_time_ms}ms")


async def example_custom_namespaces():
    """Example 3: Custom namespace selection for cross-collection search."""
    print("\n" + "=" * 80)
    print("Example 3: Custom Namespace Selection")
    print("=" * 80)

    async with RAGPipeline() as pipeline:
        # Search across multiple custom namespaces
        request = RAGQueryRequest(
            query="Historical contributions to science and technology",
            persona_key="researcher",
            namespaces=[
                "kwanzaa_black_stem",
                "kwanzaa_primary_sources",
                "kwanzaa_speeches_letters",
            ],
            similarity_threshold=0.75,
            enable_reranking=True,
        )

        response = await pipeline.process(request)

        print(f"\nQuery: {response.query}")
        print(f"Searched Namespaces: {response.statistics.namespaces_searched}")
        print(f"Results Found: {len(response.chunks)}")

        # Show namespace distribution
        namespace_counts = {}
        for chunk in response.chunks:
            namespace_counts[chunk.namespace] = namespace_counts.get(chunk.namespace, 0) + 1

        print("\nResults by Namespace:")
        for namespace, count in namespace_counts.items():
            print(f"  {namespace}: {count} chunks")


async def example_context_injection():
    """Example 4: Generate formatted context for LLM injection."""
    print("\n" + "=" * 80)
    print("Example 4: Context String for LLM Injection")
    print("=" * 80)

    async with RAGPipeline() as pipeline:
        request = RAGQueryRequest(
            query="Explain the principle of Ujima (Collective Work)",
            persona_key="educator",
            include_context_string=True,
        )

        response = await pipeline.process(request)

        # Access formatted context
        if response.context_string:
            print(f"\nContext Summary:")
            print(f"  Chunks Included: {response.context_string.num_chunks}")
            print(f"  Estimated Tokens: {response.context_string.total_tokens}")
            print(f"  Max Score: {response.context_string.max_chunk_score:.3f}")

            print("\nFormatted Context (first 500 chars):")
            print("-" * 80)
            print(response.context_string.formatted_context[:500])
            print("...")
            print("-" * 80)

            # This context can now be injected into an LLM prompt
            system_prompt = f"""You are an AI assistant specializing in Kwanzaa history.
Use the following retrieved context to answer the user's question.
Always cite sources using the provided citation labels.

{response.context_string.formatted_context}
"""
            print("\nSystem prompt ready for LLM (length: {} chars)".format(len(system_prompt)))


async def example_creative_persona():
    """Example 5: Creative persona for diverse results without reranking."""
    print("\n" + "=" * 80)
    print("Example 5: Creative Persona")
    print("=" * 80)

    async with RAGPipeline() as pipeline:
        request = RAGQueryRequest(
            query="Inspiration for celebrating community and heritage",
            persona_key="creator",
        )

        response = await pipeline.process(request)

        print(f"\nQuery: {response.query}")
        print(f"Persona: {response.persona}")
        print(f"Similarity Threshold: {response.persona_thresholds.similarity_threshold}")
        print(f"Reranking: {response.reranking_enabled}")
        print(f"Results: {len(response.chunks)}")

        # Creator persona has lower threshold and no reranking for diverse results
        print("\nDiverse Content Types:")
        content_types = set(chunk.content_type for chunk in response.chunks)
        for content_type in content_types:
            print(f"  - {content_type}")


async def example_statistics_and_transparency():
    """Example 6: Access detailed retrieval statistics for transparency."""
    print("\n" + "=" * 80)
    print("Example 6: Retrieval Statistics and Transparency")
    print("=" * 80)

    async with RAGPipeline() as pipeline:
        request = RAGQueryRequest(
            query="The history of Black excellence in America",
            persona_key="researcher",
            enable_reranking=True,
        )

        response = await pipeline.process(request)

        # Access comprehensive statistics
        stats = response.statistics

        print("\n=== Retrieval Statistics ===")
        print(f"\nVolume Metrics:")
        print(f"  Total Retrieved: {stats.total_retrieved}")
        print(f"  Total Reranked: {stats.total_reranked}")
        print(f"  Total Returned: {stats.total_returned}")

        print(f"\nQuality Metrics:")
        print(f"  Top Score: {stats.top_score:.3f}")
        print(f"  Average Score: {stats.average_score:.3f}")

        print(f"\nExecution Details:")
        print(f"  Namespaces: {', '.join(stats.namespaces_searched)}")
        print(f"  Filters: {stats.filters_applied or 'None'}")
        print(f"  Embedding Model: {response.embedding_model}")
        if response.rerank_model:
            print(f"  Rerank Model: {response.rerank_model}")

        print(f"\nTiming Metrics:")
        print(f"  Embedding Time: {stats.embedding_time_ms}ms")
        print(f"  Search Time: {stats.search_time_ms}ms")
        print(f"  Rerank Time: {stats.rerank_time_ms}ms")
        print(f"  Total Time: {stats.total_time_ms}ms")

        # Calculate percentages
        if stats.total_time_ms > 0:
            embed_pct = (stats.embedding_time_ms / stats.total_time_ms) * 100
            search_pct = (stats.search_time_ms / stats.total_time_ms) * 100
            rerank_pct = (stats.rerank_time_ms / stats.total_time_ms) * 100

            print(f"\nTime Distribution:")
            print(f"  Embedding: {embed_pct:.1f}%")
            print(f"  Search: {search_pct:.1f}%")
            print(f"  Reranking: {rerank_pct:.1f}%")


async def example_integration_with_answer_json():
    """Example 7: Integration with answer_json contract."""
    print("\n" + "=" * 80)
    print("Example 7: Integration with Answer JSON Contract")
    print("=" * 80)

    async with RAGPipeline() as pipeline:
        request = RAGQueryRequest(
            query="What was the significance of the March on Washington?",
            persona_key="educator",
            enable_reranking=True,
        )

        response = await pipeline.process(request)

        print("\n=== Mapping to Answer JSON Contract ===\n")

        # Simulate conversion to answer_json sources
        print(f"Sources Array ({len(response.chunks)} items):")
        for i, chunk in enumerate(response.chunks[:3], 1):
            print(f"\n  Source {i}:")
            print(f"    citation_label: {chunk.citation_label}")
            print(f"    canonical_url: {chunk.canonical_url}")
            print(f"    source_org: {chunk.source_org}")
            print(f"    year: {chunk.year}")
            print(f"    content_type: {chunk.content_type}")
            print(f"    namespace: {chunk.namespace}")
            print(f"    relevance_score: {chunk.final_score or chunk.score:.3f}")

        # Simulate conversion to retrieval_summary
        print(f"\nRetrieval Summary:")
        print(f"  query: {response.query}")
        print(f"  top_k: {len(response.chunks)}")
        print(f"  namespaces: {response.statistics.namespaces_searched}")
        print(f"  execution_time_ms: {response.statistics.total_time_ms}")
        print(f"  embedding_model: {response.embedding_model}")

        print("\n  results (top 2):")
        for chunk in response.chunks[:2]:
            print(f"    - rank: {chunk.rank}")
            print(f"      score: {chunk.final_score or chunk.score:.3f}")
            print(f"      snippet: {chunk.content[:80]}...")
            print(f"      citation_label: {chunk.citation_label}")


async def main():
    """Run all examples."""
    print("\n" + "=" * 80)
    print("RAG PIPELINE USAGE EXAMPLES")
    print("=" * 80)

    examples = [
        ("Basic Query", example_basic_query),
        ("Researcher with Filters", example_researcher_with_filters),
        ("Custom Namespaces", example_custom_namespaces),
        ("Context Injection", example_context_injection),
        ("Creative Persona", example_creative_persona),
        ("Statistics", example_statistics_and_transparency),
        ("Answer JSON Integration", example_integration_with_answer_json),
    ]

    print("\nNote: These examples require a running ZeroDB instance with indexed content.")
    print("If ZeroDB is not available, they will use mock data or fail gracefully.\n")

    for name, example_func in examples:
        try:
            await example_func()
        except Exception as e:
            print(f"\nExample '{name}' failed: {str(e)}")
            print("This is expected if ZeroDB is not configured or populated.\n")

    print("\n" + "=" * 80)
    print("Examples complete!")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
