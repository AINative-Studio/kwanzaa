#!/usr/bin/env python3
"""
Diagnose which specific educator test cases are failing citation coverage.
"""
import re
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel, PeftConfig

# Test questions from test_citation_coverage.py
EDUCATOR_TESTS = [
    {"id": "edu_001", "question": "When was the Emancipation Proclamation signed, and what did it declare?"},
    {"id": "edu_002", "question": "What innovations did George Washington Carver develop using peanuts?"},
    {"id": "edu_003", "question": "What were the key provisions of the Voting Rights Act of 1965?"},
    {"id": "edu_004", "question": "What was the outcome of Brown v. Board of Education and why was it significant?"},
    {"id": "edu_005", "question": "Describe the role of the Tuskegee Airmen during World War II."},
    {"id": "edu_006", "question": "What were the main goals of the March on Washington in 1963?"},
    {"id": "edu_007", "question": "Who were the Little Rock Nine and what challenges did they face?"},
    {"id": "edu_008", "question": "What contributions did Katherine Johnson make to NASA's space program?"},
    {"id": "edu_009", "question": "Explain the significance of Juneteenth in American history."},
    {"id": "edu_010", "question": "What was the purpose of the Freedmen's Bureau after the Civil War?"},
    {"id": "edu_011", "question": "What specific achievements did Mae Jemison accomplish in space?"},
    {"id": "edu_012", "question": "What were the core principles established in the Black Panther Party's Ten-Point Program?"},
]

# Citation detection patterns
CITATION_PATTERNS = [
    r'\[\d+\]',  # [1], [2], etc.
    r'\(\w+\s+(?:et al\.,?\s+)?\d{4}\)',  # (Author 2020)
    r'(?:according to|as noted in|citing|per)\s+[A-Z][\w\s]+\s*\(\d{4}\)',
    r'(?:source|ref|reference):\s*[A-Z]',
]

def has_citations(text):
    """Check if text contains any citation patterns."""
    for pattern in CITATION_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False

def test_question(model, tokenizer, question):
    """Test a single question and return response."""
    messages = [
        {"role": "system", "content": "You are Kwanzaa Bot, an educational assistant focused on African American history and culture. Always cite your sources using [1], [2] format."},
        {"role": "user", "content": question}
    ]

    inputs = tokenizer.apply_chat_template(
        messages,
        add_generation_prompt=True,
        return_tensors="pt"
    ).to(model.device)

    with torch.no_grad():
        outputs = model.generate(
            inputs,
            max_new_tokens=300,
            temperature=0.7,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id
        )

    response = tokenizer.decode(outputs[0][inputs.shape[1]:], skip_special_tokens=True)
    return response

def main():
    print("=" * 80)
    print("DIAGNOSING EDUCATOR TEST FAILURES")
    print("=" * 80)

    # Load adapter
    print("\n1. Loading adapter v2...")
    adapter_path = "backend/models/adapters/kwanzaa-adapter-v2"
    base_model = "meta-llama/Llama-3.2-1B-Instruct"

    model = AutoModelForCausalLM.from_pretrained(
        base_model,
        device_map="auto",
        torch_dtype=torch.bfloat16,
    )
    model = PeftModel.from_pretrained(model, adapter_path)
    tokenizer = AutoTokenizer.from_pretrained(adapter_path)

    print("✓ Adapter loaded\n")

    # Test each question
    print("2. Testing each educator question...\n")

    passed = []
    failed = []

    for test in EDUCATOR_TESTS:
        print(f"Testing {test['id']}: {test['question'][:60]}...")
        response = test_question(model, tokenizer, test['question'])

        has_citation = has_citations(response)

        if has_citation:
            passed.append(test)
            print(f"  ✓ PASS - Citations found")
        else:
            failed.append(test)
            print(f"  ✗ FAIL - No citations")
            print(f"  Response: {response[:150]}...")

        print()

    # Summary
    print("=" * 80)
    print("RESULTS SUMMARY")
    print("=" * 80)
    print(f"Passed: {len(passed)}/12 ({len(passed)/12*100:.1f}%)")
    print(f"Failed: {len(failed)}/12 ({len(failed)/12*100:.1f}%)")

    if failed:
        print("\nFAILING TEST CASES:")
        for test in failed:
            print(f"  - {test['id']}: {test['question']}")

    print("\n" + "=" * 80)
    print("RECOMMENDATION: Create training examples for failing cases")
    print("=" * 80)

if __name__ == "__main__":
    main()
