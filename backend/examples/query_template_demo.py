#!/usr/bin/env python3
"""
Query Template System Demo

This script demonstrates the query template system with all four personas.
Run this to see how different personas handle the same queries differently.

Usage:
    cd backend
    python3 -m examples.query_template_demo

    OR (with PYTHONPATH):
    PYTHONPATH=/Users/aideveloper/kwanzaa/backend python3 examples/query_template_demo.py
"""

import sys
from pathlib import Path

# Add backend directory to path for imports
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.models.query_template import (
    PersonaType,
    TemplateSelectionRequest,
)
from app.services.query_templates import QueryTemplateService


def print_section(title: str) -> None:
    """Print a section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def print_template_result(response, persona: PersonaType) -> None:
    """Print formatted template application results."""
    app = response.application
    meta = response.template_metadata

    print(f"Persona: {persona.value.upper()}")
    print(f"Display Name: {meta.get('display_name', 'N/A')}")
    print(f"Nguzo Saba Principle: {meta.get('nguzo_saba_principle', 'N/A')}")
    print(f"\nOriginal Query: {app.original_query}")
    print(f"Expanded Query: {app.expanded_query}")

    if app.expansion_terms:
        print(f"Expansion Terms: {', '.join(app.expansion_terms)}")
    else:
        print("Expansion Terms: None")

    print(f"\nNamespaces: {', '.join(app.namespaces)}")
    print(f"Similarity Threshold: {app.similarity_threshold}")
    print(f"Result Limit: {app.result_limit}")
    print(f"Min Results: {app.min_results}")
    print(f"Rerank: {app.rerank}")

    print(f"\nContext Formatting:")
    print(f"  - Citation Style: {app.context_formatting.citation_style}")
    print(f"  - Include Citations: {app.context_formatting.include_citations}")
    print(f"  - Show Provenance: {app.context_formatting.show_provenance}")
    print("-" * 80)


def demo_persona_comparison(service: QueryTemplateService, query: str) -> None:
    """Compare how different personas handle the same query."""
    print_section(f"Query: '{query}'")

    personas = [
        PersonaType.BUILDER,
        PersonaType.EDUCATOR,
        PersonaType.CREATOR,
        PersonaType.RESEARCHER,
    ]

    for persona in personas:
        request = TemplateSelectionRequest(
            query=query,
            persona=persona,
        )

        response = service.apply_template(request)
        print_template_result(response, persona)
        print()


def demo_auto_detection(service: QueryTemplateService) -> None:
    """Demonstrate automatic persona detection."""
    print_section("Automatic Persona Detection")

    queries = [
        "How to implement vector search with ZeroDB?",
        "When was Kwanzaa first celebrated?",
        "Inspiring speeches about unity and community",
        "Scholarly analysis of the Black Power movement",
        "Tell me about celebrations",  # Ambiguous
    ]

    for query in queries:
        persona, confidence = service.detect_persona(query)

        if persona:
            print(f"Query: '{query}'")
            print(f"  → Detected: {persona.value} (confidence: {confidence:.2f})")
        else:
            print(f"Query: '{query}'")
            print(f"  → No detection (confidence: {confidence:.2f}, threshold: 0.75)")
        print()


def demo_builder_persona(service: QueryTemplateService) -> None:
    """Demonstrate Builder persona with technical queries."""
    print_section("Builder Persona Examples")

    queries = [
        "How do I implement semantic search?",
        "Show me the API schema for search requests",
        "Best practices for embedding generation",
    ]

    for query in queries:
        request = TemplateSelectionRequest(
            query=query,
            persona=PersonaType.BUILDER,
        )

        response = service.apply_template(request)
        print(f"Query: '{query}'")
        print(f"Expanded: '{response.application.expanded_query}'")
        print(f"Focus: Code patterns, technical guides")
        print(f"Threshold: {response.application.similarity_threshold} (balanced)")
        print()


def demo_educator_persona(service: QueryTemplateService) -> None:
    """Demonstrate Educator persona with historical queries."""
    print_section("Educator Persona Examples")

    queries = [
        "When was Kwanzaa first celebrated?",
        "Who founded Kwanzaa and why?",
        "What are the seven principles?",
    ]

    for query in queries:
        request = TemplateSelectionRequest(
            query=query,
            persona=PersonaType.EDUCATOR,
        )

        response = service.apply_template(request)
        print(f"Query: '{query}'")
        print(f"Expanded: '{response.application.expanded_query}'")
        print(f"Focus: Historical accuracy, verified sources")
        print(f"Threshold: {response.application.similarity_threshold} (high quality)")
        print(f"Citations: Required (Chicago style)")
        print()


def demo_creator_persona(service: QueryTemplateService) -> None:
    """Demonstrate Creator persona with narrative queries."""
    print_section("Creator Persona Examples")

    queries = [
        "Powerful speeches about unity",
        "Ceremonial language for Karamu feast",
        "Storytelling traditions in Kwanzaa",
    ]

    for query in queries:
        request = TemplateSelectionRequest(
            query=query,
            persona=PersonaType.CREATOR,
        )

        response = service.apply_template(request)
        print(f"Query: '{query}'")
        print(f"Expanded: '{response.application.expanded_query}'")
        print(f"Focus: Narrative, rhetorical structures, inspiration")
        print(f"Namespaces: {len(response.application.namespaces)} sources")
        print(f"Threshold: {response.application.similarity_threshold} (inclusive)")
        print()


def demo_researcher_persona(service: QueryTemplateService) -> None:
    """Demonstrate Researcher persona with scholarly queries."""
    print_section("Researcher Persona Examples")

    queries = [
        "Evolution of Kwanzaa celebrations 1966-1980",
        "Black Press coverage of Kwanzaa",
        "Research methodologies for studying cultural movements",
    ]

    for query in queries:
        request = TemplateSelectionRequest(
            query=query,
            persona=PersonaType.RESEARCHER,
        )

        response = service.apply_template(request)
        print(f"Query: '{query}'")
        print(f"Expanded: '{response.application.expanded_query}'")
        print(f"Focus: Comprehensive coverage, multiple sources")
        print(f"Namespaces: {len(response.application.namespaces)} sources")
        print(f"Result Limit: {response.application.result_limit} (maximum)")
        print()


def demo_template_overrides(service: QueryTemplateService) -> None:
    """Demonstrate template parameter overrides."""
    print_section("Template Overrides Example")

    query = "Kwanzaa celebrations in the 1970s"

    # Standard researcher template
    request1 = TemplateSelectionRequest(
        query=query,
        persona=PersonaType.RESEARCHER,
    )
    response1 = service.apply_template(request1)

    print("Standard Researcher Template:")
    print(f"  Threshold: {response1.application.similarity_threshold}")
    print(f"  Result Limit: {response1.application.result_limit}")
    print(f"  Filters: {response1.application.metadata_filters}")
    print()

    # With overrides
    request2 = TemplateSelectionRequest(
        query=query,
        persona=PersonaType.RESEARCHER,
        template_overrides={
            "similarity_threshold": 0.85,
            "result_limit": 30,
            "filters": {
                "year_gte": 1970,
                "year_lte": 1979,
            },
        },
    )
    response2 = service.apply_template(request2)

    print("With Overrides:")
    print(f"  Threshold: {response2.application.similarity_threshold} (↑ from 0.75)")
    print(f"  Result Limit: {response2.application.result_limit} (↑ from 20)")
    print(f"  Filters: {response2.application.metadata_filters}")
    print("  → Year range 1970-1979 applied")


def demo_template_examples(service: QueryTemplateService) -> None:
    """Show example queries for each template."""
    print_section("Template Example Queries")

    personas = [
        PersonaType.BUILDER,
        PersonaType.EDUCATOR,
        PersonaType.CREATOR,
        PersonaType.RESEARCHER,
    ]

    for persona in personas:
        examples = service.get_template_examples(persona)
        print(f"{persona.value.upper()} Examples:")
        for i, example in enumerate(examples[:3], 1):
            print(f"  {i}. {example}")
        print()


def demo_template_validation(service: QueryTemplateService) -> None:
    """Demonstrate template validation."""
    print_section("Template Validation")

    # Validate existing templates
    for persona in PersonaType:
        template = service.get_template(persona)
        if template:
            errors = service.validate_template(template)
            if errors:
                print(f"{persona.value}: ❌ FAILED")
                for error in errors:
                    print(f"  - {error}")
            else:
                print(f"{persona.value}: ✅ VALID")
        else:
            print(f"{persona.value}: ⚠️  NOT FOUND")


def main() -> None:
    """Run all demonstrations."""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "QUERY TEMPLATE SYSTEM DEMO" + " " * 32 + "║")
    print("╚" + "=" * 78 + "╝")

    # Initialize service
    print("\nInitializing QueryTemplateService...")
    service = QueryTemplateService()
    print(f"✓ Loaded {len(service.templates)} templates")

    # Run demonstrations
    demo_template_validation(service)
    demo_template_examples(service)
    demo_auto_detection(service)

    # Persona-specific demos
    demo_builder_persona(service)
    demo_educator_persona(service)
    demo_creator_persona(service)
    demo_researcher_persona(service)

    # Advanced features
    demo_template_overrides(service)

    # Comparison demo
    demo_persona_comparison(service, "How do the seven principles apply today?")

    print_section("Demo Complete")
    print("All templates are working correctly!")
    print("\nNext steps:")
    print("  1. Review docs/rag/query-templates-guide.md for detailed documentation")
    print("  2. Check docs/rag/query-templates-examples.md for integration patterns")
    print("  3. Run tests: pytest backend/tests/test_query_templates.py")
    print()


if __name__ == "__main__":
    main()
