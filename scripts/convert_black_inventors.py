#!/usr/bin/env python3
"""
Convert Black Inventors quiz data to Kwanzaa training format.
"""

import json
from datetime import datetime
from pathlib import Path

# Black Inventors data from HuggingFace Space
BLACK_INVENTORS_DATA = [
    {
        "question": "Who invented the traffic signal?",
        "options": ["Garrett Morgan", "George Washington Carver", "Lewis Latimer", "Madam C.J. Walker"],
        "answer": "Garrett Morgan",
        "fact": "Garrett Morgan invented the three-position traffic signal in 1923 after witnessing a terrible accident.",
        "image": "https://upload.wikimedia.org/wikipedia/commons/1/1f/Garrett_Morgan.jpg"
    },
    {
        "question": "Who invented peanut butter?",
        "options": ["Garrett Morgan", "George Washington Carver", "Elijah McCoy", "Lonnie Johnson"],
        "answer": "George Washington Carver",
        "fact": "Carver developed over 300 uses for peanuts and revolutionized agriculture in the American South.",
        "image": "https://upload.wikimedia.org/wikipedia/commons/9/9c/George_Washington_Carver_c1910_-_Restoration.jpg"
    },
    {
        "question": "Who invented the carbon filament for light bulbs?",
        "options": ["Lewis Latimer", "Sarah Boone", "Garrett Morgan", "Frederick Jones"],
        "answer": "Lewis Latimer",
        "fact": "Latimer worked with Edison and invented the carbon filament making bulbs practical for everyday use.",
        "image": "https://upload.wikimedia.org/wikipedia/commons/4/4b/Lewis_Howard_Latimer.jpg"
    },
    {
        "question": "Who invented the modern-day refrigerator truck?",
        "options": ["Frederick Jones", "Madam C.J. Walker", "Lewis Latimer", "Patricia Bath"],
        "answer": "Frederick Jones",
        "fact": "Jones held over 60 patents, including portable air-cooling units revolutionizing perishable food transport.",
        "image": "https://upload.wikimedia.org/wikipedia/commons/5/5f/Frederick_McKinley_Jones.jpg"
    },
    {
        "question": "Who invented the ironing board?",
        "options": ["Sarah Boone", "Lewis Latimer", "Patricia Bath", "Elijah McCoy"],
        "answer": "Sarah Boone",
        "fact": "Boone improved the ironing board in 1892 with a narrower, curved design for pressing clothing.",
        "image": "https://upload.wikimedia.org/wikipedia/commons/4/4a/Sarah_Boone_inventor.jpg"
    },
    {
        "question": "Who developed the first successful laser cataract surgery technique?",
        "options": ["Patricia Bath", "Elijah McCoy", "Lonnie Johnson", "Madam C.J. Walker"],
        "answer": "Patricia Bath",
        "fact": "Dr. Bath was the first African American woman doctor receiving a medical patent for pioneering laser surgery.",
        "image": "https://upload.wikimedia.org/wikipedia/commons/7/7e/Dr._Patricia_Bath.jpg"
    },
    {
        "question": "Who invented the Super Soaker water gun?",
        "options": ["Lonnie Johnson", "Madam C.J. Walker", "Lewis Latimer", "Garrett Morgan"],
        "answer": "Lonnie Johnson",
        "fact": "Johnson, a NASA engineer, invented the Super Soaker becoming one of the most popular toys ever.",
        "image": "https://upload.wikimedia.org/wikipedia/commons/3/3a/Lonnie_Johnson_2010.jpg"
    },
    {
        "question": "Who invented the automatic lubricator for steam engines, known as 'the real McCoy'?",
        "options": ["Elijah McCoy", "Sarah Boone", "Frederick Jones", "Garrett Morgan"],
        "answer": "Elijah McCoy",
        "fact": "McCoy's automatic oiling device was so superior that people requested 'the real McCoy.' He held 57 patents.",
        "image": "https://upload.wikimedia.org/wikipedia/commons/7/7f/Elijah_McCoy_three-quarter_length_portrait.jpg"
    },
    {
        "question": "Who was the first Black woman millionaire in America due to her haircare products?",
        "options": ["Madam C.J. Walker", "Patricia Bath", "Sarah Boone", "Lewis Latimer"],
        "answer": "Madam C.J. Walker",
        "fact": "Walker built a beauty empire in the early 1900s becoming one of the most successful self-made women.",
        "image": "https://upload.wikimedia.org/wikipedia/commons/4/49/Madam_CJ_Walker_1914.jpg"
    },
    {
        "question": "Who invented improvements to the portable pencil sharpener?",
        "options": ["John Lee Love", "Garrett Morgan", "Elijah McCoy", "Lonnie Johnson"],
        "answer": "John Lee Love",
        "fact": "Love invented the portable pencil sharpener in 1897 with shaving collection, a design still used today.",
        "image": "https://upload.wikimedia.org/wikipedia/commons/7/7f/John_Lee_Love.jpg"
    },
    {
        "question": "Who invented the home security system?",
        "options": ["Marie Van Brittan Brown", "George Washington Carver", "Frederick Jones", "Garrett Morgan"],
        "answer": "Marie Van Brittan Brown",
        "fact": "Brown invented the first home security system in 1966 including cameras, monitors, and microphones.",
        "image": "https://upload.wikimedia.org/wikipedia/commons/5/5f/Marie_Van_Brittan_Brown.jpg"
    },
    {
        "question": "Who invented the synchronous multiplex railway telegraph?",
        "options": ["Granville T. Woods", "Lewis Latimer", "Frederick Jones", "Garrett Morgan"],
        "answer": "Granville T. Woods",
        "fact": "Woods invented the synchronous multiplex railway telegraph and held over 50 patents improving railway safety.",
        "image": "https://upload.wikimedia.org/wikipedia/commons/3/3b/Granville_T._Woods.jpg"
    },
    {
        "question": "Who invented the modern blood bank?",
        "options": ["Dr. Charles Drew", "Patricia Bath", "Frederick Jones", "Lonnie Johnson"],
        "answer": "Dr. Charles Drew",
        "fact": "Drew developed blood plasma storage techniques leading to first large-scale blood banks during WWII.",
        "image": "https://upload.wikimedia.org/wikipedia/commons/4/4e/Charles_Drew_c1940s.jpg"
    },
    {
        "question": "Who invented the golf tee?",
        "options": ["Dr. George Grant", "John Lee Love", "Elijah McCoy", "Lewis Latimer"],
        "answer": "Dr. George Grant",
        "fact": "Grant, a Harvard-trained dentist, invented the wooden golf tee in 1899 replacing sand piles.",
        "image": "https://upload.wikimedia.org/wikipedia/commons/6/6a/George_Franklin_Grant.jpg"
    },
    {
        "question": "Who invented improvements to the chamber commode?",
        "options": ["Thomas Elkins", "Sarah Boone", "Lewis Latimer", "Frederick Jones"],
        "answer": "Thomas Elkins",
        "fact": "Elkins patented an improved chamber commode in 1872 with features like bookshelves and washstands.",
        "image": "https://upload.wikimedia.org/wikipedia/commons/7/7f/Thomas_Elkins.jpg"
    },
    {
        "question": "Who invented the folding chair?",
        "options": ["Nathaniel Alexander", "John Purdy", "Sarah Boone", "Garrett Morgan"],
        "answer": "Nathaniel Alexander",
        "fact": "Alexander patented the folding chair in 1911, improving portability and becoming event standard.",
        "image": "https://upload.wikimedia.org/wikipedia/commons/5/5f/Nathaniel_Alexander.jpg"
    },
    {
        "question": "Who invented the potato chip?",
        "options": ["George Crum", "George Washington Carver", "Frederick Jones", "Lonnie Johnson"],
        "answer": "George Crum",
        "fact": "Crum, a chef, invented the potato chip in 1853 when a customer complained fries were too thick.",
        "image": "https://upload.wikimedia.org/wikipedia/commons/4/4a/George_Crum.jpg"
    }
]


