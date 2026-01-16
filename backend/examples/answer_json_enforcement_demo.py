"""Demonstration of answer_json enforcement mechanisms.

This example shows how the validation enforcement prevents raw text blobs
and ensures 100% compliance with the answer_json contract.

Run this example with:
    python -m backend.examples.answer_json_enforcement_demo
"""

import asyncio
from datetime import datetime, timezone
from uuid import uuid4

from app.utils.answer_validation import (
    AnswerValidationError,
    validate_answer_json,
    is_valid_answer_json,
    get_validation_errors,
)
from app.utils.response_enforcement import (
    validate_and_convert_response,
    create_validation_error_response,
    AnswerJsonResponseValidator,
)


def print_section(title: str):
    """Print a section header."""
    print(f"\n{'=' * 70}")
    print(f"  {title}")
    print(f"{'=' * 70}\n")


def example_1_raw_text_blob_rejected():
    """Example 1: Raw text blob is rejected."""
    print_section("Example 1: Raw Text Blob - REJECTED")

    # This is what we DON'T want - a raw text blob
    raw_text_response = {
        "response": "The Civil Rights Act of 1964 was landmark legislation that prohibited discrimination based on race, color, religion, sex, or national origin.",
        "model": "gpt-4",
        "timestamp": "2026-01-16T10:00:00Z",
    }

    print("Attempting to validate raw text response:")
    print(f"{raw_text_response}\n")

    # Try to validate
    if is_valid_answer_json(raw_text_response):
        print("✅ VALID - Response conforms to answer_json")
    else:
        print("❌ INVALID - Response does NOT conform to answer_json")

        # Get detailed errors
        errors = get_validation_errors(raw_text_response)
        print(f"\nValidation errors ({len(errors)} total):")
        for error in errors[:5]:  # Show first 5 errors
            print(f"  • {error.field}: {error.message}")

        if len(errors) > 5:
            print(f"  ... and {len(errors) - 5} more errors")

    print("\n⚠️  This response would be REJECTED by the middleware")
    print("   The UI would never receive this raw text blob")


def example_2_valid_structured_response():
    """Example 2: Valid structured response is accepted."""
    print_section("Example 2: Valid Structured Response - ACCEPTED")

    # This is what we WANT - a complete answer_json response
    valid_response = {
        "version": "kwanzaa.answer.v1",
        "persona": "educator",
        "model_mode": "base_adapter_rag",
        "toggles": {
            "require_citations": True,
            "primary_sources_only": False,
            "creative_mode": False,
        },
        "answer": {
            "text": "The Civil Rights Act of 1964 was landmark legislation that prohibited discrimination based on race, color, religion, sex, or national origin.",
            "confidence": 0.95,
            "tone": "neutral",
            "completeness": "complete",
        },
        "sources": [
            {
                "citation_label": "National Archives (1964) — Civil Rights Act",
                "canonical_url": "https://www.archives.gov/milestone-documents/civil-rights-act",
                "source_org": "National Archives",
                "year": 1964,
                "content_type": "proclamation",
                "license": "Public Domain",
                "namespace": "kwanzaa_primary_sources",
                "doc_id": "nara_cra_1964",
                "chunk_id": "nara_cra_1964::chunk::3",
            }
        ],
        "retrieval_summary": {
            "query": "What did the Civil Rights Act of 1964 prohibit?",
            "top_k": 5,
            "namespaces": ["kwanzaa_primary_sources"],
            "results": [
                {
                    "rank": 1,
                    "score": 0.95,
                    "snippet": "An Act to enforce the constitutional right to vote...",
                    "citation_label": "National Archives (1964) — Civil Rights Act",
                    "canonical_url": "https://www.archives.gov/milestone-documents/civil-rights-act",
                    "doc_id": "nara_cra_1964",
                    "chunk_id": "nara_cra_1964::chunk::3",
                    "namespace": "kwanzaa_primary_sources",
                }
            ],
        },
        "unknowns": {
            "unsupported_claims": [],
            "missing_context": [],
            "clarifying_questions": [],
        },
        "integrity": {
            "citation_required": True,
            "citations_provided": True,
            "retrieval_confidence": "high",
            "fallback_behavior": "not_needed",
        },
        "provenance": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "retrieval_run_id": str(uuid4()),
            "assistant_message_id": str(uuid4()),
        },
    }

    print("Validating complete answer_json response...")

    if is_valid_answer_json(valid_response):
        print("✅ VALID - Response conforms to answer_json")

        # Convert to Pydantic model
        validated = validate_answer_json(valid_response)

        print("\nValidated response details:")
        print(f"  Version: {validated.version}")
        print(f"  Persona: {validated.persona.value}")
        print(f"  Answer text: {validated.answer.text[:80]}...")
        print(f"  Sources: {len(validated.sources)} citation(s)")
        print(f"  Retrieval results: {len(validated.retrieval_summary.results)}")
        print(f"  Confidence: {validated.answer.confidence:.2f}")

        print("\n✅ This response would be ACCEPTED and passed to the UI")
    else:
        print("❌ INVALID - Unexpected validation failure")


