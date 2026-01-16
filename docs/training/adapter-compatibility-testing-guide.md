# Adapter Compatibility Testing Guide

**Issue:** #12 - Adapter Compatibility Testing
**Version:** 1.0.0
**Last Updated:** January 16, 2026

---

## Quick Start

### 5-Minute Smoke Test

Test an adapter on a new base model with 5 prompts:

```bash
cd /Users/aideveloper/kwanzaa

# Quick compatibility check (pre-flight)
python evals/adapter_compatibility_checks.py \
  --adapter kwanzaa-v1-olmo \
  --base llama \
  --verbose

# If pre-flight passes, run quick test
python evals/test_adapter_compatibility.py \
  --adapter kwanzaa-v1-olmo \
  --bases llama \
  --quick
```

Expected output:
```
================================================================================
ADAPTER COMPATIBILITY CHECK REPORT
================================================================================

Summary: 6/7 checks passed
  Critical Failures: 0
  Warnings: 1

Overall Status: COMPATIBLE (with possible warnings)

[WARNING] architecture_compatibility
  Message: Different architecture families: olmo -> llama
  Remediation: Expect quality degradation. Consider retraining adapter.

================================================================================
COMPATIBILITY MATRIX
================================================================================
Adapter                        │ LLaMA 3.1-8B-Instruct
───────────────────────────────┼──────────────────────
kwanzaa-v1-olmo                │ ⚠ degraded

Legend:
  ✓ = Success (production-ready)
  ⚠ = Degraded (works with issues)
  ✗ = Failure (incompatible)
```

---

## Full Evaluation (Production Pre-Deployment)

Run comprehensive 50-prompt test suite:

```bash
# Full evaluation (takes 5-10 minutes)
python evals/test_adapter_compatibility.py \
  --adapter kwanzaa-v1-olmo \
  --bases llama \
  --full

# Results saved to:
# /Users/aideveloper/kwanzaa/evals/results/adapter_compatibility/
```

---

## Test All Combinations

Test adapter across all supported base models:

```bash
# Test all combinations
python evals/test_adapter_compatibility.py \
  --adapter kwanzaa-v1-olmo \
  --bases olmo,llama,deepseek \
  --full
```

Or test everything:

```bash
# Test all adapters on all bases
python evals/test_adapter_compatibility.py --test-all --full
```

---

## CI/CD Integration

Add to your CI/CD pipeline to block incompatible deployments:

```yaml
# .github/workflows/adapter-compatibility.yml
name: Adapter Compatibility Check

on:
  pull_request:
    paths:
      - 'adapters/**'
      - 'evals/**'

jobs:
  compatibility-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Pre-flight Check
        run: |
          python evals/adapter_compatibility_checks.py \
            --adapter ${{ env.ADAPTER_NAME }} \
            --base ${{ env.BASE_MODEL }} \
            --exit-on-failure

      - name: Full Compatibility Test
        if: success()
        run: |
          python evals/test_adapter_compatibility.py \
            --adapter ${{ env.ADAPTER_NAME }} \
            --bases ${{ env.BASE_MODEL }} \
            --full

      - name: Upload Results
        uses: actions/upload-artifact@v3
        with:
          name: compatibility-results
          path: evals/results/adapter_compatibility/
```

---

## Understanding Test Results

### Compatibility Status

| Status | Meaning | Action |
|--------|---------|--------|
| **SUCCESS** | All metrics meet thresholds | Deploy to production |
| **DEGRADED** | Works but below targets | Deploy with workarounds |
| **LOAD_FAILURE** | Adapter won't load | Retrain or block deployment |
| **INFERENCE_FAILURE** | Loads but inference fails | Block deployment |

### Key Metrics

**Citation Accuracy** (Target: ≥85%)
- Percentage of citations that match provided sources
- Critical for educational/reference use cases
- Below 85% = NOT RECOMMENDED for production

**JSON Compliance** (Target: ≥95%)
- Percentage of responses with valid JSON
- Critical for UI rendering
- Below 95% = Risk of frontend crashes

**Refusal Rate** (Target: ≥80%)
- Percentage of appropriate "I don't know" responses
- Critical for trustworthiness
- Below 80% = Risk of hallucination

**Latency** (Target: <500ms)
- Average response time
- Important for UX
- Above 500ms = Poor user experience

---

## Reading Compatibility Reports

### Example Report Structure

```markdown
## Test 2: LLaMA 3.1-8B-Instruct (Alternative Base)

**Status:** ⚠ DEGRADED (Usable with Limitations)

#### Inference Quality
| Metric | Value | Threshold | Pass |
|--------|-------|-----------|------|
| **Citation Accuracy** | 78% | ≥85% | ✗ |
| **JSON Compliance** | 95% | ≥95% | ✓ |
| **Refusal Rate** | 72% | ≥80% | ✗ |

**Failure Categories:**
- `quality_degradation` - Citation accuracy below threshold

**Recommended Workarounds:**
1. Retrain adapter on LLaMA base (2-4 hours, 95%+ effectiveness)
2. Add post-processing citation validator (1 day, 70-80% effectiveness)

**Production Recommendation:** **CONDITIONAL APPROVAL**
- Acceptable for research demos and low-stakes queries
- NOT recommended for educational content or historical reference
```

