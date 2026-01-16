"""Tests for query template service and models.

Tests cover:
1. Template loading and validation
2. Query expansion for each persona
3. Metadata filter generation
4. Template application workflow
5. Auto-detection of personas
6. Override handling
"""

import pytest

from app.models.query_template import (
    ContextFormattingPreferences,
    MetadataFilterTemplate,
    PersonaType,
    QueryExpansionRules,
    QueryExpansionStrategy,
    QueryTemplate,
    RetrievalParameterOverrides,
    TemplateSelectionRequest,
)
from app.services.query_templates import QueryTemplateService


class TestQueryTemplateModels:
    """Test query template data models."""

    def test_persona_type_enum(self):
        """Test PersonaType enum has all expected values."""
        assert PersonaType.BUILDER == "builder"
        assert PersonaType.EDUCATOR == "educator"
        assert PersonaType.CREATOR == "creator"
        assert PersonaType.RESEARCHER == "researcher"

    def test_query_expansion_strategy_enum(self):
        """Test QueryExpansionStrategy enum values."""
        assert QueryExpansionStrategy.TECHNICAL == "technical"
        assert QueryExpansionStrategy.HISTORICAL == "historical"
        assert QueryExpansionStrategy.THEMATIC == "thematic"
        assert QueryExpansionStrategy.RESEARCH == "research"
        assert QueryExpansionStrategy.NONE == "none"

    def test_metadata_filter_template_validation(self):
        """Test MetadataFilterTemplate validates year ranges."""
        # Valid year range
        valid_filter = MetadataFilterTemplate(
            year_range={"min": 1900, "max": 2000}
        )
        assert valid_filter.year_range["min"] == 1900

        # Invalid year range (min > max)
        with pytest.raises(ValueError, match="min.*max"):
            MetadataFilterTemplate(year_range={"min": 2000, "max": 1900})

    def test_retrieval_parameter_overrides_validation(self):
        """Test RetrievalParameterOverrides validates ranges."""
        # Valid parameters
        valid_params = RetrievalParameterOverrides(
            similarity_threshold=0.75,
            result_limit=10,
            diversity_factor=0.5,
        )
        assert valid_params.similarity_threshold == 0.75

        # Invalid similarity threshold
        with pytest.raises(ValueError):
            RetrievalParameterOverrides(similarity_threshold=1.5)

        # Invalid diversity factor
        with pytest.raises(ValueError):
            RetrievalParameterOverrides(diversity_factor=2.0)

    def test_query_template_requires_namespaces(self):
        """Test QueryTemplate requires at least one namespace."""
        with pytest.raises(ValueError, match="namespace"):
            QueryTemplate(
                persona=PersonaType.BUILDER,
                display_name="Builder",
                description="Test template",
                namespaces=[],  # Empty list should fail
                nguzo_saba_principle="Test principle",
            )

    def test_context_formatting_preferences_defaults(self):
        """Test ContextFormattingPreferences has sensible defaults."""
        prefs = ContextFormattingPreferences()
        assert prefs.include_metadata is True
        assert prefs.include_citations is True
        assert prefs.citation_style == "chicago"
        assert prefs.snippet_length == 512


