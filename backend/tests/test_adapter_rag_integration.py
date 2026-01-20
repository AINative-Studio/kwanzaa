"""Test adapter integration with RAG-like workflow.

This module tests the trained adapter's ability to generate
appropriate responses for Kwanzaa-related queries, simulating
a RAG pipeline flow.

Following TDD approach with integration testing.
"""

import pytest
from pathlib import Path
from typing import List, Dict
from app.core.config_loader import config_loader


@pytest.fixture
def adapter_path():
    """Get the path to the trained adapter."""
    config = config_loader.load_adapter_config("qlora")
    adapter_path = config["adapter"]["adapter_path"]
    backend_dir = Path(__file__).parent.parent
    return backend_dir / adapter_path


@pytest.fixture
def model_config():
    """Get the model configuration."""
    return config_loader.load_model_config("llama")


class TestAdapterRAGIntegration:
    """Test adapter with RAG-like queries and context."""

    @pytest.mark.integration
    @pytest.mark.slow
    def test_adapter_generates_kwanzaa_response(self, adapter_path):
        """Test that adapter generates appropriate Kwanzaa responses."""
        # Given: Loaded adapter model
        from transformers import AutoTokenizer
        from peft import AutoPeftModelForCausalLM

        model = AutoPeftModelForCausalLM.from_pretrained(
            str(adapter_path),
            device_map="auto",
        )
        tokenizer = AutoTokenizer.from_pretrained(str(adapter_path))

        # When: Asking about Kwanzaa principles
        test_query = "What are the seven principles of Kwanzaa?"
        messages = [
            {"role": "system", "content": "You are a helpful assistant knowledgeable about Kwanzaa."},
            {"role": "user", "content": test_query}
        ]

        text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = tokenizer(text, return_tensors="pt").to(model.device)
        outputs = model.generate(**inputs, max_new_tokens=200, temperature=0.7, do_sample=True)
        response = tokenizer.decode(outputs[0][inputs['input_ids'].shape[1]:], skip_special_tokens=True)

        # Then: Response should be relevant and non-empty
        assert len(response) > 0
        assert len(response.split()) > 10, "Response should be substantial"

        # Should mention Kwanzaa or principles
        response_lower = response.lower()
        kwanzaa_related = any(term in response_lower for term in [
            "kwanzaa", "nguzo saba", "principle", "umoja", "unity",
            "kujichagulia", "ujima", "ujamaa", "nia", "kuumba", "imani"
        ])
        assert kwanzaa_related, f"Response should be Kwanzaa-related. Got: {response}"

    @pytest.mark.integration
    @pytest.mark.slow
    def test_adapter_with_rag_context(self, adapter_path):
        """Test adapter with simulated RAG context injection."""
        # Given: Loaded adapter and simulated RAG context
        from transformers import AutoTokenizer
        from peft import AutoPeftModelForCausalLM

        model = AutoPeftModelForCausalLM.from_pretrained(
            str(adapter_path),
            device_map="auto",
        )
        tokenizer = AutoTokenizer.from_pretrained(str(adapter_path))

        # Simulated RAG context (as would come from RAG pipeline)
        rag_context = """# Retrieved Context
The following 2 sources were retrieved for this query:

## Source 1: Official Kwanzaa Website - The Seven Principles
**Relevance Score:** 0.92
**Year:** 2020
**Source Organization:** Official Kwanzaa Website
**Content Type:** educational_content

**Content:**
The Seven Principles (Nguzo Saba) of Kwanzaa are:
1. Umoja (Unity) - To strive for and maintain unity in the family
2. Kujichagulia (Self-Determination) - To define ourselves
3. Ujima (Collective Work) - To build and maintain our community
4. Ujamaa (Cooperative Economics) - To build and maintain our own stores
5. Nia (Purpose) - To make our collective vocation
6. Kuumba (Creativity) - To do always as much as we can
7. Imani (Faith) - To believe with all our heart

## Source 2: Kwanzaa History and Culture
**Relevance Score:** 0.88
**Year:** 2019
**Source Organization:** Cultural Heritage Foundation

**Content:**
Kwanzaa is an annual celebration of African-American culture that is held from
December 26 to January 1, culminating in gift-giving and a feast."""

        # When: Asking question with RAG context
        test_query = "What are the seven principles of Kwanzaa and what do they mean?"
        messages = [
            {"role": "system", "content": "You are a helpful assistant. Use the provided context to answer questions accurately. Always cite sources when using information from the context."},
            {"role": "user", "content": f"{rag_context}\n\nQuestion: {test_query}\n\nPlease answer based on the context provided above."}
        ]

        text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = tokenizer(text, return_tensors="pt").to(model.device)
        outputs = model.generate(**inputs, max_new_tokens=300, temperature=0.5, do_sample=True)
        response = tokenizer.decode(outputs[0][inputs['input_ids'].shape[1]:], skip_special_tokens=True)

        # Then: Response should use RAG context
        assert len(response) > 0
        response_lower = response.lower()

        # Should mention multiple principles (at least 3)
        principles_mentioned = sum([
            "umoja" in response_lower,
            "kujichagulia" in response_lower,
            "ujima" in response_lower,
            "ujamaa" in response_lower,
            "nia" in response_lower,
            "kuumba" in response_lower,
            "imani" in response_lower,
        ])
        assert principles_mentioned >= 3, f"Should mention at least 3 principles. Got: {response}"

    @pytest.mark.integration
    @pytest.mark.slow
    def test_adapter_response_quality_metrics(self, adapter_path):
        """Test adapter response quality with various metrics."""
        # Given: Loaded adapter
        from transformers import AutoTokenizer
        from peft import AutoPeftModelForCausalLM

        model = AutoPeftModelForCausalLM.from_pretrained(
            str(adapter_path),
            device_map="auto",
        )
        tokenizer = AutoTokenizer.from_pretrained(str(adapter_path))

        test_cases = [
            {
                "query": "What is Kwanzaa?",
                "expected_terms": ["celebration", "african", "december", "holiday", "culture"],
                "min_words": 15
            },
            {
                "query": "When is Kwanzaa celebrated?",
                "expected_terms": ["december", "january", "26", "days", "seven"],
                "min_words": 10
            },
            {
                "query": "What is Umoja?",
                "expected_terms": ["unity", "principle", "first", "family", "community"],
                "min_words": 10
            }
        ]

        for test_case in test_cases:
            # When: Generating response
            messages = [
                {"role": "system", "content": "You are a knowledgeable assistant about Kwanzaa."},
                {"role": "user", "content": test_case["query"]}
            ]

            text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
            inputs = tokenizer(text, return_tensors="pt").to(model.device)
            outputs = model.generate(**inputs, max_new_tokens=150, temperature=0.6, do_sample=True)
            response = tokenizer.decode(outputs[0][inputs['input_ids'].shape[1]:], skip_special_tokens=True)

            # Then: Check quality metrics
            response_lower = response.lower()
            word_count = len(response.split())

            # Minimum length check
            assert word_count >= test_case["min_words"], \
                f"Response too short for '{test_case['query']}'. Expected >={test_case['min_words']}, got {word_count}"

            # Relevance check - at least one expected term should appear
            terms_found = [term for term in test_case["expected_terms"] if term in response_lower]
            assert len(terms_found) >= 1, \
                f"Response not relevant for '{test_case['query']}'. Expected terms: {test_case['expected_terms']}, Found: {terms_found}. Response: {response}"

    @pytest.mark.integration
    def test_adapter_config_consistency(self, adapter_path, model_config):
        """Test that adapter configuration is consistent with model config."""
        # Given: Adapter and model configs
        from peft import PeftConfig

        adapter_config = PeftConfig.from_pretrained(str(adapter_path))
        model_id = model_config["model"]["model_id"]

        # Then: Base model should match
        assert adapter_config.base_model_name_or_path in model_id or \
               model_id in adapter_config.base_model_name_or_path, \
               f"Adapter base model ({adapter_config.base_model_name_or_path}) should match config model ({model_id})"


# Test markers
pytestmark = [
    pytest.mark.rag,
    pytest.mark.integration,
]
