"""Query template service for persona-specific retrieval.

This service implements the template engine that:
1. Loads and manages query templates from configuration
2. Applies templates to user queries with expansion
3. Generates persona-specific search parameters
4. Supports both explicit template selection and auto-detection

Aligned with Nguzo Saba principles:
- Kujichagulia (Self-Determination): User-driven template selection
- Nia (Purpose): Goal-oriented query enhancement
- Kuumba (Creativity): Flexible template composition
- Imani (Faith): Transparent template application
"""

import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import yaml

from app.models.query_template import (
    ContextFormattingPreferences,
    MetadataFilterTemplate,
    PersonaType,
    QueryExpansionRules,
    QueryExpansionStrategy,
    QueryTemplate,
    QueryTemplateApplication,
    RetrievalParameterOverrides,
    TemplateSelectionRequest,
    TemplateSelectionResponse,
)


class QueryTemplateService:
    """Service for loading and applying persona-specific query templates."""

    def __init__(self, config_path: Optional[str] = None) -> None:
        """Initialize the query template service.

        Args:
            config_path: Path to query_templates.yaml. If None, uses default location.
        """
        self.config_path = config_path or self._get_default_config_path()
        self.templates: Dict[PersonaType, QueryTemplate] = {}
        self.expansion_dictionaries: Dict[str, Dict[str, List[str]]] = {}
        self.selection_rules: Dict[str, Any] = {}
        self._load_config()

    def _get_default_config_path(self) -> str:
        """Get default config path relative to backend directory."""
        # Assuming this file is in backend/app/services/
        backend_dir = Path(__file__).parent.parent.parent
        return str(backend_dir / "config" / "rag" / "query_templates.yaml")

    def _load_config(self) -> None:
        """Load templates and configuration from YAML file.

        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If config is invalid
        """
        try:
            with open(self.config_path, "r") as f:
                config = yaml.safe_load(f)

            # Load templates
            templates_config = config.get("templates", {})
            for persona_key, template_data in templates_config.items():
                try:
                    persona = PersonaType(persona_key)
                    template = self._parse_template(persona, template_data)
                    self.templates[persona] = template
                except (ValueError, KeyError) as e:
                    print(f"Warning: Failed to load template for {persona_key}: {e}")
                    continue

            # Load expansion dictionaries
            self.expansion_dictionaries = config.get("expansion_dictionaries", {})

            # Load selection rules
            self.selection_rules = config.get("selection_rules", {})

        except FileNotFoundError:
            raise FileNotFoundError(f"Query template config not found: {self.config_path}")
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in query template config: {e}")

    def _parse_template(self, persona: PersonaType, data: Dict[str, Any]) -> QueryTemplate:
        """Parse template data from config into QueryTemplate model.

        Args:
            persona: Persona type
            data: Template data from config

        Returns:
            Parsed QueryTemplate

        Raises:
            ValueError: If template data is invalid
        """
        # Parse expansion rules
        expansion_data = data.get("expansion", {})
        expansion = QueryExpansionRules(
            strategy=QueryExpansionStrategy(expansion_data.get("strategy", "none")),
            add_synonyms=expansion_data.get("add_synonyms", False),
            add_related_terms=expansion_data.get("add_related_terms", False),
            extract_entities=expansion_data.get("extract_entities", False),
            temporal_context=expansion_data.get("temporal_context", False),
            max_expansion_terms=expansion_data.get("max_expansion_terms", 5),
        )

        # Parse filters
        filters_data = data.get("filters", {})
        filters = MetadataFilterTemplate(
            content_types=filters_data.get("content_types"),
            year_range=filters_data.get("year_range"),
            source_org_priority=filters_data.get("source_org_priority"),
            tags_required=filters_data.get("tags_required"),
            tags_preferred=filters_data.get("tags_preferred"),
        )

        # Parse retrieval overrides
        retrieval_data = data.get("retrieval", {})
        retrieval = RetrievalParameterOverrides(
            similarity_threshold=retrieval_data.get("similarity_threshold"),
            result_limit=retrieval_data.get("result_limit"),
            min_results=retrieval_data.get("min_results"),
            rerank=retrieval_data.get("rerank"),
            diversity_factor=retrieval_data.get("diversity_factor"),
        )

        # Parse context formatting
        context_data = data.get("context_formatting", {})
        context_formatting = ContextFormattingPreferences(
            include_metadata=context_data.get("include_metadata", True),
            include_citations=context_data.get("include_citations", True),
            citation_style=context_data.get("citation_style", "chicago"),
            snippet_length=context_data.get("snippet_length", 512),
            highlight_query_terms=context_data.get("highlight_query_terms", False),
            show_provenance=context_data.get("show_provenance", True),
            deduplicate_sources=context_data.get("deduplicate_sources", True),
        )

        # Build template
        return QueryTemplate(
            persona=persona,
            display_name=data["display_name"],
            description=data["description"],
            namespaces=data["namespaces"],
            expansion=expansion,
            filters=filters,
            retrieval=retrieval,
            context_formatting=context_formatting,
            nguzo_saba_principle=data.get("nguzo_saba_principle", ""),
            example_queries=data.get("example_queries", []),
        )

    def get_template(self, persona: PersonaType) -> Optional[QueryTemplate]:
        """Get template for a specific persona.

        Args:
            persona: Persona type

        Returns:
            QueryTemplate if found, None otherwise
        """
        return self.templates.get(persona)

    def list_templates(self) -> Dict[PersonaType, QueryTemplate]:
        """List all available templates.

        Returns:
            Dictionary of persona to template mappings
        """
        return self.templates.copy()

    def detect_persona(self, query: str) -> Tuple[Optional[PersonaType], float]:
        """Auto-detect appropriate persona from query text.

        Uses pattern matching to identify query characteristics.

        Args:
            query: User query text

        Returns:
            Tuple of (detected persona, confidence score)
        """
        if not self.selection_rules.get("auto_detection", {}).get("enabled", False):
            return None, 0.0

        patterns = self.selection_rules.get("auto_detection", {}).get("patterns", {})
        threshold = self.selection_rules.get("auto_detection", {}).get(
            "confidence_threshold", 0.75
        )

        query_lower = query.lower()
        scores: Dict[PersonaType, float] = {}

        for persona_key, pattern_list in patterns.items():
            try:
                persona = PersonaType(persona_key)
                matches = sum(1 for pattern in pattern_list if pattern.lower() in query_lower)
                scores[persona] = matches / len(pattern_list) if pattern_list else 0.0
            except ValueError:
                continue

        if not scores:
            return None, 0.0

        # Get persona with highest score
        best_persona = max(scores, key=scores.get)  # type: ignore
        best_score = scores[best_persona]

        if best_score >= threshold:
            return best_persona, best_score

        return None, 0.0

    def expand_query(
        self, query: str, expansion_rules: QueryExpansionRules
    ) -> Tuple[str, List[str]]:
        """Expand query based on expansion rules.

        Args:
            query: Original query text
            expansion_rules: Rules for query expansion

        Returns:
            Tuple of (expanded query, list of added terms)
        """
        if expansion_rules.strategy == QueryExpansionStrategy.NONE:
            return query, []

        added_terms: Set[str] = set()
        query_lower = query.lower()

        # Get expansion dictionary for this strategy
        strategy_dict = self.expansion_dictionaries.get(expansion_rules.strategy.value, {})

        # Add related terms based on query content
        if expansion_rules.add_related_terms:
            for term, related in strategy_dict.items():
                if term.lower() in query_lower:
                    # Add related terms up to max limit
                    available_slots = expansion_rules.max_expansion_terms - len(added_terms)
                    added_terms.update(related[:available_slots])

                    if len(added_terms) >= expansion_rules.max_expansion_terms:
                        break

        # Add synonyms (simple implementation - could be enhanced with thesaurus)
        if expansion_rules.add_synonyms and len(added_terms) < expansion_rules.max_expansion_terms:
            # This is a simplified implementation
            # In production, integrate with a proper synonym service
            pass

        # Extract entities (simplified - could use NER)
        if expansion_rules.extract_entities:
            # Simple capitalized word extraction as entity candidates
            entities = re.findall(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b", query)
            available_slots = expansion_rules.max_expansion_terms - len(added_terms)
            added_terms.update(entities[:available_slots])

        # Build expanded query
        if added_terms:
            expansion_terms_list = list(added_terms)
            expanded = f"{query} {' '.join(expansion_terms_list)}"
            return expanded.strip(), expansion_terms_list

        return query, []

    def apply_template(
        self,
        request: TemplateSelectionRequest,
    ) -> TemplateSelectionResponse:
        """Apply a query template to a user query.

        This is the main method for template application. It:
        1. Retrieves the appropriate template
        2. Expands the query based on template rules
        3. Applies metadata filters
        4. Generates retrieval parameters
        5. Returns complete application result

        Args:
            request: Template selection and application request

        Returns:
            TemplateSelectionResponse with applied template

        Raises:
            ValueError: If persona is invalid or template not found
        """
        # Get template
        template = self.get_template(request.persona)
        if not template:
            raise ValueError(f"No template found for persona: {request.persona}")

        # Expand query
        expanded_query, expansion_terms = self.expand_query(
            request.query, template.expansion
        )

        # Build metadata filters
        metadata_filters = self._build_metadata_filters(
            template.filters, request.template_overrides
        )

        # Get retrieval parameters (with overrides)
        similarity_threshold = self._get_override(
            "similarity_threshold",
            template.retrieval.similarity_threshold,
            request.template_overrides,
            default=0.7,
        )

        result_limit = self._get_override(
            "result_limit",
            template.retrieval.result_limit,
            request.template_overrides,
            default=10,
        )

        min_results = self._get_override(
            "min_results",
            template.retrieval.min_results,
            request.template_overrides,
            default=1,
        )

        rerank = self._get_override(
            "rerank",
            template.retrieval.rerank,
            request.template_overrides,
            default=False,
        )

        # Build application result
        application = QueryTemplateApplication(
            original_query=request.query,
            expanded_query=expanded_query,
            expansion_terms=expansion_terms,
            namespaces=template.namespaces,
            metadata_filters=metadata_filters,
            similarity_threshold=similarity_threshold,
            result_limit=result_limit,
            min_results=min_results,
            rerank=rerank,
            context_formatting=template.context_formatting,
            template_used=f"{request.persona.value}_template",
            persona=request.persona,
        )

        # Build metadata
        template_metadata = {
            "persona": request.persona.value,
            "display_name": template.display_name,
            "nguzo_saba_principle": template.nguzo_saba_principle,
            "expansion_strategy": template.expansion.strategy.value,
            "namespaces_count": len(template.namespaces),
        }

        return TemplateSelectionResponse(
            status="success",
            application=application,
            template_metadata=template_metadata,
        )

    def _build_metadata_filters(
        self,
        filter_template: MetadataFilterTemplate,
        overrides: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Build metadata filter dictionary from template.

        Args:
            filter_template: Filter template from query template
            overrides: Optional override values

        Returns:
            Metadata filter dictionary for search
        """
        filters: Dict[str, Any] = {}

        # Content types
        if filter_template.content_types:
            filters["content_type"] = {"$in": filter_template.content_types}

        # Year range
        if filter_template.year_range:
            if "min" in filter_template.year_range:
                filters["year_gte"] = filter_template.year_range["min"]
            if "max" in filter_template.year_range:
                filters["year_lte"] = filter_template.year_range["max"]

        # Source org priority
        if filter_template.source_org_priority:
            filters["source_org"] = {"$in": filter_template.source_org_priority}

        # Required tags
        if filter_template.tags_required:
            filters["tags"] = {"$all": filter_template.tags_required}

        # Preferred tags (for boosting - not strict filter)
        if filter_template.tags_preferred:
            # Store as metadata for potential boosting in reranking
            filters["tags_preferred"] = filter_template.tags_preferred

        # Apply overrides
        if overrides:
            filters.update(overrides.get("filters", {}))

        return filters

    def _get_override(
        self,
        key: str,
        template_value: Any,
        overrides: Optional[Dict[str, Any]],
        default: Any,
    ) -> Any:
        """Get value with override support.

        Args:
            key: Parameter key
            template_value: Value from template
            overrides: Override dictionary
            default: Default value if neither template nor override provided

        Returns:
            Final value (priority: override > template > default)
        """
        if overrides and key in overrides:
            return overrides[key]

        if template_value is not None:
            return template_value

        return default

    def validate_template(self, template: QueryTemplate) -> List[str]:
        """Validate a query template configuration.

        Args:
            template: Template to validate

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        # Check required fields
        required_fields = self.selection_rules.get("validation", {}).get(
            "required_fields", []
        )
        for field in required_fields:
            if not getattr(template, field, None):
                errors.append(f"Missing required field: {field}")

        # Check namespace count
        max_namespaces = self.selection_rules.get("validation", {}).get("max_namespaces", 6)
        if len(template.namespaces) > max_namespaces:
            errors.append(
                f"Too many namespaces: {len(template.namespaces)} (max: {max_namespaces})"
            )

        # Check similarity threshold range
        if template.retrieval.similarity_threshold is not None:
            min_threshold = self.selection_rules.get("validation", {}).get(
                "min_similarity_threshold", 0.5
            )
            max_threshold = self.selection_rules.get("validation", {}).get(
                "max_similarity_threshold", 0.95
            )
            if not (min_threshold <= template.retrieval.similarity_threshold <= max_threshold):
                errors.append(
                    f"Similarity threshold {template.retrieval.similarity_threshold} "
                    f"outside valid range [{min_threshold}, {max_threshold}]"
                )

        # Check result limit
        if template.retrieval.result_limit is not None:
            max_limit = self.selection_rules.get("validation", {}).get("max_result_limit", 50)
            if template.retrieval.result_limit > max_limit:
                errors.append(
                    f"Result limit {template.retrieval.result_limit} exceeds max: {max_limit}"
                )

        return errors

    def get_template_examples(self, persona: PersonaType) -> List[str]:
        """Get example queries for a persona template.

        Args:
            persona: Persona type

        Returns:
            List of example queries
        """
        template = self.get_template(persona)
        return template.example_queries if template else []