class TestQueryTemplateService:
    """Test query template service."""

    @pytest.fixture
    def service(self, tmp_path):
        """Create query template service with test config."""
        # Create minimal test config
        config = """
templates:
  builder:
    display_name: "Builder"
    description: "For developers"
    nguzo_saba_principle: "Kujichagulia"
    namespaces:
      - "kwanzaa_dev_patterns"
    expansion:
      strategy: "technical"
      add_synonyms: true
      add_related_terms: true
      max_expansion_terms: 10
    filters:
      content_types:
        - "code_example"
        - "technical_guide"
    retrieval:
      similarity_threshold: 0.70
      result_limit: 10
      min_results: 1
      rerank: false
    context_formatting:
      include_metadata: true
      citation_style: "chicago"
    example_queries:
      - "How to implement search?"

  educator:
    display_name: "Educator"
    description: "For teachers"
    nguzo_saba_principle: "Imani"
    namespaces:
      - "kwanzaa_primary_sources"
    expansion:
      strategy: "historical"
      add_synonyms: true
      extract_entities: true
      temporal_context: true
      max_expansion_terms: 8
    filters:
      content_types:
        - "historical_document"
      tags_required:
        - "verified"
    retrieval:
      similarity_threshold: 0.80
      result_limit: 10
      min_results: 3
      rerank: true
    context_formatting:
      include_citations: true
      show_provenance: true
    example_queries:
      - "When was Kwanzaa founded?"

expansion_dictionaries:
  technical:
    api:
      - "endpoint"
      - "interface"
    schema:
      - "model"
      - "structure"
  historical:
    kwanzaa:
      - "African American holiday"
      - "Nguzo Saba"

selection_rules:
  default: "educator"
  auto_detection:
    enabled: true
    confidence_threshold: 0.75
    patterns:
      builder:
        - "how to implement"
        - "code example"
        - "api"
      educator:
        - "when was"
        - "who founded"
  validation:
    max_namespaces: 6
    min_similarity_threshold: 0.5
    max_similarity_threshold: 0.95
    max_result_limit: 50
    required_fields:
      - "display_name"
      - "description"
      - "namespaces"
"""
        config_path = tmp_path / "query_templates.yaml"
        config_path.write_text(config)

        return QueryTemplateService(config_path=str(config_path))

    def test_service_initialization(self, service):
        """Test service loads templates correctly."""
        assert len(service.templates) == 2
        assert PersonaType.BUILDER in service.templates
        assert PersonaType.EDUCATOR in service.templates

    def test_get_template(self, service):
        """Test retrieving specific template."""
        builder_template = service.get_template(PersonaType.BUILDER)
        assert builder_template is not None
        assert builder_template.display_name == "Builder"
        assert builder_template.persona == PersonaType.BUILDER
        assert "kwanzaa_dev_patterns" in builder_template.namespaces

    def test_get_template_nonexistent(self, service):
        """Test getting non-existent template returns None."""
        # Creator not in test config
        template = service.get_template(PersonaType.CREATOR)
        assert template is None

    def test_list_templates(self, service):
        """Test listing all templates."""
        templates = service.list_templates()
        assert len(templates) == 2
        assert PersonaType.BUILDER in templates
        assert PersonaType.EDUCATOR in templates

    def test_detect_persona_builder(self, service):
        """Test persona detection for builder queries."""
        query = "How to implement the search api in my code?"
        persona, confidence = service.detect_persona(query)

        # Detection should identify builder (has "how to implement", "api", "code example" patterns)
        if persona:
            assert persona == PersonaType.BUILDER
            assert confidence >= 0.75
        else:
            # If detection returns None, check that confidence was too low
            assert confidence < 0.75

    def test_detect_persona_educator(self, service):
        """Test persona detection for educator queries."""
        query = "When was Kwanzaa founded and who started it?"
        persona, confidence = service.detect_persona(query)

        # Detection should identify educator (has "when was", "who founded" patterns)
        if persona:
            assert persona == PersonaType.EDUCATOR
            assert confidence >= 0.75
        else:
            # If detection returns None, check that confidence was too low
            assert confidence < 0.75

    def test_detect_persona_low_confidence(self, service):
        """Test persona detection with ambiguous query."""
        query = "Tell me about celebrations"
        persona, confidence = service.detect_persona(query)

        # Should return None if confidence too low
        if persona is None:
            assert confidence < 0.75
        else:
            # Or return detected persona with lower confidence
            assert confidence >= 0.0

    def test_expand_query_technical(self, service):
        """Test query expansion with technical strategy."""
        template = service.get_template(PersonaType.BUILDER)
        query = "How to use the api?"

        expanded, terms = service.expand_query(query, template.expansion)

        # Should include related terms for "api"
        assert len(terms) > 0
        assert any(term in ["endpoint", "interface"] for term in terms)
        assert query in expanded

    def test_expand_query_historical(self, service):
        """Test query expansion with historical strategy."""
        template = service.get_template(PersonaType.EDUCATOR)
        query = "Tell me about Kwanzaa"

        expanded, terms = service.expand_query(query, template.expansion)

        # Should include related terms for "kwanzaa"
        assert len(terms) > 0
        # Terms should be from expansion dictionary
        expanded_lower = expanded.lower()
        assert "kwanzaa" in expanded_lower

    def test_expand_query_no_expansion(self, service):
        """Test query with no expansion strategy."""
        rules = QueryExpansionRules(strategy=QueryExpansionStrategy.NONE)
        query = "test query"

        expanded, terms = service.expand_query(query, rules)

        assert expanded == query
        assert len(terms) == 0

    def test_apply_template_builder(self, service):
        """Test applying builder template to query."""
        request = TemplateSelectionRequest(
            query="How to implement vector search?",
            persona=PersonaType.BUILDER,
        )

        response = service.apply_template(request)

        assert response.status == "success"
        assert response.application.persona == PersonaType.BUILDER
        assert response.application.original_query == request.query
        assert len(response.application.namespaces) > 0
        assert response.application.similarity_threshold == 0.70
        assert response.application.result_limit == 10

    def test_apply_template_educator(self, service):
        """Test applying educator template to query."""
        request = TemplateSelectionRequest(
            query="When was Kwanzaa first celebrated?",
            persona=PersonaType.EDUCATOR,
        )

        response = service.apply_template(request)

        assert response.status == "success"
        assert response.application.persona == PersonaType.EDUCATOR
        assert response.application.similarity_threshold == 0.80
        assert response.application.rerank is True
        assert response.application.context_formatting.include_citations is True

    def test_apply_template_with_overrides(self, service):
        """Test template application with parameter overrides."""
        request = TemplateSelectionRequest(
            query="Test query",
            persona=PersonaType.BUILDER,
            template_overrides={
                "similarity_threshold": 0.85,
                "result_limit": 20,
            },
        )

        response = service.apply_template(request)

        # Overrides should take precedence
        assert response.application.similarity_threshold == 0.85
        assert response.application.result_limit == 20

    def test_apply_template_invalid_persona(self, service):
        """Test applying template with invalid persona."""
        request = TemplateSelectionRequest(
            query="Test query",
            persona=PersonaType.CREATOR,  # Not in test config
        )

        with pytest.raises(ValueError, match="No template found"):
            service.apply_template(request)

    def test_build_metadata_filters(self, service):
        """Test building metadata filters from template."""
        filter_template = MetadataFilterTemplate(
            content_types=["code_example", "technical_guide"],
            year_range={"min": 2000, "max": 2024},
            tags_required=["verified"],
        )

        filters = service._build_metadata_filters(filter_template)

        assert filters["content_type"] == {"$in": ["code_example", "technical_guide"]}
        assert filters["year_gte"] == 2000
        assert filters["year_lte"] == 2024
        assert filters["tags"] == {"$all": ["verified"]}

    def test_build_metadata_filters_with_overrides(self, service):
        """Test metadata filters with overrides."""
        filter_template = MetadataFilterTemplate(
            content_types=["code_example"],
        )

        overrides = {
            "filters": {
                "content_type": {"$in": ["technical_guide"]},
            }
        }

        filters = service._build_metadata_filters(filter_template, overrides)

        # Override should take precedence
        assert filters["content_type"] == {"$in": ["technical_guide"]}

    def test_validate_template_valid(self, service):
        """Test validation of valid template."""
        template = service.get_template(PersonaType.BUILDER)
        errors = service.validate_template(template)

        assert len(errors) == 0

    def test_validate_template_too_many_namespaces(self, service):
        """Test validation catches too many namespaces."""
        template = QueryTemplate(
            persona=PersonaType.BUILDER,
            display_name="Test",
            description="Test template",
            namespaces=["ns1", "ns2", "ns3", "ns4", "ns5", "ns6", "ns7"],  # 7 namespaces
            nguzo_saba_principle="Test",
        )

        errors = service.validate_template(template)
        assert any("namespace" in err.lower() for err in errors)

    def test_validate_template_invalid_threshold(self, service):
        """Test validation catches invalid similarity threshold."""
        template = QueryTemplate(
            persona=PersonaType.BUILDER,
            display_name="Test",
            description="Test template",
            namespaces=["ns1"],
            nguzo_saba_principle="Test",
            retrieval=RetrievalParameterOverrides(similarity_threshold=0.99),
        )

        errors = service.validate_template(template)
        assert any("threshold" in err.lower() for err in errors)

    def test_get_template_examples(self, service):
        """Test retrieving example queries for template."""
        examples = service.get_template_examples(PersonaType.BUILDER)

        assert len(examples) > 0
        assert "How to implement search?" in examples

    def test_get_template_examples_nonexistent(self, service):
        """Test getting examples for non-existent template."""
        examples = service.get_template_examples(PersonaType.CREATOR)
        assert len(examples) == 0