def example_3_missing_required_fields():
    """Example 3: Response with missing required fields."""
    print_section("Example 3: Missing Required Fields - REJECTED")

    # Missing critical fields
    incomplete_response = {
        "version": "kwanzaa.answer.v1",
        "answer": {
            "text": "Some answer text",
            "confidence": 0.8,
            "tone": "neutral",
            "completeness": "complete",
        },
        # Missing: sources, retrieval_summary, unknowns, etc.
    }

    print("Attempting to validate response with missing fields...")

    try:
        validated = validate_answer_json(incomplete_response)
        print("✅ VALID (unexpected)")
    except AnswerValidationError as e:
        print("❌ INVALID - Response has validation errors")
        print(f"\nError: {e.message}")
        print(f"\nValidation errors ({len(e.errors)} total):")

        for error in e.errors:
            print(f"  • {error.field}: {error.message}")

        print("\n⚠️  The middleware would return a 422 error with:")
        error_response = create_validation_error_response(e)
        print(f"    Error code: {error_response['error_code']}")
        print(f"    Message: {error_response['message']}")
        print(f"    Suggestions: {error_response['details']['suggestions'][0]}")


def example_4_invalid_field_values():
    """Example 4: Response with invalid field values."""
    print_section("Example 4: Invalid Field Values - REJECTED")

    # Invalid field values
    invalid_response = {
        "version": "invalid_version",  # Wrong pattern
        "persona": "educator",
        "model_mode": "base_adapter_rag",
        "toggles": {
            "require_citations": True,
            "primary_sources_only": False,
            "creative_mode": False,
        },
        "answer": {
            "text": "Answer text",
            "confidence": 1.5,  # Out of range (0.0-1.0)
            "tone": "neutral",
            "completeness": "complete",
        },
        "sources": [
            {
                "citation_label": "Test",
                "canonical_url": "not-a-valid-url",  # Invalid URL
                "source_org": "Test Org",
                "year": 2020,
                "content_type": "article",
                "license": "MIT",
                "namespace": "test",
                "doc_id": "test",
                "chunk_id": "test",
            }
        ],
        "retrieval_summary": {
            "query": "test",
            "top_k": 5,
            "namespaces": ["test"],
            "results": [],
        },
        "unknowns": {
            "unsupported_claims": [],
            "missing_context": [],
            "clarifying_questions": [],
        },
        "integrity": {
            "citation_required": True,
            "citations_provided": True,
            "retrieval_confidence": "high",
            "fallback_behavior": "not_needed",
        },
        "provenance": {
            "generated_at": "2026-01-16T10:00:00Z",
            "retrieval_run_id": str(uuid4()),
            "assistant_message_id": str(uuid4()),
        },
    }

    print("Validating response with invalid field values...")

    errors = get_validation_errors(invalid_response)

    if errors:
        print(f"❌ INVALID - Found {len(errors)} validation error(s):")

        for error in errors:
            print(f"  • {error.field}: {error.message}")

        print("\n⚠️  Common issues detected:")
        if any("version" in e.field for e in errors):
            print("    • Version must match pattern: kwanzaa.answer.v[0-9]+")
        if any("confidence" in e.field for e in errors):
            print("    • Confidence must be between 0.0 and 1.0")
        if any("canonical_url" in e.field for e in errors):
            print("    • URL must be valid (start with http:// or https://)")


