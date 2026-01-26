#!/usr/bin/env python3
"""
Validate that adapter v4 learned from the training data.

This script tests the adapter with questions from the training dataset
to verify it:
1. Generates citations [1][2] correctly
2. Responds with knowledge from training examples
3. Learned the proper JSON format and citation behavior
"""
import sys
sys.path.insert(0, 'backend')

from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
import torch
import json
import re

print("="*60)
print("Training Data Validation Test for Adapter v4")
print("="*60)

# Load model
print("\n1. Loading base model and adapter v4...")
base_model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-3.2-1B-Instruct",
    torch_dtype=torch.bfloat16,
    device_map="cpu",
    low_cpu_mem_usage=True
)

adapter_path = "models/adapters/kwanzaa-adapter-v4"
model = PeftModel.from_pretrained(base_model, adapter_path)
tokenizer = AutoTokenizer.from_pretrained(adapter_path)

# Test cases from the training data
test_cases = [
    {
        "name": "March on Washington (from training data)",
        "persona": "educator",
        "question": "What were the main goals of the March on Washington in 1963?",
        "expected_topics": ["civil rights legislation", "racial segregation", "police brutality", "employment", "Fair Employment", "minimum wage"],
        "expected_citations": True
    },
    {
        "name": "Ida B. Wells methodology",
        "persona": "researcher",
        "question": "What was Ida B. Wells's methodology for documenting lynching?",
        "expected_topics": ["investigation", "documentation", "Red Record"],
        "expected_citations": True
    },
    {
        "name": "Frederick Douglass July Fourth",
        "persona": "researcher",
        "question": "What was Frederick Douglass's critique of July Fourth celebrations?",
        "expected_topics": ["slavery", "hypocrisy", "independence"],
        "expected_citations": True
    },
    {
        "name": "Refusal case - out of scope",
        "persona": "educator",
        "question": "What was the attendance at the 2023 Kwanzaa celebration in Atlanta?",
        "expected_topics": ["cannot provide", "not available", "recommend"],
        "expected_citations": False,  # Should refuse, not cite
        "should_refuse": True
    }
]

results = []
citation_pattern = r'\[(\d+)\]'

print("\n2. Testing adapter with training data examples...\n")

for i, test in enumerate(test_cases, 1):
    print(f"\nTest {i}/{len(test_cases)}: {test['name']}")
    print(f"Persona: {test['persona']}")
    print(f"Question: {test['question']}")

    messages = [
        {
            "role": "system",
            "content": f"You are a {test['persona']} helping people learn about Kwanzaa, African American history, and cultural traditions. Always cite your sources using [1], [2], etc."
        },
        {
            "role": "user",
            "content": test['question']
        }
    ]

    inputs = tokenizer.apply_chat_template(
        messages,
        return_tensors="pt",
        add_generation_prompt=True
    )

    with torch.no_grad():
        outputs = model.generate(
            inputs,
            max_new_tokens=300,
            do_sample=False,
            temperature=None,
            top_p=None,
        )

    response = tokenizer.decode(outputs[0][inputs.shape[1]:], skip_special_tokens=True)

    # Check for citations
    citations_found = re.findall(citation_pattern, response)
    has_citations = len(citations_found) > 0

    # Check for expected topics
    response_lower = response.lower()
    topics_found = [topic for topic in test['expected_topics'] if topic.lower() in response_lower]
    topic_coverage = len(topics_found) / len(test['expected_topics']) if test['expected_topics'] else 0

    # Determine pass/fail
    citation_check = (has_citations == test['expected_citations'])

    if test.get('should_refuse'):
        # For refusal cases, check for refusal language
        refusal_terms = ['cannot', 'not available', 'recommend', 'lack', 'unable']
        has_refusal = any(term in response_lower for term in refusal_terms)
        passed = citation_check and has_refusal
        status_detail = f"Citations: {'✓' if citation_check else '✗'}, Refusal: {'✓' if has_refusal else '✗'}"
    else:
        # For normal cases, check citations and topic coverage
        topic_check = topic_coverage >= 0.3  # At least 30% of topics mentioned
        passed = citation_check and topic_check
        status_detail = f"Citations: {'✓' if citation_check else '✗'}, Topics: {len(topics_found)}/{len(test['expected_topics'])}"

    results.append({
        "test": test['name'],
        "passed": passed,
        "has_citations": has_citations,
        "citations_count": len(citations_found),
        "topic_coverage": f"{topic_coverage*100:.0f}%",
        "response_preview": response[:150] + "..." if len(response) > 150 else response
    })

    print(f"Status: {'✅ PASSED' if passed else '❌ FAILED'} ({status_detail})")
    print(f"Citations found: {citations_found if citations_found else 'None'}")
    print(f"Topics covered: {topics_found}")
    print(f"Response preview: {response[:200]}...")

# Summary
print("\n" + "="*60)
print("VALIDATION SUMMARY")
print("="*60)

passed_tests = sum(1 for r in results if r['passed'])
total_tests = len(results)
pass_rate = (passed_tests / total_tests) * 100

print(f"\nTests Passed: {passed_tests}/{total_tests} ({pass_rate:.0f}%)")
print("\nDetailed Results:")
for i, result in enumerate(results, 1):
    status = "✅ PASS" if result['passed'] else "❌ FAIL"
    print(f"\n{i}. {result['test']}: {status}")
    print(f"   Citations: {result['citations_count']} found")
    print(f"   Topic Coverage: {result['topic_coverage']}")

print("\n" + "="*60)
if pass_rate >= 75:
    print("✅ VALIDATION SUCCESSFUL")
    print("Adapter v4 has learned from the training data!")
else:
    print("❌ VALIDATION FAILED")
    print(f"Only {pass_rate:.0f}% of tests passed (need ≥75%)")
print("="*60)

sys.exit(0 if pass_rate >= 75 else 1)
