# Kwanzaa Training Documentation

**Issue:** #12 - Adapter Compatibility Testing
**Version:** 1.0.0
**Last Updated:** January 16, 2026

---

## Overview

This directory contains documentation for Kwanzaa adapter training, compatibility testing, and deployment validation.

**Core Philosophy:**
- **Zero Tolerance for Hidden Failures** - Document all incompatibilities
- **Evidence-Based Decisions** - Metrics, not opinions
- **Production-First** - Test what matters for real deployments

---

## Documentation Index

### Testing Framework

📋 **[Adapter Compatibility Testing Guide](adapter-compatibility-testing-guide.md)**
- Quick start (5-minute smoke test)
- Full evaluation procedures
- CI/CD integration
- Troubleshooting

🔧 **[Compatibility Report Template](compatibility-report-template.md)**
- Complete report structure
- Example filled report (OLMo → LLaMA)
- Failure analysis templates
- Production recommendations

⚠️ **[Known Issues & Workarounds](adapter-compatibility-known-issues.md)**
- All documented compatibility failures
- Severity classifications
- Proven workarounds
- Long-term fixes

---

## Quick Links

### For Developers

**Testing an adapter on a new base model:**
```bash
# Quick check (5 prompts, 2 minutes)
python evals/adapter_compatibility_checks.py --adapter kwanzaa-v1-olmo --base llama --verbose
python evals/test_adapter_compatibility.py --adapter kwanzaa-v1-olmo --bases llama --quick

# Full test (50 prompts, 10 minutes)
python evals/test_adapter_compatibility.py --adapter kwanzaa-v1-olmo --bases llama --full
```

**Adding a new adapter:**
1. Train adapter: `python train_adapter.py --base MODEL_ID --adapter-name NAME`
2. Add to registry in `test_adapter_compatibility.py`
3. Run compatibility tests on all target bases
4. Document results in compatibility report

### For QA/Product

**Before production deployment:**
1. Review latest compatibility report for your adapter/base combination
2. Check known issues document for blockers
3. Verify all mandatory workarounds are implemented
4. Confirm metrics meet thresholds:
   - Citation accuracy ≥85%
   - JSON compliance ≥95%
   - Refusal rate ≥80%
   - Latency <500ms

### For DevOps

**CI/CD integration:**
```yaml
# Add to your pipeline
- name: Adapter Compatibility Check
  run: |
    python evals/adapter_compatibility_checks.py \
      --adapter $ADAPTER_NAME \
      --base $BASE_MODEL \
      --exit-on-failure
```

---

## Testing Infrastructure

### Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `test_adapter_compatibility.py` | Full compatibility testing | `python test_adapter_compatibility.py --adapter NAME --bases olmo,llama --full` |
| `adapter_compatibility_checks.py` | Pre-flight checks | `python adapter_compatibility_checks.py --adapter NAME --base MODEL` |

### Test Suites

**Quick Test (5 prompts):**
- 1 citation test
- 1 refusal test
- 1 JSON compliance test
- 1 complex historical QA
- 1 multi-source synthesis

**Full Test (50 prompts):**
- 15 citation tests (basic, conflicting, primary-source)
- 10 refusal tests (out-of-scope, ambiguous, partial info)
- 10 JSON compliance tests (escaping, nesting, special chars)
- 15 historical QA (various difficulties and topics)

### Metrics Tracked

**Quality Metrics:**
- Citation Accuracy (% correct attributions)
- JSON Compliance (% valid parseable responses)
- Refusal Rate (% appropriate "I don't know" responses)
- Answer Quality Score (content relevance and completeness)

**Performance Metrics:**
- Load Time (seconds)
- Average Latency (milliseconds)
- Peak Memory (GB)
- Tokens/Second (throughput)

### Output Artifacts

**Generated Files:**
- JSON results: `/evals/results/adapter_compatibility/compatibility_test_TIMESTAMP.json`
- Logs: `/evals/results/adapter_compatibility.log`
- Reports: `docs/training/reports/` (when using template)

---

## Compatibility Matrix

### Current Status (as of 2026-01-16)

