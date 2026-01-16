# Query Templates Guide

## Overview

The Kwanzaa Query Template system provides persona-specific retrieval strategies that tailor semantic search to different user needs. Each persona has distinct query processing, namespace priorities, and context formatting preferences aligned with the Nguzo Saba (Seven Principles).

## Architecture

```
User Query + Persona
        ↓
Template Selection
        ↓
Query Expansion (strategy-specific)
        ↓
Metadata Filter Application
        ↓
Retrieval Parameter Configuration
        ↓
Context Formatting Preferences
        ↓
Search Execution
```

## Four Persona Types

### 1. Builder Persona

**Purpose**: Developers and technical professionals seeking code patterns, schemas, and implementation examples.

**Nguzo Saba Principle**: Kujichagulia (Self-Determination) - Empowering builders to learn and create independently.

**Configuration**:
- **Namespace**: `kwanzaa_dev_patterns` (exclusive focus)
- **Expansion Strategy**: Technical - extracts API patterns, code terms
- **Similarity Threshold**: 0.70 (balanced for code similarity)
- **Result Limit**: 10 results
- **Reranking**: Disabled (trust vector similarity)
- **Citations**: Not required (focus on implementation)

**Content Types**:
- Code examples
- Technical guides
- API documentation
- Schema definitions

**Example Queries**:
```
- "How do I implement semantic search with ZeroDB?"
- "Show me the API schema for search requests"
- "What's the best pattern for embedding generation?"
- "How to structure metadata for provenance tracking?"
- "Example code for persona-based retrieval"
```

**Query Expansion**:
- `api` → adds: endpoint, interface, rest, graphql
- `schema` → adds: model, structure, definition, format
- `embedding` → adds: vector, representation, encoding, semantic
- `search` → adds: retrieval, query, ranking, relevance

**Use Cases**:
1. Learning platform APIs
2. Understanding data schemas
3. Finding implementation patterns
4. Exploring code examples
5. Technical troubleshooting

---

### 2. Educator Persona

**Purpose**: Teachers and educational professionals seeking historically accurate, citation-backed content.

**Nguzo Saba Principle**: Imani (Faith) - Maintaining trust through accurate, verifiable historical information.

**Configuration**:
- **Namespace**: `kwanzaa_primary_sources` (primary sources only)
- **Expansion Strategy**: Historical - extracts dates, figures, timeline context
- **Similarity Threshold**: 0.80 (high quality required)
- **Result Limit**: 10 results
- **Min Results**: 3 (ensure sufficient coverage)
- **Reranking**: Enabled (improve relevance)
- **Citations**: Required (Chicago style)

**Content Types**:
- Historical documents
- Archival materials
- Primary sources
- Verified educational content

**Metadata Filters**:
- Tags required: `verified`
- Tags preferred: `educational`, `factual`, `historical`

**Example Queries**:
```
- "When was Kwanzaa first celebrated?"
- "Who founded Kwanzaa and why?"
- "What are the seven principles of Kwanzaa?"
- "Historical context of the Black Power movement"
- "Primary sources about Maulana Karenga"
```

**Query Expansion**:
- `kwanzaa` → adds: African American holiday, cultural celebration, seven principles, Nguzo Saba
- `founder` → adds: Maulana Karenga, Dr. Karenga, creator, originator
- `principles` → adds: Umoja, Kujichagulia, Ujima, Ujamaa, Nia, Kuumba, Imani
- `movement` → adds: Black Power, Civil Rights, cultural nationalism

**Use Cases**:
1. Lesson planning
2. Student research assistance
3. Fact verification
4. Historical context retrieval
5. Creating accurate educational materials

---

### 3. Creator Persona

**Purpose**: Content creators and writers seeking rhetorical structures, narrative elements, and cultural inspiration.

**Nguzo Saba Principle**: Kuumba (Creativity) - Inspiring creative expression grounded in cultural authenticity.

**Configuration**:
- **Namespaces**:
  1. `kwanzaa_primary_sources`
  2. `kwanzaa_speeches_letters`
  3. `kwanzaa_teaching_kits`
- **Expansion Strategy**: Thematic - extracts themes, emotional context, storytelling elements
- **Similarity Threshold**: 0.65 (more inclusive for inspiration)
- **Result Limit**: 15 results (broader coverage)
- **Min Results**: 2
- **Reranking**: Disabled (embrace diversity)
- **Citations**: Optional (MLA style)
- **Diversity Factor**: 0.7 (high diversity)

**Content Types**:
- Speeches
- Letters and correspondence
- Historical documents
- Educational resources
- Ceremonial materials

**Metadata Filters**:
- Tags preferred: `inspirational`, `narrative`, `rhetorical`, `cultural`, `ceremonial`