def example_5_batch_validation():
    """Example 5: Batch validation of multiple responses."""
    print_section("Example 5: Batch Validation")

    validator = AnswerJsonResponseValidator()

    # Create test responses
    valid_response = {
        "version": "kwanzaa.answer.v1",
        "persona": "educator",
        "model_mode": "base_adapter_rag",
        "toggles": {
            "require_citations": False,
            "primary_sources_only": False,
            "creative_mode": False,
        },
        "answer": {
            "text": "Test",
            "confidence": 0.9,
            "tone": "neutral",
            "completeness": "complete",
        },
        "sources": [],
        "retrieval_summary": {
            "query": "test",
            "top_k": 5,
            "namespaces": ["test"],
            "results": [],
        },
        "unknowns": {
            "unsupported_claims": [],
            "missing_context": [],
            "clarifying_questions": [],
        },
        "integrity": {
            "citation_required": False,
            "citations_provided": False,
            "retrieval_confidence": "high",
            "fallback_behavior": "not_needed",
        },
        "provenance": {
            "generated_at": "2026-01-16T10:00:00Z",
            "retrieval_run_id": str(uuid4()),
            "assistant_message_id": str(uuid4()),
        },
    }

    invalid_response_1 = {"invalid": "data1"}
    invalid_response_2 = {"invalid": "data2"}

    responses = [
        valid_response,
        invalid_response_1,
        valid_response.copy(),
        invalid_response_2,
        valid_response.copy(),
    ]

    print(f"Validating batch of {len(responses)} responses...")

    valid, errors = validator.validate_batch(responses, fail_fast=False)

    print(f"\n✅ Valid responses: {len(valid)}")
    print(f"❌ Invalid responses: {len(errors)}")

    if errors:
        print("\nInvalid response indices:")
        for idx, error in errors:
            print(f"  • Index {idx}: {error.message}")

    # Calculate pass rate
    pass_rate = len(valid) / len(responses) * 100
    print(f"\nValidation pass rate: {pass_rate:.1f}%")

    if pass_rate < 100:
        print("⚠️  Warning: Not all responses conform to answer_json")
        print("   These responses would be rejected by the middleware")


def example_6_error_recovery():
    """Example 6: Automatic error recovery."""
    print_section("Example 6: Automatic Error Recovery")

    validator = AnswerJsonResponseValidator()

    # Response with missing unknowns (can be auto-fixed)
    recoverable_response = {
        "version": "kwanzaa.answer.v1",
        "persona": "educator",
        "model_mode": "base_adapter_rag",
        "toggles": {
            "require_citations": False,
            "primary_sources_only": False,
            "creative_mode": False,
        },
        "answer": {
            "text": "Test answer",
            "confidence": 0.9,
            "tone": "neutral",
            "completeness": "complete",
        },
        "sources": [],
        "retrieval_summary": {
            "query": "test",
            "top_k": 5,
            "namespaces": ["test"],
            "results": [],
        },
        # Missing unknowns - can be auto-filled with empty arrays
        "integrity": {
            "citation_required": False,
            "citations_provided": False,
            "retrieval_confidence": "high",
            "fallback_behavior": "not_needed",
        },
        "provenance": {
            "generated_at": "2026-01-16T10:00:00Z",
            "retrieval_run_id": str(uuid4()),
            "assistant_message_id": str(uuid4()),
        },
    }

    print("Attempting to validate response with missing 'unknowns' field...")

    # First try normal validation
    if is_valid_answer_json(recoverable_response):
        print("✅ Valid (no recovery needed)")
    else:
        print("❌ Invalid - attempting automatic recovery...")

        # Attempt recovery
        recovered = validator.attempt_error_recovery(recoverable_response)

        if recovered:
            print("✅ Recovery successful!")
            print("\nRecovered response:")
            print(f"  • unknowns.unsupported_claims: {recovered.unknowns.unsupported_claims}")
            print(f"  • unknowns.missing_context: {recovered.unknowns.missing_context}")
            print(f"  • unknowns.clarifying_questions: {recovered.unknowns.clarifying_questions}")
            print("\n✅ Response can now be used")
        else:
            print("❌ Recovery failed - error is not automatically fixable")


