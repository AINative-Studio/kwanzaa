# Issue #77 Quick Reference

**Validate AINative Adapter Quality**

---

## 3-Step Validation Process

### Step 1: Push to Hub (2 min)
Visit: https://huggingface.co/spaces/ainativestudio/kwanzaa-training
→ Click "📤 Push to Hub"

### Step 2: Download (1 min)
```bash
python scripts/download_ainative_adapter.py
```

### Step 3: Validate (5-10 min)
```bash
python scripts/validate_ainative_adapter.py
```

---

## Success Criteria

- ✅ Overall Score ≥ 70%
- ✅ Zero AI Attribution: PASSED
- ✅ All 5 categories ≥ 60%

---

## Test Categories (10 tests)

1. **Agent Swarm** (2) - Parallel execution, orchestration
2. **AIkit SDK** (2) - React SDK, Next.js hooks
3. **ZeroDB** (2) - Vector storage, semantic search
4. **TDD/BDD** (2) - Pytest tests, BDD structure
5. **OpenAPI** (2) - POST endpoints, validation schemas

---

## After Validation

### If PASS (≥70%)
1. Fill out: `docs/training/ainative-validation-results-template.md`
2. Complete: `docs/training/issue-77-completion-checklist.md`
3. Post: `docs/training/issue-77-closure-comment-draft.md` to GitHub
4. Close Issue #77
5. Start Issue #78 (Integration)

### If FAIL (<70%)
1. Analyze failed categories
2. Enhance training data
3. Re-train adapter
4. Re-validate
5. Document improvements

---

## Key Files

**Scripts**:
- `/Users/aideveloper/kwanzaa/scripts/download_ainative_adapter.py`
- `/Users/aideveloper/kwanzaa/scripts/validate_ainative_adapter.py`

**Results**:
- `/Users/aideveloper/kwanzaa/outputs/ainative_adapter_validation.json`
- `/Users/aideveloper/kwanzaa/outputs/adapters/ainative-v1/`

**Documentation**:
- `docs/training/ainative-validation-results-template.md` - Fill this
- `docs/training/issue-77-completion-checklist.md` - Check this
- `docs/training/issue-77-closure-comment-draft.md` - Post this

**Guides**:
- `VALIDATION_WORKFLOW.md` - Simple workflow
- `AINATIVE_VALIDATION_READY.md` - Detailed guide

---

## Quick Commands

```bash
# Download adapter
python scripts/download_ainative_adapter.py

# Run validation
python scripts/validate_ainative_adapter.py

# View results
cat outputs/ainative_adapter_validation.json | python -m json.tool

# Check adapter files
ls -lh outputs/adapters/ainative-v1/
```

---

## Timeline

- Push to Hub: 2 min
- Download: 1 min
- Validation: 5-10 min
- Documentation: 15-20 min
- **Total: ~25-35 minutes**

---

## Issue #78 Preview

**Integrate AINative Adapter into Backend API**

Tasks:
1. Add to model registry
2. Create adapter service
3. Add API endpoints
4. Integration tests
5. Deploy to staging

---

**Status**: Ready to validate
**Date**: 2026-01-25