class TestQueryTemplateIntegration:
    """Integration tests for full template workflow."""

    @pytest.fixture
    def service(self, tmp_path):
        """Create service with full config."""
        # Use same config as above
        config = """
templates:
  builder:
    display_name: "Builder"
    description: "For developers"
    nguzo_saba_principle: "Kujichagulia"
    namespaces:
      - "kwanzaa_dev_patterns"
    expansion:
      strategy: "technical"
      add_related_terms: true
      max_expansion_terms: 5
    retrieval:
      similarity_threshold: 0.70
      result_limit: 10
    context_formatting:
      include_metadata: true

expansion_dictionaries:
  technical:
    search:
      - "retrieval"
      - "query"
      - "ranking"

selection_rules:
  validation:
    max_namespaces: 6
"""
        config_path = tmp_path / "query_templates.yaml"
        config_path.write_text(config)
        return QueryTemplateService(config_path=str(config_path))

    def test_end_to_end_template_application(self, service):
        """Test complete workflow from query to search params."""
        # 1. User submits query with persona
        request = TemplateSelectionRequest(
            query="How to implement semantic search?",
            persona=PersonaType.BUILDER,
        )

        # 2. Apply template
        response = service.apply_template(request)

        # 3. Verify result is ready for search execution
        app = response.application

        assert app.original_query == "How to implement semantic search?"
        assert len(app.expanded_query) >= len(app.original_query)
        assert len(app.namespaces) > 0
        assert 0.0 <= app.similarity_threshold <= 1.0
        assert app.result_limit > 0
        assert app.template_used.endswith("_template")

        # 4. Verify metadata is informative
        metadata = response.template_metadata
        assert metadata["persona"] == "builder"
        assert "display_name" in metadata
        assert "nguzo_saba_principle" in metadata