| Adapter | OLMo-7B | LLaMA 3.1-8B | DeepSeek-V2 |
|---------|---------|--------------|-------------|
| **kwanzaa-v1-olmo** | ✓ READY | ⚠ CONDITIONAL | ✗ BLOCKED |
| **kwanzaa-v1-llama** | ⚠ CONDITIONAL | ✓ READY | ✗ BLOCKED |
| **kwanzaa-v1-deepseek** | ✗ BLOCKED | ✗ BLOCKED | ✓ READY |

**Legend:**
- ✓ READY = Production-approved, no workarounds needed
- ⚠ CONDITIONAL = Works with mandatory workarounds
- ✗ BLOCKED = Incompatible, do not deploy

### Recommended Configurations

**Production (High Stakes):**
- Use native adapter/base combinations only
- Example: `kwanzaa-v1-olmo` + `OLMo-7B-Instruct`

**Research/Demos (Medium Stakes):**
- Cross-architecture allowed with workarounds
- Example: `kwanzaa-v1-olmo` + `LLaMA 3.1-8B` + Citation Validator

**Internal Tools (Low Stakes):**
- Any combination with WARNING status
- Enhanced monitoring required

---

## Known Issues Summary

### Issue #1: Cross-Architecture Citation Degradation
- **Severity:** HIGH
- **Impact:** 8-17pp drop in citation accuracy
- **Workaround:** Retrain adapter on target base OR add citation validator
- **Affects:** All cross-architecture combinations

### Issue #2: LLaMA Refusal Inconsistency
- **Severity:** MEDIUM
- **Impact:** 13-15pp drop in refusal rate
- **Workaround:** Confidence thresholding OR retrain with LLaMA-specific examples
- **Affects:** OLMo adapter → LLaMA base

### Issue #3: DeepSeek GQA Incompatibility
- **Severity:** CRITICAL
- **Impact:** Complete load failure
- **Workaround:** None (must retrain)
- **Affects:** OLMo/LLaMA adapters → DeepSeek base

### Issue #4: JSON Escaping Differences
- **Severity:** LOW
- **Impact:** 3-5% JSON parse failures
- **Workaround:** Constrained decoding OR post-processing
- **Affects:** Cross-tokenizer scenarios

**Full details:** See [Known Issues Document](adapter-compatibility-known-issues.md)

---

## Decision Tree

```
Need to deploy adapter?
    │
    ├─ Native base? (adapter trained on this base)
    │    └─ YES → Deploy with standard monitoring ✓
    │
    ├─ Different architecture family?
    │    ├─ YES → Run compatibility tests
    │    │         │
    │    │         ├─ Load fails? → BLOCK deployment ✗
    │    │         │
    │    │         ├─ Citation <85%? → Implement workarounds ⚠
    │    │         │
    │    │         └─ All metrics pass? → Deploy with enhanced monitoring ✓
    │    │
    │    └─ NO → Deploy with standard monitoring ✓
    │
    └─ DeepSeek base?
         └─ YES → Check if adapter is DeepSeek-native
                   │
                   ├─ NO → BLOCK (incompatible) ✗
                   └─ YES → Deploy ✓
```

---

## Workflow Examples

### Scenario 1: New Adapter Development

```bash
# Step 1: Train adapter
python train_adapter.py \
  --base ai2/OLMo-7B-Instruct \
  --adapter-name kwanzaa-v2-olmo \
  --data training_data.jsonl

# Step 2: Test on native base
python evals/test_adapter_compatibility.py \
  --adapter kwanzaa-v2-olmo \
  --bases olmo \
  --full

# Step 3: Test cross-architecture (if needed)
python evals/test_adapter_compatibility.py \
  --adapter kwanzaa-v2-olmo \
  --bases llama,deepseek \
  --full

# Step 4: Document results
# - Fill out compatibility report template
# - Update known issues document if new issues found
# - Make deployment recommendation
```

---

### Scenario 2: Pre-Deployment Validation