def create_training_sample(inventor_data: dict, idx: int) -> dict:
    """Convert inventor quiz data to training sample format."""

    # Extract inventor name and create citation
    answer = inventor_data["answer"]
    fact = inventor_data["fact"]
    question = inventor_data["question"]

    # Create simulated retrieval context
    retrieved_context = [{
        "rank": 1,
        "score": 0.92,
        "content": fact,
        "metadata": {
            "citation_label": f"{answer} — Black Inventor",
            "canonical_url": inventor_data["image"],
            "source_org": "Wikipedia",
            "year": None,  # Will extract from fact if possible
            "content_type": "biographical",
            "license": "Public Domain"
        }
    }]

    # Create expected output with citation
    expected_output = {
        "version": "kwanzaa.answer.v1",
        "persona": "educator",
        "model_mode": "base_adapter_rag",
        "toggles": {
            "require_citations": True,
            "primary_sources_only": False,
            "creative_mode": False
        },
        "answer": {
            "text": f"{answer} {fact.replace(answer, '[1]', 1)}",
            "confidence": 0.92,
            "tone": "educational",
            "completeness": "complete"
        },
        "sources": [{
            "citation_label": f"{answer} — Black Inventor",
            "canonical_url": inventor_data["image"],
            "source_org": "Wikipedia",
            "year": None,
            "content_type": "biographical",
            "license": "Public Domain",
            "namespace": "kwanzaa_inventors",
            "doc_id": f"inventor_{answer.lower().replace(' ', '_').replace('.', '')}",
            "chunk_id": f"inventor_{answer.lower().replace(' ', '_').replace('.', '')}_bio",
            "tags": ["inventor", "innovation", "african_american_history"],
            "relevance_score": 0.92
        }],
        "retrieval_summary": {
            "query": question,
            "top_k": 10,
            "namespaces": ["kwanzaa_inventors"],
            "filters": {},
            "results": [{
                "rank": 1,
                "score": 0.92,
                "snippet": fact[:100] + "...",
                "citation_label": f"{answer} — Black Inventor",
                "canonical_url": inventor_data["image"],
                "doc_id": f"inventor_{answer.lower().replace(' ', '_').replace('.', '')}",
                "chunk_id": f"inventor_{answer.lower().replace(' ', '_').replace('.', '')}_bio",
                "namespace": "kwanzaa_inventors"
            }],
            "execution_time_ms": 245
        },
        "unknowns": {
            "unsupported_claims": [],
            "missing_context": [],
            "clarifying_questions": []
        },
        "integrity": {
            "citation_required": True,
            "citations_provided": True,
            "retrieval_confidence": "high",
            "fallback_behavior": "not_needed"
        },
        "provenance": {
            "generated_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        }
    }

    # Create training sample
    sample = {
        "sample_id": f"inventor_{idx:03d}",
        "category": "grounded_answer",
        "persona": "educator",
        "user_query": question,
        "retrieved_context": retrieved_context,
        "expected_output": expected_output,
        "metadata": {
            "difficulty": "easy",
            "principles": ["nia", "kuumba"],
            "quality_score": 0.9,
            "source": "black_inventors_quiz",
            "notes": f"Black inventor: {answer}",
            "tags": ["inventor", "innovation", "african_american_history"]
        }
    }

    return sample


def main():
    """Convert all Black Inventors data to training format."""

    print("=" * 80)
    print("Converting Black Inventors Quiz Data to Training Format")
    print("=" * 80)

    # Create samples
    samples = []
    for idx, inventor_data in enumerate(BLACK_INVENTORS_DATA, 1):
        sample = create_training_sample(inventor_data, idx)
        samples.append(sample)
        print(f"✓ Converted: {inventor_data['answer']}")

    # Create dataset
    dataset = {
        "dataset_name": "Black Inventors Examples",
        "version": "1.0.0",
        "description": "Training examples for Black inventors and their innovations",
        "source": "https://huggingface.co/spaces/Hyram33/black-inventors",
        "license": "Educational Use",
        "created_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "total_samples": len(samples),
        "samples": samples
    }

    # Save to file
    output_path = Path("data/training/examples/black-inventors-examples.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump(dataset, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Saved {len(samples)} samples to: {output_path}")
    print(f"\nSample breakdown:")
    print(f"  - Total: {len(samples)}")
    print(f"  - Category: grounded_answer")
    print(f"  - Persona: educator")
    print(f"  - All with citations")

    print("\n" + "=" * 80)
    print("SUCCESS! Black Inventors dataset ready for training")
    print("=" * 80)


if __name__ == "__main__":
    main()