**Example Queries**:
```
- "Powerful speeches about unity and collective work"
- "Narrative structures in Kwanzaa storytelling"
- "Ceremonial language for Karamu feast"
- "Themes of self-determination in African American literature"
- "Inspirational quotes about cultural identity"
```

**Query Expansion**:
- `unity` → adds: togetherness, solidarity, collective, community
- `heritage` → adds: ancestry, tradition, legacy, roots
- `creativity` → adds: innovation, expression, artistry, imagination
- `purpose` → adds: mission, goal, vision, calling

**Use Cases**:
1. Writing speeches or presentations
2. Creating cultural content
3. Finding narrative inspiration
4. Developing ceremonial materials
5. Storytelling and creative writing

---

### 4. Researcher Persona

**Purpose**: Scholars and researchers requiring comprehensive source coverage with metadata-first approach.

**Nguzo Saba Principle**: Ujima (Collective Work and Responsibility) - Supporting rigorous scholarship for community benefit.

**Configuration**:
- **Namespaces** (comprehensive):
  1. `kwanzaa_primary_sources`
  2. `kwanzaa_black_press`
  3. `kwanzaa_speeches_letters`
  4. `kwanzaa_black_stem`
- **Expansion Strategy**: Research - extracts research questions, methodology terms
- **Similarity Threshold**: 0.75 (balanced for comprehensive coverage)
- **Result Limit**: 20 results (maximum coverage)
- **Min Results**: 5 (ensure depth)
- **Reranking**: Enabled (relevance optimization)
- **Citations**: Required (Chicago style)
- **Show Provenance**: Enabled (full metadata)
- **Diversity Factor**: 0.6 (balanced)

**Content Types**:
- Historical documents
- Newspaper articles
- Periodicals
- Speeches and letters
- Scientific papers
- Archival materials

**Metadata Filters**:
- Tags preferred: `peer-reviewed`, `archival`, `scholarly`, `primary-source`, `historical`

**Example Queries**:
```
- "Evolution of Kwanzaa celebrations 1966-1980"
- "Academic discourse on African American cultural movements"
- "Primary sources from the Black Press about Kwanzaa"
- "Scholarly analysis of the Nguzo Saba principles"
- "Historical methodology for studying cultural holidays"
```

**Query Expansion**:
- `methodology` → adds: approach, framework, method, protocol
- `analysis` → adds: examination, investigation, study, research
- `evidence` → adds: source, citation, reference, documentation
- `context` → adds: background, setting, circumstances, environment

**Use Cases**:
1. Academic research
2. Literature reviews
3. Historical analysis
4. Scholarly writing
5. Comprehensive source compilation

---

## API Usage

### Basic Template Application

```python
from app.services.query_templates import QueryTemplateService
from app.models.query_template import TemplateSelectionRequest, PersonaType

# Initialize service
template_service = QueryTemplateService()

# Apply template
request = TemplateSelectionRequest(
    query="When was Kwanzaa first celebrated?",
    persona=PersonaType.EDUCATOR
)

response = template_service.apply_template(request)

# Extract search parameters
search_params = {
    "query": response.application.expanded_query,
    "namespaces": response.application.namespaces,
    "similarity_threshold": response.application.similarity_threshold,
    "result_limit": response.application.result_limit,
    "metadata_filters": response.application.metadata_filters,
    "rerank": response.application.rerank
}
```

### Auto-Detection of Persona

```python
# Detect persona from query
query = "How to implement the search API?"
persona, confidence = template_service.detect_persona(query)

if persona and confidence >= 0.75:
    print(f"Detected {persona} persona with {confidence:.2f} confidence")
    # Use detected persona
    request = TemplateSelectionRequest(query=query, persona=persona)
else:
    # Fall back to default (educator)
    request = TemplateSelectionRequest(query=query, persona=PersonaType.EDUCATOR)
```

### Template Overrides

```python
# Override specific parameters
request = TemplateSelectionRequest(
    query="Research on Kwanzaa history",
    persona=PersonaType.RESEARCHER,
    template_overrides={
        "similarity_threshold": 0.85,  # Higher than template default
        "result_limit": 30,  # More results than default
        "filters": {
            "year_gte": 1966,  # Only sources from 1966 onward
            "year_lte": 1980
        }
    }
)
```

### Integration with Search Service

```python
from app.services.search import SearchService
from app.services.query_templates import QueryTemplateService

# Initialize services
search_service = SearchService()
template_service = QueryTemplateService()

# Apply template
template_request = TemplateSelectionRequest(
    query="When was Kwanzaa founded?",
    persona=PersonaType.EDUCATOR
)
template_response = template_service.apply_template(template_request)

# Use template output for search
search_request = SearchRequest(
    query=template_response.application.expanded_query,
    namespace=template_response.application.namespaces[0],
    threshold=template_response.application.similarity_threshold,
    limit=template_response.application.result_limit,
    filters=template_response.application.metadata_filters
)

search_results = await search_service.search(search_request, zerodb_search_func)
```

