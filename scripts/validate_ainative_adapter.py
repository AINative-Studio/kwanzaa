#!/usr/bin/env python3
"""
Validate AINative Adapter Quality

Tests the trained AINative adapter (Llama-3.2-1B + QLoRA) on platform-specific tasks:
- Agent Swarm orchestration
- AIkit SDK integration (React, Vue, Svelte, Next.js)
- ZeroDB vector operations
- Test-Driven Development patterns
- OpenAPI specifications

This script validates the adapter against the training objectives before integration.
"""

import os
import sys
import json
import torch
from pathlib import Path
from typing import List, Dict, Tuple
from dataclasses import dataclass
from dotenv import load_dotenv

# Add backend to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import PeftModel


@dataclass
class ValidationTest:
    """Test case for adapter validation."""
    category: str
    prompt: str
    expected_keywords: List[str]
    expected_not_keywords: List[str] = None


# Validation test cases
VALIDATION_TESTS = [
    # Agent Swarm Orchestration
    ValidationTest(
        category="Agent Swarm",
        prompt="How do I create a parallel agent swarm with 3 agents using the AINative API?",
        expected_keywords=["POST", "/api/v1/swarms", "parallel", "agents", "json"],
        expected_not_keywords=["Claude", "Anthropic", "AI-generated"]
    ),
    ValidationTest(
        category="Agent Swarm",
        prompt="What's the difference between sequential and parallel agent execution?",
        expected_keywords=["sequential", "parallel", "execution_mode", "order"],
        expected_not_keywords=["Claude", "emoji"]
    ),

    # AIkit SDK Integration
    ValidationTest(
        category="AIkit SDK",
        prompt="Show me how to initialize the AINative React SDK",
        expected_keywords=["import", "AINativeProvider", "apiKey", "React", "component"],
        expected_not_keywords=["Claude", "Anthropic"]
    ),
    ValidationTest(
        category="AIkit SDK",
        prompt="How do I use the useAgentSwarm hook in a Next.js component?",
        expected_keywords=["useAgentSwarm", "import", "Next.js", "component", "hook"],
        expected_not_keywords=["emoji", "AI-generated"]
    ),

    # ZeroDB Operations
    ValidationTest(
        category="ZeroDB",
        prompt="How do I store a vector embedding in ZeroDB?",
        expected_keywords=["POST", "/api/v1/vectors", "embedding", "1536", "metadata"],
        expected_not_keywords=["Claude", "Anthropic"]
    ),
    ValidationTest(
        category="ZeroDB",
        prompt="What's the API endpoint for semantic search in ZeroDB?",
        expected_keywords=["POST", "/api/v1/vectors/search", "query_vector", "limit", "similarity"],
        expected_not_keywords=["emoji", "AI tool"]
    ),

    # Test-Driven Development
    ValidationTest(
        category="TDD/BDD",
        prompt="Write a pytest test for a FastAPI endpoint that creates a user",
        expected_keywords=["pytest", "def test_", "assert", "async", "client"],
        expected_not_keywords=["Claude", "emoji", "Anthropic"]
    ),
    ValidationTest(
        category="TDD/BDD",
        prompt="Show me BDD-style test structure for testing API endpoints",
        expected_keywords=["describe", "context", "it", "expect", "test"],
        expected_not_keywords=["AI-generated", "emoji"]
    ),

    # OpenAPI Specifications
    ValidationTest(
        category="OpenAPI",
        prompt="How do I define a POST endpoint in OpenAPI 3.0 spec?",
        expected_keywords=["paths", "post", "requestBody", "responses", "schema"],
        expected_not_keywords=["Claude", "Anthropic", "emoji"]
    ),
    ValidationTest(
        category="OpenAPI",
        prompt="What's the structure for defining request validation in OpenAPI?",
        expected_keywords=["schema", "properties", "required", "type", "validation"],
        expected_not_keywords=["AI tool", "emoji"]
    ),
]


def load_adapter(adapter_path: Path, base_model: str = "unsloth/Llama-3.2-1B-Instruct") -> Tuple:
    """Load the base model and adapter."""

    print(f"📦 Loading base model: {base_model}")

    # Quantization config for memory efficiency
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_use_double_quant=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16
    )

    # Load base model
    model = AutoModelForCausalLM.from_pretrained(
        base_model,
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=True
    )

    tokenizer = AutoTokenizer.from_pretrained(base_model)
    tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"

    # Load adapter
    print(f"🔧 Loading adapter: {adapter_path}")
    model = PeftModel.from_pretrained(model, adapter_path)
    model.eval()

    return model, tokenizer


def generate_response(model, tokenizer, prompt: str, max_length: int = 512) -> str:
    """Generate response from the model."""

    # Format prompt with Llama-3 chat template
    messages = [
        {"role": "system", "content": "You are an expert in the AINative platform. Provide concise, accurate technical information."},
        {"role": "user", "content": prompt}
    ]

    # Apply chat template
    formatted_prompt = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )

    # Tokenize
    inputs = tokenizer(
        formatted_prompt,
        return_tensors="pt",
        padding=True,
        truncation=True,
        max_length=1024
    ).to(model.device)

    # Generate
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_length,
            temperature=0.7,
            do_sample=True,
            top_p=0.95,
            repetition_penalty=1.1,
            eos_token_id=tokenizer.eos_token_id,
            pad_token_id=tokenizer.pad_token_id
        )

    # Decode
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)

    # Extract only the assistant's response
    if "<|start_header_id|>assistant<|end_header_id|>" in response:
        response = response.split("<|start_header_id|>assistant<|end_header_id|>")[-1]
    elif "assistant" in response.lower():
        # Fallback: try to extract after "assistant"
        parts = response.split("assistant", 1)
        if len(parts) > 1:
            response = parts[1]

    return response.strip()


