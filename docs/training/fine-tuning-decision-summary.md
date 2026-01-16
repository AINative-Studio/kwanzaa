# Fine-Tuning Strategy Decision Summary

**Issue:** #32 - E3A-US1 Select Fine-Tuning Strategy
**Date:** January 16, 2026
**Status:** DECIDED - QLoRA Selected

## Executive Decision

**Recommended Strategy: QLoRA with 4-bit NF4 Quantization**

After comprehensive analysis of VRAM requirements, cost implications, quality trade-offs, and infrastructure constraints, we recommend **QLoRA (Quantized LoRA) with 4-bit quantization** for the Kwanzaa adapter training.

## Quick Comparison

| Factor | LoRA (FP16/BF16) | QLoRA (4-bit) | Winner |
|--------|------------------|---------------|---------|
| **VRAM Required** | 28-32 GB | 10-12 GB | QLoRA (63% reduction) |
| **Training Cost** | $10-15 | $5-10 | QLoRA (50% cheaper) |
| **Hardware Access** | A100 80GB only | RTX 3090/4090, A10G | QLoRA (democratized) |
| **Training Speed** | 25 min/run | 35 min/run | LoRA (but acceptable) |
| **Final Quality** | 100% baseline | 98-99% baseline | LoRA (marginal) |
| **Budget Fit** | Good ($10-15) | Excellent ($5-10) | QLoRA |

**Overall Winner: QLoRA** (8.7/10 vs 7.1/10 weighted score)

## Key Benefits of QLoRA

1. **Cost Efficiency:** $5-10 total vs $500-5,000 budget (99% under budget)
2. **Accessibility:** Runs on consumer GPUs (RTX 3090/4090), enabling community reproduction
3. **Quality:** 98-99% of LoRA performance, meets all Kwanzaa targets
4. **Proven:** Widely adopted, extensive validation in production systems
5. **Iteration Speed:** Low cost enables 10+ training runs for refinement

## Accepted Trade-offs

1. **1-2% Quality Degradation:** QLoRA achieves 98% of LoRA performance
   - **Why Acceptable:** Kwanzaa targets are 90% citation coverage (not 99%)
   - **Evidence:** Citation coverage expected: 91-93% (target: ≥90%)

2. **20-30% Slower Training:** 35 minutes vs 25 minutes per run
   - **Why Acceptable:** 35 minutes is still very fast for iteration
   - **Impact:** 10 minutes difference is negligible for 3-4 total runs

## Recommended Configuration

```yaml
adapter:
  method: "qlora"

  lora:
    r: 16                    # Rank (balance of capacity and efficiency)
    alpha: 32                # Scaling factor (2 × rank)
    dropout: 0.05
    target_modules: ["q_proj", "k_proj", "v_proj", "o_proj",
                     "gate_proj", "up_proj", "down_proj"]

  quantization:
    load_in_4bit: true
    bnb_4bit_compute_dtype: "bfloat16"
    bnb_4bit_use_double_quant: true
    bnb_4bit_quant_type: "nf4"

training:
  num_train_epochs: 2
  learning_rate: 0.0002
  per_device_train_batch_size: 1
  gradient_accumulation_steps: 16
  optim: "paged_adamw_8bit"
```

## Hardware Recommendation

**Primary:** AWS A10G (24GB) or GCP equivalent
- **Cost:** $0.50-1.00/hour
- **Training Time:** ~35 minutes per run
- **Total Cost:** $4-8 for complete project

**Alternative (Local):** RTX 3090/4090 (24GB)
- **Cost:** $0/hour (if owned)
- **Training Time:** ~40 minutes per run

## Expected Quality Metrics

| Metric | Target | Expected with QLoRA | Status |
|--------|--------|---------------------|---------|
| **JSON Parse Rate** | 100% | 100% | ✅ |
| **Citation Coverage** | ≥90% | 91-93% | ✅ |
| **Refusal Precision** | ≥85% | 87-90% | ✅ |
| **Training Cost** | <$300 | $5-10 | ✅ |
| **Training Time** | <8 hours | 3-4 hours | ✅ |

## Budget Impact

```
Estimated Costs (QLoRA):
├── Pilot run: $0.50
├── Training runs (3×): $1.50
├── Evaluation: $0.75
├── Experimentation: $1.50
└── Storage: $1.00
    ───────────────
    Total: $5.25

Budget Allocation:
├── Total Budget: $500-5,000
├── Used: $5-10
├── Remaining: $490-4,995 (98-99% under budget)
└── Surplus Use: Additional iterations, dataset expansion, multi-model testing
```

## Risk Mitigation

### Primary Risk: Quality Below Target

**Likelihood:** Low (15%)
**Mitigation:**
1. Run pilot evaluation on 10 examples first
2. If quality 85-89%, increase rank to r=32 or add more examples
3. Fallback to LoRA (FP16) on A100 40GB if needed (+$10 cost)

**Contingency Budget:** $20 for additional runs

### Fallback Plan

If QLoRA fails quality targets after 2 runs:
- **Action:** Switch to LoRA (FP16) on A100 40GB
- **Cost:** +$10-15
- **Timeline:** +2 days
- **Still under budget:** $25 total vs $500 budget

## Implementation Timeline

### Week 1: QLoRA Training & Validation

**Days 1-3: Setup & Pilot**
- Day 1: Environment setup, dataset validation
- Day 2: Pilot run (10 examples)
- Day 3: Full training run #1

**Days 4-5: Evaluation & Iteration**
- Day 4: Evaluate metrics, identify issues
- Day 5: Training run #2 (if needed)

### Week 2: Production & Publishing

**Day 1: Final Training**
- Production training with optimal config
- Full monitoring and logging

**Days 2-3: Validation & Release**
- Comprehensive evaluation (40-question golden set)
- Human review (20 samples)
- Publish to Hugging Face: `ainative/kwanzaa-adapter-v1`

## Decision Confidence: 95%

**Why High Confidence:**
- Extensive empirical evidence (QLoRA paper: 99.3% of full precision quality)
- Conservative estimates (likely to exceed expectations)
- Strong budget margin (10x under budget enables experimentation)
- Proven approach (widely adopted in production systems)
- Aligns with open-source values (community can reproduce)

**What Would Change Decision:**
- If Kwanzaa required 99%+ accuracy (then LoRA's 1% advantage would matter)
- If budget was truly constrained at $10 (but it's $500+)
- If training needed <10 minutes (but 35 min is acceptable)

## Next Steps

1. **Today:** Close GitHub issue #32 with decision + link to full document
2. **This Week:** Provision A10G, run pilot training, validate metrics
3. **Next Week:** Production run, publish adapter, document results

## References

**Full Decision Document:** `/Users/aideveloper/kwanzaa/docs/training/fine-tuning-strategy.md`

**Key Supporting Documents:**
- Adapter Objectives: `/Users/aideveloper/kwanzaa/docs/training/adapter-objectives.md`
- Training Config: `/Users/aideveloper/kwanzaa/backend/training/config/training.yaml`
- Model Selection: `/Users/aideveloper/kwanzaa/docs/model-selection-criteria.md`

**Academic References:**
- QLoRA Paper: https://arxiv.org/abs/2305.14314
- LoRA Paper: https://arxiv.org/abs/2106.09685
- Hugging Face PEFT: https://github.com/huggingface/peft

---

**Decision Status:** FINAL
**Approved:** January 16, 2026
**Implementation Start:** January 17, 2026