```bash
# Step 1: Pre-flight check
python evals/adapter_compatibility_checks.py \
  --adapter kwanzaa-v1-olmo \
  --base llama \
  --verbose \
  --exit-on-failure

# Step 2: If pre-flight passes, run full test
python evals/test_adapter_compatibility.py \
  --adapter kwanzaa-v1-olmo \
  --bases llama \
  --full

# Step 3: Review results
cat evals/results/adapter_compatibility/compatibility_test_*.json

# Step 4: Implement workarounds if needed
# - Add citation validator
# - Configure confidence thresholds
# - Set up enhanced monitoring

# Step 5: Shadow mode deployment (1 week)
# - Deploy alongside existing system
# - Compare outputs
# - Monitor metrics

# Step 6: Production rollout
# - Gradual rollout (10% → 50% → 100%)
# - Monitor citation accuracy, refusal rate
# - Rollback if metrics degrade
```

---

### Scenario 3: Troubleshooting Production Issue

```bash
# Step 1: Check current metrics
# - Citation accuracy dropping?
# - JSON parse failures?
# - Refusal rate changing?

# Step 2: Re-run compatibility tests
python evals/test_adapter_compatibility.py \
  --adapter CURRENT_ADAPTER \
  --bases CURRENT_BASE \
  --full

# Step 3: Compare to baseline
# - Load original compatibility test results
# - Calculate deltas
# - Identify regression

# Step 4: Check known issues
# - Review known issues document
# - Look for matching patterns
# - Apply recommended workarounds

# Step 5: If unknown issue
# - Document new issue in known issues doc
# - Create GitHub issue
# - Implement temporary workaround
# - Plan long-term fix
```

---

## Maintenance

### Weekly Tasks

- [ ] Review production metrics for all deployed adapter/base combinations
- [ ] Check for metric degradation vs baseline
- [ ] Update known issues document if new issues discovered

### Per-Release Tasks

- [ ] Test new adapter versions on all target bases
- [ ] Update compatibility matrix
- [ ] Generate compatibility reports
- [ ] Review and update workarounds

### Quarterly Tasks

- [ ] Audit all cross-architecture deployments
- [ ] Evaluate if retraining would improve quality
- [ ] Review test suite coverage
- [ ] Update documentation with lessons learned

---

## Contributing

### Adding New Tests

1. Add test prompts to `get_test_prompts()` in `test_adapter_compatibility.py`
2. Ensure mix of difficulty levels and categories
3. Include expected behaviors
4. Run on all adapters to validate

### Adding New Compatibility Checks

1. Add check method to `AdapterCompatibilityChecker` in `adapter_compatibility_checks.py`
2. Follow naming pattern: `check_FEATURE_NAME()`
3. Return `CompatibilityCheck` object
4. Add to `run_all_checks()` method

### Documenting New Issues

1. Open `docs/training/adapter-compatibility-known-issues.md`
2. Follow template from existing issues (Issues #1-4)
3. Include severity, impact, workarounds
4. Update compatibility matrix if needed

---

## References

### Internal Documentation
- [Model Selection Criteria](../model-selection-criteria.md)
- [Model Comparison Report](../model-comparison.md)
- [Answer JSON Contract](../answer_json_contract.md)

### External Resources
- [HuggingFace PEFT Documentation](https://huggingface.co/docs/peft)
- [LoRA Paper](https://arxiv.org/abs/2106.09685)
- [QLoRA Paper](https://arxiv.org/abs/2305.14314)

### Project Links
- **Issue #12:** Adapter Compatibility Testing
- **GitHub Repo:** github.com/AINative-Studio/kwanzaa
- **Test Framework:** `/Users/aideveloper/kwanzaa/evals/`

---

## Support

**Questions or issues?**
- Review this documentation first
- Check known issues document
- Search GitHub issues
- Ask in #ml-engineering Slack

**Found a bug in test framework?**
- Create GitHub issue with `testing-framework` label
- Include reproduction steps
- Attach test results and logs

**Need help interpreting results?**
- Review compatibility report template examples
- Check troubleshooting section
- Ask senior ML engineer for review

---

**Last Updated:** 2026-01-16
**Maintained By:** AINative Studio ML Engineering Team
**Document Version:** 1.0.0

---

**End of README**