def validate_response(response: str, test: ValidationTest) -> Dict:
    """Validate a response against test criteria."""

    response_lower = response.lower()

    # Check expected keywords
    found_keywords = [kw for kw in test.expected_keywords if kw.lower() in response_lower]
    missing_keywords = [kw for kw in test.expected_keywords if kw.lower() not in response_lower]

    # Check forbidden keywords
    forbidden_found = []
    if test.expected_not_keywords:
        forbidden_found = [kw for kw in test.expected_not_keywords if kw.lower() in response_lower]

    # Calculate score
    keyword_score = len(found_keywords) / len(test.expected_keywords) if test.expected_keywords else 0
    forbidden_penalty = len(forbidden_found) * 0.2  # -20% per forbidden keyword
    final_score = max(0, keyword_score - forbidden_penalty)

    return {
        "score": final_score,
        "found_keywords": found_keywords,
        "missing_keywords": missing_keywords,
        "forbidden_found": forbidden_found,
        "passed": final_score >= 0.6 and len(forbidden_found) == 0
    }


def main():
    """Run adapter validation tests."""

    # Configuration
    adapter_path = Path(__file__).parent.parent / "outputs" / "adapters" / "ainative-v1"

    if not adapter_path.exists():
        print(f"❌ Adapter not found: {adapter_path}")
        print("\n💡 Please download the adapter first using:")
        print("   python scripts/download_ainative_adapter.py")
        return 1

    print("🚀 AINative Adapter Validation\n")
    print(f"Adapter: {adapter_path}")
    print(f"Tests: {len(VALIDATION_TESTS)}\n")

    # Load adapter
    try:
        model, tokenizer = load_adapter(adapter_path)
    except Exception as e:
        print(f"❌ Failed to load adapter: {e}")
        return 1

    # Run validation tests
    results = []
    category_scores = {}

    for i, test in enumerate(VALIDATION_TESTS, 1):
        print(f"\n{'='*80}")
        print(f"Test {i}/{len(VALIDATION_TESTS)}: {test.category}")
        print(f"{'='*80}")
        print(f"\n📝 Prompt: {test.prompt}\n")

        # Generate response
        try:
            response = generate_response(model, tokenizer, test.prompt)
            print(f"🤖 Response:\n{response}\n")
        except Exception as e:
            print(f"❌ Generation failed: {e}\n")
            continue

        # Validate response
        validation = validate_response(response, test)
        results.append({
            "test": test,
            "response": response,
            "validation": validation
        })

        # Update category scores
        if test.category not in category_scores:
            category_scores[test.category] = []
        category_scores[test.category].append(validation["score"])

        # Print validation results
        status = "✅ PASS" if validation["passed"] else "❌ FAIL"
        print(f"{status} Score: {validation['score']:.1%}")

        if validation["found_keywords"]:
            print(f"  ✅ Found: {', '.join(validation['found_keywords'])}")
        if validation["missing_keywords"]:
            print(f"  ⚠️  Missing: {', '.join(validation['missing_keywords'])}")
        if validation["forbidden_found"]:
            print(f"  ❌ Forbidden: {', '.join(validation['forbidden_found'])}")

    # Summary
    print(f"\n{'='*80}")
    print("📊 VALIDATION SUMMARY")
    print(f"{'='*80}\n")

    total_score = sum(r["validation"]["score"] for r in results) / len(results) if results else 0
    passed_tests = sum(1 for r in results if r["validation"]["passed"])

    print(f"Overall Score: {total_score:.1%}")
    print(f"Tests Passed: {passed_tests}/{len(results)}")
    print()

    print("Category Scores:")
    for category, scores in category_scores.items():
        avg_score = sum(scores) / len(scores)
        print(f"  {category:20s}: {avg_score:.1%}")

    # Zero AI Attribution Check
    print("\n🔍 Zero AI Attribution Check:")
    forbidden_terms = ["Claude", "Anthropic", "AI-generated", "AI tool"]
    all_responses = " ".join(r["response"] for r in results)
    violations = [term for term in forbidden_terms if term.lower() in all_responses.lower()]

    if violations:
        print(f"  ❌ FAILED - Found: {', '.join(violations)}")
    else:
        print(f"  ✅ PASSED - No AI attribution detected")

    # Save results
    output_file = Path(__file__).parent.parent / "outputs" / "ainative_adapter_validation.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w") as f:
        json.dump({
            "overall_score": total_score,
            "tests_passed": passed_tests,
            "total_tests": len(results),
            "category_scores": {k: sum(v)/len(v) for k, v in category_scores.items()},
            "zero_ai_attribution": len(violations) == 0,
            "results": [
                {
                    "category": r["test"].category,
                    "prompt": r["test"].prompt,
                    "response": r["response"],
                    "score": r["validation"]["score"],
                    "passed": r["validation"]["passed"]
                }
                for r in results
            ]
        }, f, indent=2)

    print(f"\n📄 Results saved to: {output_file}")

    # Return success if overall score >= 70% and no AI attribution
    if total_score >= 0.7 and len(violations) == 0:
        print("\n✅ Adapter validation PASSED")
        return 0
    else:
        print("\n❌ Adapter validation FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