def example_7_streaming_validation():
    """Example 7: Streaming response validation."""
    print_section("Example 7: Streaming Response Validation")

    validator = AnswerJsonResponseValidator()

    # Simulate streaming chunks
    chunk_1 = {
        "version": "kwanzaa.answer.v1",
        "answer": {"text": "The Civil Rights Act..."},
    }

    chunk_2 = {
        "version": "kwanzaa.answer.v1",
        "answer": {
            "text": "The Civil Rights Act of 1964 was landmark legislation...",
        },
    }

    final_chunk = {
        "version": "kwanzaa.answer.v1",
        "persona": "educator",
        "model_mode": "base_adapter_rag",
        "toggles": {
            "require_citations": True,
            "primary_sources_only": False,
            "creative_mode": False,
        },
        "answer": {
            "text": "The Civil Rights Act of 1964 was landmark legislation.",
            "confidence": 0.95,
            "tone": "neutral",
            "completeness": "complete",
        },
        "sources": [],
        "retrieval_summary": {
            "query": "Tell me about the Civil Rights Act",
            "top_k": 5,
            "namespaces": ["kwanzaa_primary_sources"],
            "results": [],
        },
        "unknowns": {
            "unsupported_claims": [],
            "missing_context": [],
            "clarifying_questions": [],
        },
        "integrity": {
            "citation_required": True,
            "citations_provided": False,
            "retrieval_confidence": "high",
            "fallback_behavior": "not_needed",
        },
        "provenance": {
            "generated_at": "2026-01-16T10:00:00Z",
            "retrieval_run_id": str(uuid4()),
            "assistant_message_id": str(uuid4()),
        },
    }

    print("Validating streaming chunks...\n")

    # Validate intermediate chunks (relaxed validation)
    result_1 = validator.validate_streaming_chunk(chunk_1, is_final_chunk=False)
    print(f"Chunk 1 (intermediate): {'✅ Valid' if result_1 else '❌ Invalid'}")

    result_2 = validator.validate_streaming_chunk(chunk_2, is_final_chunk=False)
    print(f"Chunk 2 (intermediate): {'✅ Valid' if result_2 else '❌ Invalid'}")

    # Validate final chunk (full validation)
    result_final = validator.validate_streaming_chunk(final_chunk, is_final_chunk=True)
    print(f"Final chunk: {'✅ Valid' if result_final else '❌ Invalid'}")

    print("\nℹ️  Intermediate chunks use relaxed validation")
    print("   Only the final chunk requires full answer_json compliance")


def main():
    """Run all examples."""
    print("\n" + "=" * 70)
    print("  ANSWER_JSON ENFORCEMENT DEMONSTRATION")
    print("  Preventing Raw Text Blobs & Ensuring 100% Compliance")
    print("=" * 70)

    example_1_raw_text_blob_rejected()
    example_2_valid_structured_response()
    example_3_missing_required_fields()
    example_4_invalid_field_values()
    example_5_batch_validation()
    example_6_error_recovery()
    example_7_streaming_validation()

    print("\n" + "=" * 70)
    print("  DEMONSTRATION COMPLETE")
    print("=" * 70)
    print("\nKey Takeaways:")
    print("  • Raw text blobs are REJECTED - only structured JSON passes")
    print("  • All required fields must be present and valid")
    print("  • Detailed error messages help debug validation failures")
    print("  • Batch validation allows checking multiple responses")
    print("  • Automatic recovery can fix simple issues")
    print("  • Streaming responses have relaxed intermediate validation")
    print("\n  See docs/api/answer-json-enforcement.md for more details")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
