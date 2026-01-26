# AINative Adapter - Validation Workflow

## ✅ READY TO PROCEED

All infrastructure is in place. Follow these 3 simple steps:

---

## Step 1: Push Adapter to HuggingFace Hub

**Action**: Visit https://huggingface.co/spaces/ainativestudio/kwanzaa-training

**What to do**:
1. You'll see a new "📤 After Training" section
2. Click the blue "📤 Push to Hub" button
3. Wait ~1-2 minutes for upload
4. You'll see: "✅ SUCCESS! Adapter available at: https://huggingface.co/ainativestudio/ainative-adapter-v1"

**Note**: If the "Push to Hub" button doesn't appear, refresh the page and wait 1-2 minutes for the Space to rebuild.

---

## Step 2: Download Adapter Locally

```bash
python scripts/download_ainative_adapter.py
```

**Expected**: Adapter files downloaded to `outputs/adapters/ainative-v1/`

---

## Step 3: Run Validation

```bash
python scripts/validate_ainative_adapter.py
```

**Tests** (10 total):
- Agent Swarm (2): Parallel execution, orchestration patterns
- AIkit SDK (2): React SDK, Next.js hooks
- ZeroDB (2): Vector storage, semantic search
- TDD/BDD (2): Pytest tests, BDD structure
- OpenAPI (2): POST endpoints, validation schemas

**Success Criteria**:
- Overall Score ≥ 70%
- Zero AI Attribution: PASSED
- All categories ≥ 60%

**Results**: Saved to `outputs/ainative_adapter_validation.json`

---

## Quick Reference

**Documentation**:
- `AINATIVE_VALIDATION_READY.md` - This guide with full details
- `docs/training/AINATIVE_NEXT_STEPS.md` - Complete instructions
- `docs/training/ainative-adapter-retrieval.md` - Retrieval guide

**Scripts**:
- `scripts/download_ainative_adapter.py`
- `scripts/validate_ainative_adapter.py`
- `scripts/push_adapter_to_hub.py`

**HuggingFace**:
- Space: https://huggingface.co/spaces/ainativestudio/kwanzaa-training
- Dataset: https://huggingface.co/datasets/ainativestudio/ainative-training-v1
- Adapter (after Step 1): https://huggingface.co/ainativestudio/ainative-adapter-v1

---

## Timeline

- Step 1: 2 minutes
- Step 2: 1 minute
- Step 3: 5-10 minutes
- **Total: ~8-13 minutes**

---

## After Validation

Once validation passes → **Issue #78**: Integrate adapter into backend API

**Ready to start!** 🚀
