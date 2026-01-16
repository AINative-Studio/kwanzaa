# Kwanzaa Adapter Training Dataset

This directory contains the high-quality training dataset for fine-tuning the Kwanzaa adapter model to produce answer_json-compliant outputs with proper citation, refusal, and grounding behaviors.

## Directory Structure

```
data/training/
├── README.md                          # This file
├── dataset-schema.json                # JSON schema for training samples
├── examples/                          # Training example files
│   ├── citation-examples.json         # Citation behavior examples (3 samples)
│   ├── refusal-examples.json          # Refusal behavior examples (4 samples)
│   ├── grounded-answer-examples.json  # Grounded synthesis examples (3 samples)
│   └── format-compliance-examples.json # Format edge case examples (4 samples)
└── validation/                        # Validation outputs (generated)
    └── validation-report.json
```

## Quick Start

### Validate the Dataset

```bash
# Run validation script
python scripts/validate_training_data.py \
  --schema data/training/dataset-schema.json \
  --examples data/training/examples/ \
  --output data/training/validation/

# View results
cat data/training/validation/validation-report.json
```

### Load Training Data

```python
import json
from pathlib import Path

def load_training_data(examples_dir: str = "data/training/examples/"):
    """Load all training examples from JSON files."""
    samples = []
    for file_path in Path(examples_dir).glob("*.json"):
        with open(file_path) as f:
            data = json.load(f)
            samples.extend(data['samples'])
    return samples

# Usage
training_samples = load_training_data()
print(f"Loaded {len(training_samples)} training samples")

# Filter by category
citation_samples = [s for s in training_samples if s['category'] == 'citation']
refusal_samples = [s for s in training_samples if s['category'] == 'refusal']
```

## Current Dataset Status

**Version:** 1.0.0 (Seed Examples)
**Total Samples:** 14
**Status:** Initial seed dataset for demonstration

### Current Distribution

| Category | Count | Target (160 total) |
|----------|-------|-------------------|
| Citation | 3 | 56 |
| Refusal | 4 | 40 |
| Grounded Answer | 3 | 48 |
| Format Compliance | 4 | 16 |
| **Total** | **14** | **160** |

| Persona | Count | Target |
|---------|-------|--------|
| Educator | 6 | 56 |
| Researcher | 4 | 40 |
| Creator | 3 | 40 |
| Builder | 1 | 24 |

**Next Steps:** Follow the data collection strategy in `/docs/training/dataset-preparation.md` to expand to 160+ training samples.

## Dataset Schema

See `dataset-schema.json` for the complete JSON schema definition.

### Key Fields

Each training sample contains:

```json
{
  "sample_id": "citation_educator_001",
  "category": "citation|refusal|grounded_answer|format_compliance",
  "persona": "educator|researcher|creator|builder",
  "user_query": "User's question",
  "retrieved_context": [
    {
      "rank": 1,
      "score": 0.93,
      "chunk_id": "doc::chunk::1",
      "content": "...",
      "metadata": { /* citation metadata */ }
    }
  ],
  "expected_output": {
    "version": "kwanzaa.answer.v1",
    "answer": { /* ... */ },
    "sources": [ /* ... */ ],
    "retrieval_summary": { /* ... */ },
    "unknowns": { /* ... */ }
  },
  "metadata": {
    "difficulty": "easy|medium|hard",
    "principle_focus": ["Imani", "Nia"],
    "quality_score": 0.95,
    "reviewer": "annotator_id"
  }
}
```

## Usage Guidelines

### For Annotators

1. Read `/docs/training/dataset-preparation.md` thoroughly
2. Follow annotation guidelines in Appendix B
3. Use provided examples as quality reference
4. Validate samples against schema before submission
5. Aim for quality score ≥ 0.85

### For Model Training

1. Load and validate dataset
2. Split into train/validation sets (80/20 or use separate eval set)
3. Format for your training framework (Hugging Face, OpenAI, etc.)
4. Track training metrics against evaluation set
5. Validate outputs against answer_json contract

### For Evaluation

1. Use evaluation set (separate from training)
2. Measure citation accuracy, refusal correctness, format compliance
3. Calculate per-category and per-persona metrics
4. Compare against baseline model
5. Iterate on dataset based on failure analysis

## Quality Standards

All samples must meet:

- **Schema Validity:** 100% pass JSON schema validation
- **Quality Score:** ≥ 0.85 (target: ≥ 0.90 average)
- **Realism:** Natural queries, realistic retrieval
- **Educational Value:** Teaches distinct pattern
- **Diversity:** No duplicate scenarios

See dataset preparation doc for detailed quality criteria.

## Contributing

### Adding New Examples

1. Create examples following the schema
2. Place in appropriate category file (or create new file)
3. Run validation script
4. Submit PR with validation report
5. Include rationale in PR description

### Improving Existing Examples

1. Identify issue with existing sample
2. Propose improvement with justification
3. Update quality_score if applicable
4. Document changes in metadata.notes
5. Re-validate before submitting

## Related Documentation

- **Dataset Preparation Strategy:** `/docs/training/dataset-preparation.md`
- **Answer JSON Contract:** `/docs/answer_json_contract.md`
- **Semantic Search API:** `/docs/api/semantic-search-api.md`
- **Project README:** `/README.md`

## License

Training dataset follows the same license as the Kwanzaa project:
- Code/Infrastructure: Apache 2.0
- Training samples: CC BY-NC 4.0 (non-commercial use)
- Original sources: As specified in metadata (typically Public Domain)

## Questions?

- File an issue: https://github.com/AINative-Studio/kwanzaa/issues
- Review documentation: `/docs/training/dataset-preparation.md`
- Check schema: `dataset-schema.json`

---

**Maintained by:** AINative Studio
**Project:** Kwanzaa - First Fruits for AI
**Last Updated:** January 16, 2026