---

## Configuration

### Template Structure

Templates are defined in `backend/config/rag/query_templates.yaml`:

```yaml
templates:
  persona_key:
    display_name: "Human-readable name"
    description: "Template purpose"
    nguzo_saba_principle: "Aligned principle"

    namespaces:
      - "namespace1"
      - "namespace2"

    expansion:
      strategy: "technical|historical|thematic|research|none"
      add_synonyms: true
      add_related_terms: true
      extract_entities: true
      temporal_context: false
      max_expansion_terms: 10

    filters:
      content_types:
        - "type1"
        - "type2"
      year_range:
        min: 1900
        max: 2024
      tags_required:
        - "required_tag"
      tags_preferred:
        - "preferred_tag"

    retrieval:
      similarity_threshold: 0.75
      result_limit: 10
      min_results: 3
      rerank: true
      diversity_factor: 0.5

    context_formatting:
      include_metadata: true
      include_citations: true
      citation_style: "chicago|apa|mla"
      snippet_length: 512
      highlight_query_terms: false
      show_provenance: true
      deduplicate_sources: true

    example_queries:
      - "Example query 1"
      - "Example query 2"
```

### Expansion Dictionaries

Define term expansions per strategy:

```yaml
expansion_dictionaries:
  technical:
    term:
      - "related_term1"
      - "related_term2"

  historical:
    historical_term:
      - "context_term1"
      - "context_term2"
```

### Selection Rules

Configure auto-detection and validation:

```yaml
selection_rules:
  default: "educator"

  auto_detection:
    enabled: true
    confidence_threshold: 0.75
    patterns:
      builder:
        - "pattern1"
        - "pattern2"

  validation:
    max_namespaces: 6
    min_similarity_threshold: 0.5
    max_similarity_threshold: 0.95
    max_result_limit: 50
```

---

## Testing

### Run Template Tests

```bash
# Run all template tests
pytest backend/tests/test_query_templates.py -v

# Run specific test class
pytest backend/tests/test_query_templates.py::TestQueryTemplateService -v

# Test persona-specific behavior
pytest backend/tests/test_query_templates.py::TestPersonaSpecificBehaviors -v
```

### Test Coverage Areas

1. **Model Validation**: Pydantic model constraints
2. **Template Loading**: YAML parsing and validation
3. **Query Expansion**: Strategy-specific expansion
4. **Metadata Filters**: Filter generation and application
5. **Persona Detection**: Auto-detection accuracy
6. **Override Handling**: Parameter override priority
7. **End-to-End**: Complete workflow testing

---

## Examples by Use Case

### Use Case 1: API Documentation Search (Builder)

```python
request = TemplateSelectionRequest(
    query="ZeroDB vector search API parameters",
    persona=PersonaType.BUILDER
)

response = template_service.apply_template(request)

# Result:
# - Expanded query includes: "endpoint", "interface", "method"
# - Namespace: kwanzaa_dev_patterns
# - Threshold: 0.70
# - Focus on code examples and technical guides
```

### Use Case 2: Classroom Lesson Planning (Educator)

```python
request = TemplateSelectionRequest(
    query="Origins of Kwanzaa and the seven principles",
    persona=PersonaType.EDUCATOR
)

response = template_service.apply_template(request)

# Result:
# - Expanded query adds historical context
# - Namespace: kwanzaa_primary_sources only
# - Threshold: 0.80 (high quality)
# - Citations required, verified sources only
# - Reranking enabled for best results
```

### Use Case 3: Speech Writing (Creator)

```python
request = TemplateSelectionRequest(
    query="Inspiring quotes about unity and community",
    persona=PersonaType.CREATOR
)

response = template_service.apply_template(request)

# Result:
# - Expanded with thematic terms: togetherness, solidarity, collective
# - Namespaces: primary_sources, speeches_letters, teaching_kits
# - Threshold: 0.65 (inclusive)
# - 15 results for broad inspiration
# - High diversity factor (0.7)
```

### Use Case 4: Academic Research (Researcher)

```python
request = TemplateSelectionRequest(
    query="Historical evolution of Kwanzaa 1966-1980",
    persona=PersonaType.RESEARCHER,
    template_overrides={
        "filters": {
            "year_gte": 1966,
            "year_lte": 1980
        }
    }
)

response = template_service.apply_template(request)

# Result:
# - Comprehensive namespace coverage (4 sources)
# - Threshold: 0.75 (balanced)
# - 20 results (maximum coverage)
# - Reranking enabled
# - Full provenance metadata
# - Year filter applied: 1966-1980
```

---

## Best Practices