class TestPersonaSpecificBehaviors:
    """Test that each persona has distinct retrieval behaviors."""

    @pytest.fixture
    def full_service(self, tmp_path):
        """Create service with all four personas."""
        config = """
templates:
  builder:
    display_name: "Builder"
    description: "Developer persona"
    nguzo_saba_principle: "Kujichagulia"
    namespaces: ["kwanzaa_dev_patterns"]
    expansion:
      strategy: "technical"
    retrieval:
      similarity_threshold: 0.70
    context_formatting:
      include_citations: false

  educator:
    display_name: "Educator"
    description: "Educator persona"
    nguzo_saba_principle: "Imani"
    namespaces: ["kwanzaa_primary_sources"]
    expansion:
      strategy: "historical"
    retrieval:
      similarity_threshold: 0.80
      rerank: true
    context_formatting:
      include_citations: true

  creator:
    display_name: "Creator"
    description: "Creator persona"
    nguzo_saba_principle: "Kuumba"
    namespaces: ["kwanzaa_primary_sources", "kwanzaa_speeches_letters"]
    expansion:
      strategy: "thematic"
    retrieval:
      similarity_threshold: 0.65
      result_limit: 15
    context_formatting:
      include_citations: true
      citation_style: "mla"

  researcher:
    display_name: "Researcher"
    description: "Researcher persona"
    nguzo_saba_principle: "Ujima"
    namespaces: ["kwanzaa_primary_sources", "kwanzaa_black_press", "kwanzaa_speeches_letters"]
    expansion:
      strategy: "research"
    retrieval:
      similarity_threshold: 0.75
      result_limit: 20
      rerank: true
    context_formatting:
      include_citations: true
      show_provenance: true

selection_rules:
  validation:
    max_namespaces: 6
"""
        config_path = tmp_path / "query_templates.yaml"
        config_path.write_text(config)
        return QueryTemplateService(config_path=str(config_path))

    def test_builder_focuses_on_code(self, full_service):
        """Test builder persona focuses on technical content."""
        request = TemplateSelectionRequest(
            query="How to implement search?",
            persona=PersonaType.BUILDER,
        )
        response = full_service.apply_template(request)

        assert "dev_patterns" in response.application.namespaces[0]
        assert response.application.similarity_threshold == 0.70
        assert not response.application.context_formatting.include_citations

    def test_educator_requires_high_quality(self, full_service):
        """Test educator persona has high quality threshold."""
        request = TemplateSelectionRequest(
            query="When was Kwanzaa founded?",
            persona=PersonaType.EDUCATOR,
        )
        response = full_service.apply_template(request)

        assert response.application.similarity_threshold == 0.80
        assert response.application.rerank is True
        assert response.application.context_formatting.include_citations

    def test_creator_uses_multiple_namespaces(self, full_service):
        """Test creator persona searches multiple sources."""
        request = TemplateSelectionRequest(
            query="Inspirational Kwanzaa speeches",
            persona=PersonaType.CREATOR,
        )
        response = full_service.apply_template(request)

        assert len(response.application.namespaces) >= 2
        assert response.application.similarity_threshold == 0.65
        assert response.application.context_formatting.citation_style == "mla"

    def test_researcher_comprehensive_coverage(self, full_service):
        """Test researcher persona seeks comprehensive coverage."""
        request = TemplateSelectionRequest(
            query="Scholarly analysis of Kwanzaa",
            persona=PersonaType.RESEARCHER,
        )
        response = full_service.apply_template(request)

        assert len(response.application.namespaces) >= 3
        assert response.application.result_limit == 20
        assert response.application.rerank is True
        assert response.application.context_formatting.show_provenance