### Interpreting Results

**All Metrics Pass (✓):**
- Deploy to production with standard monitoring
- No special workarounds needed

**Some Metrics Fail (✗):**
- Review **Recommended Workarounds** section
- Implement mandatory workarounds before deployment
- Set up enhanced monitoring

**Load/Inference Failure:**
- **DO NOT DEPLOY**
- Retrain adapter on target base model
- Or choose different base model

---

## Failure Categories Explained

### DIMENSION_MISMATCH
**What it means:** Hidden size incompatibility (e.g., 4096 vs 5120)
**Impact:** Adapter will not load
**Fix:** Retrain adapter on target base

### ARCHITECTURE_INCOMPATIBILITY
**What it means:** Different layer structures (e.g., MHA vs GQA)
**Impact:** May not load, or severe quality degradation
**Fix:** Retrain adapter on target base

### TOKENIZER_MISMATCH
**What it means:** Different vocabularies or special tokens
**Impact:** JSON escaping issues, minor quality loss
**Fix:** Add post-processing or use constrained decoding

### QUALITY_DEGRADATION
**What it means:** Citation accuracy or refusal rate below threshold
**Impact:** Works but not production-ready
**Fix:** Retrain or implement workarounds

### JSON_COMPLIANCE_FAILURE
**What it means:** Invalid JSON in >5% of responses
**Impact:** Frontend parsing errors
**Fix:** Constrained decoding or post-processing

---

## Workaround Decision Tree

```
┌─────────────────────────────────────────────┐
│ Compatibility test failed                   │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
         ┌────────────────────┐
         │ Load failure?      │
         └────────┬───────────┘
                  │
        ┌─────────┴─────────┐
        │ YES               │ NO
        ▼                   ▼
┌───────────────┐   ┌──────────────────┐
│ BLOCK         │   │ Inference        │
│ DEPLOYMENT    │   │ failure?         │
│               │   └────────┬─────────┘
│ Action:       │            │
│ - Retrain or  │   ┌────────┴────────┐
│ - Switch base │   │ YES             │ NO
└───────────────┘   ▼                 ▼
            ┌───────────────┐  ┌─────────────────┐
            │ BLOCK         │  │ Quality         │
            │ DEPLOYMENT    │  │ degradation?    │
            │               │  └────────┬────────┘
            │ Action:       │           │
            │ - Debug or    │  ┌────────┴────────┐
            │ - Retrain     │  │ YES             │ NO
            └───────────────┘  ▼                 ▼
                    ┌──────────────────┐  ┌──────────────┐
                    │ Critical metrics │  │ DEPLOY       │
                    │ failed?          │  │              │
                    └────────┬─────────┘  │ Action:      │
                             │            │ - Standard   │
                    ┌────────┴────────┐   │   monitoring │
                    │ YES             │NO └──────────────┘
                    ▼                 ▼
            ┌──────────────┐  ┌──────────────────┐
            │ CONDITIONAL  │  │ DEPLOY           │
            │ APPROVAL     │  │ with monitoring  │
            │              │  │                  │
            │ Action:      │  │ Action:          │
            │ - Mandatory  │  │ - Monitor        │
            │   workaround │  │   closely        │
            │ - Enhanced   │  │ - Review weekly  │
            │   monitoring │  └──────────────────┘
            └──────────────┘
```

---

## Common Scenarios

### Scenario 1: Testing New Adapter on Native Base

**Example:** Test `kwanzaa-v1-olmo` on `OLMo-7B-Instruct` (same base it was trained on)

**Expected:** All checks pass, metrics at or above baseline

```bash
python evals/test_adapter_compatibility.py \
  --adapter kwanzaa-v1-olmo \
  --bases olmo \
  --full
```

**If it fails:** Something is wrong with adapter training or test setup. Debug before proceeding.

---

### Scenario 2: Cross-Architecture Testing

**Example:** Test `kwanzaa-v1-olmo` on `LLaMA 3.1-8B` (different architecture)

**Expected:** Load succeeds, but 10-20% quality degradation

```bash
# Pre-flight check first
python evals/adapter_compatibility_checks.py \
  --adapter kwanzaa-v1-olmo \
  --base llama

# If warnings only, proceed with full test
python evals/test_adapter_compatibility.py \
  --adapter kwanzaa-v1-olmo \
  --bases llama \
  --full
```

**If degradation >20%:** Consider retraining adapter on LLaMA base.

---

### Scenario 3: Completely Incompatible Base

**Example:** Test `kwanzaa-v1-olmo` on `DeepSeek-V2` (incompatible architecture)

**Expected:** Pre-flight fails with CRITICAL errors

```bash
python evals/adapter_compatibility_checks.py \
  --adapter kwanzaa-v1-olmo \
  --base deepseek \
  --exit-on-failure
```