### 1. Choose the Right Persona

- **Builder**: Technical how-to, implementation questions
- **Educator**: Historical facts, verified information
- **Creator**: Inspiration, narratives, creative content
- **Researcher**: Comprehensive analysis, multiple sources

### 2. Use Auto-Detection Wisely

Auto-detection works best when queries contain clear signal words:
- "how to implement" → Builder
- "when was" / "who founded" → Educator
- "inspiring" / "creative" → Creator
- "scholarly" / "comprehensive" → Researcher

For ambiguous queries, explicitly specify persona.

### 3. Override Parameters Thoughtfully

Override when:
- Specific date ranges needed
- Different quality threshold required
- More/fewer results desired
- Special filtering criteria

Don't override:
- Namespaces (persona-specific by design)
- Expansion strategy (persona-optimized)
- Citation preferences (persona-aligned)

### 4. Validate Template Configuration

Before deploying custom templates:

```python
template = service.get_template(PersonaType.CUSTOM)
errors = service.validate_template(template)

if errors:
    for error in errors:
        print(f"Validation error: {error}")
```

### 5. Monitor Query Expansion

Track expansion effectiveness:

```python
response = template_service.apply_template(request)

print(f"Original: {response.application.original_query}")
print(f"Expanded: {response.application.expanded_query}")
print(f"Terms added: {response.application.expansion_terms}")

# Evaluate if expansion improved retrieval
```

---

## Troubleshooting

### Issue: No results returned

**Possible causes**:
1. Similarity threshold too high
2. Metadata filters too restrictive
3. Query-namespace mismatch

**Solutions**:
- Lower threshold via overrides
- Relax filters
- Verify appropriate namespace for content

### Issue: Low-quality results

**Possible causes**:
1. Similarity threshold too low
2. Wrong persona selected
3. Query needs better expansion

**Solutions**:
- Increase threshold
- Use Educator or Researcher persona (higher quality)
- Enable reranking

### Issue: Results lack diversity

**Possible causes**:
1. Low diversity factor
2. Deduplication too aggressive
3. Single namespace search

**Solutions**:
- Increase diversity_factor in overrides
- Disable deduplicate_sources
- Use Creator or Researcher persona (multiple namespaces)

### Issue: Template not loading

**Possible causes**:
1. YAML syntax error
2. Missing required fields
3. Invalid enum values

**Solutions**:
- Validate YAML syntax
- Check validation.required_fields
- Verify enum values (strategy, citation_style, etc.)

---

## Performance Considerations

### Caching

Template service supports query expansion caching:

```yaml
performance:
  cache_expanded_queries: true
  cache_ttl_seconds: 600
```

Expanded queries are cached for 10 minutes to avoid redundant expansion.

### Parallel Namespace Search

For personas with multiple namespaces:

```yaml
performance:
  parallel_namespace_search: true
  max_parallel_namespaces: 3
```

Searches up to 3 namespaces in parallel for faster results.

### Query Normalization

Standardize queries before expansion:

```yaml
performance:
  enable_query_normalization: true
  enable_stopword_removal: false  # Keep for semantic search
```

---

## Nguzo Saba Alignment

Each template embodies one of the Seven Principles:

1. **Umoja (Unity)**: Shared template system across personas
2. **Kujichagulia (Self-Determination)**: Builder persona - independent learning
3. **Ujima (Collective Work)**: Researcher persona - scholarly contribution
4. **Ujamaa (Cooperative Economics)**: N/A for query templates
5. **Nia (Purpose)**: Goal-oriented query enhancement
6. **Kuumba (Creativity)**: Creator persona - cultural expression
7. **Imani (Faith)**: Educator persona - trustworthy information

Templates are designed to support community-focused knowledge retrieval while respecting user autonomy and purpose.

---

## Future Enhancements

### Planned Features

1. **Custom Template Creation**: API for users to define custom templates
2. **Template Analytics**: Track which templates perform best
3. **Dynamic Expansion**: LLM-powered query expansion
4. **Multi-Persona Search**: Combine results from multiple personas
5. **Feedback Loop**: User ratings improve template quality
6. **Template Versioning**: A/B test template configurations

### Contributing

To propose new templates or improvements:

1. Define template in YAML
2. Write comprehensive tests
3. Document use cases and examples
4. Align with Nguzo Saba principles
5. Submit PR with validation results

---

## References

- **Models**: `backend/app/models/query_template.py`
- **Service**: `backend/app/services/query_templates.py`
- **Configuration**: `backend/config/rag/query_templates.yaml`
- **Tests**: `backend/tests/test_query_templates.py`
- **Integration**: `backend/app/services/search.py`

## Support

For questions or issues:
1. Check this guide first
2. Review test cases for examples
3. Validate template configuration
4. File issue with reproduction steps
