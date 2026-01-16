# Query Template System - Working Examples

This document provides practical, copy-paste examples of the query template system in action for each persona type.

## Table of Contents

1. [Builder Persona Examples](#builder-persona-examples)
2. [Educator Persona Examples](#educator-persona-examples)
3. [Creator Persona Examples](#creator-persona-examples)
4. [Researcher Persona Examples](#researcher-persona-examples)
5. [Integration Examples](#integration-examples)

---

## Builder Persona Examples

### Example 1: API Documentation Search

```python
from app.services.query_templates import QueryTemplateService
from app.models.query_template import TemplateSelectionRequest, PersonaType

service = QueryTemplateService()

# User query: "How do I use the ZeroDB vector search API?"
request = TemplateSelectionRequest(
    query="How do I use the ZeroDB vector search API?",
    persona=PersonaType.BUILDER
)

response = service.apply_template(request)

print(f"Original Query: {response.application.original_query}")
print(f"Expanded Query: {response.application.expanded_query}")
print(f"Expansion Terms: {response.application.expansion_terms}")
print(f"Namespaces: {response.application.namespaces}")
print(f"Threshold: {response.application.similarity_threshold}")

# Output:
# Original Query: How do I use the ZeroDB vector search API?
# Expanded Query: How do I use the ZeroDB vector search API? endpoint interface
# Expansion Terms: ['endpoint', 'interface']
# Namespaces: ['kwanzaa_dev_patterns']
# Threshold: 0.70
```

### Example 2: Schema Definition Search

```python
request = TemplateSelectionRequest(
    query="What's the schema for search requests?",
    persona=PersonaType.BUILDER
)

response = service.apply_template(request)

# Query gets expanded with: model, structure, definition, format
# Content filters applied: code_example, technical_guide, api_documentation, schema_definition
# Result: Technical documentation with code examples
```

### Example 3: Implementation Pattern Search

```python
request = TemplateSelectionRequest(
    query="Best practices for embedding generation",
    persona=PersonaType.BUILDER
)

response = service.apply_template(request)

# Query expansion adds: vector, representation, encoding, semantic
# Tags preferred: implementation, pattern, best-practice, api
# Result limit: 10 (focused technical results)
```

---

## Educator Persona Examples

### Example 1: Historical Facts Search

```python
request = TemplateSelectionRequest(
    query="When was Kwanzaa first celebrated?",
    persona=PersonaType.EDUCATOR
)

response = service.apply_template(request)

print(f"Original Query: {response.application.original_query}")
print(f"Expanded Query: {response.application.expanded_query}")
print(f"Namespaces: {response.application.namespaces}")
print(f"Threshold: {response.application.similarity_threshold}")
print(f"Rerank: {response.application.rerank}")
print(f"Citations: {response.application.context_formatting.include_citations}")

# Output:
# Original Query: When was Kwanzaa first celebrated?
# Expanded Query: When was Kwanzaa first celebrated? African American holiday cultural celebration seven principles Nguzo Saba
# Namespaces: ['kwanzaa_primary_sources']
# Threshold: 0.80 (high quality requirement)
# Rerank: True
# Citations: True (Chicago style)
```

### Example 2: Founder Information

```python
request = TemplateSelectionRequest(
    query="Who created Kwanzaa and why?",
    persona=PersonaType.EDUCATOR
)

response = service.apply_template(request)

# Query expansion adds: Maulana Karenga, Dr. Karenga, creator, originator
# Content types: historical_document, archival_material, primary_source
# Tags required: verified
# Min results: 3 (ensure sufficient coverage)
# Provenance: Shown in results
```

### Example 3: Principles Explanation

```python
request = TemplateSelectionRequest(
    query="What are the seven principles of Kwanzaa?",
    persona=PersonaType.EDUCATOR
)

response = service.apply_template(request)

# Query expansion adds: Umoja, Kujichagulia, Ujima, Ujamaa, Nia, Kuumba, Imani
# Only primary sources used
# High similarity threshold (0.80) ensures accuracy
# Citations required for lesson planning
```

---

## Creator Persona Examples

### Example 1: Inspirational Speech Search

```python
request = TemplateSelectionRequest(
    query="Powerful speeches about unity and community",
    persona=PersonaType.CREATOR
)

response = service.apply_template(request)

print(f"Original Query: {response.application.original_query}")
print(f"Expanded Query: {response.application.expanded_query}")
print(f"Namespaces: {response.application.namespaces}")
print(f"Result Limit: {response.application.result_limit}")
print(f"Citation Style: {response.application.context_formatting.citation_style}")

# Output:
# Original Query: Powerful speeches about unity and community
# Expanded Query: Powerful speeches about unity and community togetherness solidarity collective
# Namespaces: ['kwanzaa_primary_sources', 'kwanzaa_speeches_letters', 'kwanzaa_teaching_kits']
# Result Limit: 15 (broader inspiration)
# Citation Style: mla
```

### Example 2: Narrative Elements Search

```python
request = TemplateSelectionRequest(
    query="Storytelling traditions in Kwanzaa celebrations",
    persona=PersonaType.CREATOR
)

response = service.apply_template(request)

# Multiple namespaces for diverse inspiration
# Lower threshold (0.65) for more inclusive results
# Tags preferred: inspirational, narrative, rhetorical, cultural
# No reranking (embrace diversity)
```

### Example 3: Ceremonial Content

```python
request = TemplateSelectionRequest(
    query="Traditional language for Karamu feast ceremony",
    persona=PersonaType.CREATOR
)

response = service.apply_template(request)

# Searches: primary_sources, speeches_letters, teaching_kits
# Content types: speech, letter, educational_resource, ceremonial
# Diversity factor: 0.7 (high diversity for creative inspiration)
```

---

## Researcher Persona Examples

### Example 1: Historical Evolution Study

```python
request = TemplateSelectionRequest(
    query="Evolution of Kwanzaa celebrations 1966-1980",
    persona=PersonaType.RESEARCHER,
    template_overrides={
        "filters": {
            "year_gte": 1966,
            "year_lte": 1980
        }
    }
)

response = service.apply_template(request)

print(f"Original Query: {response.application.original_query}")
print(f"Namespaces: {response.application.namespaces}")
print(f"Result Limit: {response.application.result_limit}")
print(f"Metadata Filters: {response.application.metadata_filters}")
print(f"Provenance: {response.application.context_formatting.show_provenance}")

# Output:
# Original Query: Evolution of Kwanzaa celebrations 1966-1980
# Namespaces: ['kwanzaa_primary_sources', 'kwanzaa_black_press', 'kwanzaa_speeches_letters', 'kwanzaa_black_stem']
# Result Limit: 20 (comprehensive coverage)
# Metadata Filters: {'year_gte': 1966, 'year_lte': 1980, ...}
# Provenance: True (full source metadata)
```

### Example 2: Multi-Source Analysis

```python
request = TemplateSelectionRequest(
    query="Black Press coverage of Kwanzaa in the 1970s",
    persona=PersonaType.RESEARCHER
)

response = service.apply_template(request)

# Four namespaces searched: primary_sources, black_press, speeches_letters, black_stem
# Query expansion adds: examination, investigation, study, documentation
# Content types: historical_document, newspaper_article, periodical, speech, letter
# Min results: 5 (ensure depth)
# Reranking enabled for relevance
```

### Example 3: Scholarly Methodology

```python
request = TemplateSelectionRequest(
    query="Research methodologies for studying African American cultural movements",
    persona=PersonaType.RESEARCHER
)

response = service.apply_template(request)

# Query expansion adds: approach, framework, method, protocol
# Tags preferred: peer-reviewed, archival, scholarly, primary-source
# Comprehensive namespace coverage
# Chicago citation style for academic work
```

---

## Integration Examples

### Example 1: Complete Search Workflow

```python
from app.services.search import SearchService
from app.services.query_templates import QueryTemplateService
from app.models.search import SearchRequest
from app.models.query_template import TemplateSelectionRequest, PersonaType

# Initialize services
search_service = SearchService()
template_service = QueryTemplateService()

async def template_based_search(query: str, persona: PersonaType):
    """Perform search using query templates."""

    # Step 1: Apply template
    template_request = TemplateSelectionRequest(
        query=query,
        persona=persona
    )
    template_response = template_service.apply_template(template_request)

    # Step 2: Build search request from template
    search_request = SearchRequest(
        query=template_response.application.expanded_query,
        namespace=template_response.application.namespaces[0],
        threshold=template_response.application.similarity_threshold,
        limit=template_response.application.result_limit
    )

    # Step 3: Execute search
    results = await search_service.search(search_request, zerodb_search_func)

    # Step 4: Return with template metadata
    return {
        "results": results,
        "template_info": {
            "persona": persona.value,
            "original_query": template_response.application.original_query,
            "expanded_query": template_response.application.expanded_query,
            "expansion_terms": template_response.application.expansion_terms
        }
    }

# Use it
results = await template_based_search(
    "When was Kwanzaa founded?",
    PersonaType.EDUCATOR
)
```

### Example 2: Auto-Detection with Fallback

```python
async def smart_search(query: str):
    """Search with automatic persona detection."""

    # Try to detect persona
    persona, confidence = template_service.detect_persona(query)

    if persona and confidence >= 0.75:
        print(f"Auto-detected {persona.value} persona (confidence: {confidence:.2f})")
    else:
        # Fall back to educator (safe default)
        persona = PersonaType.EDUCATOR
        print("Using default educator persona")

    # Apply template and search
    response = await search_service.search_with_template(
        query=query,
        persona=persona,
        zerodb_search_func=zerodb_search_func
    )

    return response

# Example queries with auto-detection
await smart_search("How to implement search?")  # → Builder
await smart_search("Who founded Kwanzaa?")      # → Educator
await smart_search("Inspiring unity quotes")    # → Creator
await smart_search("Scholarly analysis")         # → Researcher
```

### Example 3: Template Override for Specific Needs

```python
async def historical_range_search(query: str, start_year: int, end_year: int):
    """Search within specific historical period."""

    response = await search_service.search_with_template(
        query=query,
        persona=PersonaType.RESEARCHER,
        template_overrides={
            "filters": {
                "year_gte": start_year,
                "year_lte": end_year
            },
            "result_limit": 30,  # More results for comprehensive study
            "similarity_threshold": 0.70  # Lower for broader coverage
        },
        zerodb_search_func=zerodb_search_func
    )

    return response

# Study Kwanzaa in the 1970s
results = await historical_range_search(
    "Kwanzaa celebrations and community adoption",
    start_year=1970,
    end_year=1979
)
```

### Example 4: Multi-Persona Comparison

```python
async def compare_persona_results(query: str):
    """Compare results across different personas."""

    personas = [
        PersonaType.BUILDER,
        PersonaType.EDUCATOR,
        PersonaType.CREATOR,
        PersonaType.RESEARCHER
    ]

    results = {}

    for persona in personas:
        response = await search_service.search_with_template(
            query=query,
            persona=persona,
            zerodb_search_func=zerodb_search_func
        )

        results[persona.value] = {
            "result_count": len(response["search_response"].results),
            "namespaces": response["retrieval_configuration"]["namespaces"],
            "threshold": response["retrieval_configuration"]["similarity_threshold"],
            "expansion_terms": response["query_expansion"]["expansion_terms"]
        }

    return results

# Compare how different personas handle same query
comparison = await compare_persona_results("Kwanzaa principles")
```

### Example 5: Custom Template Validation

```python
def validate_custom_template(template):
    """Validate a custom template before deployment."""

    errors = template_service.validate_template(template)

    if errors:
        print("Template validation errors:")
        for error in errors:
            print(f"  - {error}")
        return False

    print("Template is valid!")

    # Test with example queries
    if template.example_queries:
        print("\nTesting example queries:")
        for example in template.example_queries[:3]:
            request = TemplateSelectionRequest(
                query=example,
                persona=template.persona
            )
            response = template_service.apply_template(request)
            print(f"  ✓ '{example}' → {len(response.application.expansion_terms)} terms added")

    return True
```

---

## Performance Monitoring

### Example: Track Query Expansion Effectiveness

```python
async def search_with_analytics(query: str, persona: PersonaType):
    """Search with performance analytics."""

    import time
    start = time.time()

    # Apply template
    template_start = time.time()
    template_request = TemplateSelectionRequest(query=query, persona=persona)
    template_response = template_service.apply_template(template_request)
    template_time = time.time() - template_start

    # Search
    search_start = time.time()
    response = await search_service.search_with_template(
        query=query,
        persona=persona,
        zerodb_search_func=zerodb_search_func
    )
    search_time = time.time() - search_start

    total_time = time.time() - start

    # Analytics
    analytics = {
        "query": query,
        "persona": persona.value,
        "timing": {
            "template_application_ms": int(template_time * 1000),
            "search_execution_ms": int(search_time * 1000),
            "total_ms": int(total_time * 1000)
        },
        "expansion": {
            "original_length": len(query),
            "expanded_length": len(template_response.application.expanded_query),
            "terms_added": len(template_response.application.expansion_terms),
            "expansion_rate": len(template_response.application.expansion_terms) / len(query.split())
        },
        "results": {
            "count": len(response["search_response"].results),
            "avg_score": sum(r.score for r in response["search_response"].results) /
                        len(response["search_response"].results) if response["search_response"].results else 0,
            "namespaces_used": len(template_response.application.namespaces)
        }
    }

    return response, analytics

# Track effectiveness
result, stats = await search_with_analytics(
    "How to implement vector search?",
    PersonaType.BUILDER
)

print(f"Template application: {stats['timing']['template_application_ms']}ms")
print(f"Search execution: {stats['timing']['search_execution_ms']}ms")
print(f"Expansion rate: {stats['expansion']['expansion_rate']:.2f} terms per word")
print(f"Results found: {stats['results']['count']}")
print(f"Average score: {stats['results']['avg_score']:.3f}")
```

---

## Troubleshooting Examples

### Problem: Too Few Results

```python
# Original query gets no results
request = TemplateSelectionRequest(
    query="Obscure historical detail",
    persona=PersonaType.EDUCATOR
)

# Solution 1: Lower threshold
request_relaxed = TemplateSelectionRequest(
    query="Obscure historical detail",
    persona=PersonaType.EDUCATOR,
    template_overrides={
        "similarity_threshold": 0.65  # Lower from 0.80
    }
)

# Solution 2: Use researcher persona (more namespaces)
request_broad = TemplateSelectionRequest(
    query="Obscure historical detail",
    persona=PersonaType.RESEARCHER  # Searches 4 namespaces instead of 1
)
```

### Problem: Results Too Broad

```python
# Original query gets too many unrelated results
request = TemplateSelectionRequest(
    query="Kwanzaa celebrations",
    persona=PersonaType.CREATOR
)

# Solution: Add metadata filters
request_focused = TemplateSelectionRequest(
    query="Kwanzaa celebrations",
    persona=PersonaType.CREATOR,
    template_overrides={
        "filters": {
            "content_type": ["speech", "letter"],  # Limit content types
            "year_gte": 1990  # Modern celebrations only
        },
        "similarity_threshold": 0.75  # Higher threshold
    }
)
```

---

## Summary

The query template system provides:

1. **Persona-Specific Behavior**: Each persona has distinct retrieval characteristics
2. **Automatic Query Enhancement**: Strategy-based expansion improves recall
3. **Flexible Configuration**: Override any parameter for specific needs
4. **Transparent Operation**: Full visibility into template application
5. **Performance Optimization**: Caching and smart namespace selection

All examples above are production-ready and can be adapted to your specific use cases.