Expected output:
```
[CRITICAL] dimension_mismatch
  Message: Hidden dimension mismatch: 4096 != 5120
  Remediation: INCOMPATIBLE - adapter will fail to load. Must retrain.

[CRITICAL] target_modules
  Message: Target module mismatch
  Remediation: Adapter may fail to load or produce errors.

Overall Status: INCOMPATIBLE (critical failures detected)
```

**Action:** Do not proceed. Retrain on DeepSeek base if required.

---

## Best Practices

### Before Training New Adapter

1. **Choose Target Base Model(s):** Decide upfront which base models you need to support
2. **Train Per-Base Adapters:** Train separate adapter for each base model family
3. **Use Consistent Naming:** `kwanzaa-v1-{base}` (e.g., `kwanzaa-v1-olmo`, `kwanzaa-v1-llama`)

### After Training

1. **Test Native Base First:** Verify adapter works on its training base
2. **Run Pre-Flight Checks:** Quick compatibility check before full evaluation
3. **Document Results:** Save results and update known issues document

### Before Production Deployment

1. **Full 50-Prompt Test:** Run comprehensive evaluation
2. **Review Known Issues:** Check `/docs/training/adapter-compatibility-known-issues.md`
3. **Implement Workarounds:** Add any mandatory workarounds from report
4. **Shadow Mode:** Run 1 week in shadow mode comparing to baseline
5. **Monitor:** Set up dashboards and alerts for key metrics

---

## Troubleshooting

### "Unknown adapter" error

**Problem:** Adapter config not found

**Solution:** Add adapter to `available_adapters` dict in `test_adapter_compatibility.py`:

```python
available_adapters = {
    "kwanzaa-v1-olmo": AdapterConfig(
        name="kwanzaa-v1-olmo",
        path="/path/to/adapter",
        base_model_id=BaseModel.OLMO_7B.value,
        adapter_type="lora",
        rank=16,
        alpha=32,
        target_modules=["q_proj", "v_proj", "k_proj", "o_proj"],
    ),
}
```

---

### "Placeholder model response" in results

**Problem:** Test framework is using mock inference (not actual model)

**Solution:** This is expected in the initial implementation. To use real models:

1. Implement actual model loading in `load_adapter_and_base()`
2. Implement real inference in `run_inference()`
3. Add transformers + peft dependencies

Example implementation:

```python
def load_adapter_and_base(self, adapter_config, base_model_id):
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import PeftModel

    # Load base model
    model = AutoModelForCausalLM.from_pretrained(
        base_model_id,
        device_map=self.device,
    )

    # Load adapter
    model = PeftModel.from_pretrained(
        model,
        adapter_config.path,
    )

    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(base_model_id)

    return True, (model, tokenizer), None
```

---

### Results show 100% success but you expect failures

**Problem:** Mock implementation doesn't catch real compatibility issues

**Solution:** Implement actual model loading and inference (see above)

---

### Test hangs or takes too long

**Problem:** Model loading or inference is slow

**Solutions:**
1. Use `--quick` flag for 5-prompt smoke test
2. Use quantization (4-bit) for faster loading
3. Reduce batch size or max tokens
4. Use smaller models for testing

---

## File Locations

### Test Framework
- **Main Test Script:** `/Users/aideveloper/kwanzaa/evals/test_adapter_compatibility.py`
- **Pre-flight Checks:** `/Users/aideveloper/kwanzaa/evals/adapter_compatibility_checks.py`

### Documentation
- **This Guide:** `/Users/aideveloper/kwanzaa/docs/training/adapter-compatibility-testing-guide.md`
- **Known Issues:** `/Users/aideveloper/kwanzaa/docs/training/adapter-compatibility-known-issues.md`
- **Report Template:** `/Users/aideveloper/kwanzaa/docs/training/compatibility-report-template.md`

### Results
- **Test Results:** `/Users/aideveloper/kwanzaa/evals/results/adapter_compatibility/`
- **Log Files:** `/Users/aideveloper/kwanzaa/evals/results/adapter_compatibility.log`

---

## Next Steps

### After Completing Compatibility Testing

1. **Document Results:**
   - Fill out compatibility report template
   - Update known issues document
   - Share with team

2. **Make Deployment Decision:**
   - Review compatibility matrix
   - Check recommendations
   - Implement required workarounds

3. **Set Up Monitoring:**
   - Track citation accuracy
   - Monitor JSON parse failures
   - Alert on quality degradation

4. **Plan Retraining (if needed):**
   - If quality <85%, schedule adapter retraining
   - Use same data, different base model
   - Re-run compatibility tests

---

## Getting Help

**Found a new compatibility issue?**
1. Document it in `/docs/training/adapter-compatibility-known-issues.md`
2. Follow the issue template from existing issues
3. Create GitHub issue with label `adapter-compatibility`

**Questions about results?**
- Review the Known Issues document
- Check the Report Template for examples
- Ask in #ml-engineering Slack channel

**Contributing improvements?**
- Submit PR with test updates
- Update this guide with new scenarios
- Share learnings with the team

---

**End of Guide**
