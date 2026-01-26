# AINative Adapter - Corrective Action Plan

**Date**: 2026-01-25
**Status**: Validation FAILED (47%), Training Data INVALID
**Goal**: Achieve ≥70% validation score with high-quality dataset

---

## Summary of Failure

### What Happened
1. ✅ Trained adapter with 88 examples (92% format validation)
2. ✅ Pushed to HuggingFace Hub successfully
3. ❌ Validation failed: 47% overall score (threshold: 70%)
4. ❌ Root cause: Training data contains placeholder responses and TODOs

### Key Findings

**Data Quality Issues**:
- 45% of responses are "# TODO: Add full implementation"
- 34% of responses just echo the question
- 0 examples with REST API endpoint patterns
- 0 examples with SDK initialization code
- 0 examples with React hook usage

**Validation Results**:
- ZeroDB: 0% (hallucinated fictional APIs)
- Agent Swarm: 45% (invented physics simulation)
- AIkit SDK: 40% (fictional package names)
- TDD/BDD: 70% ✅ (generic patterns worked)
- OpenAPI: 80% ✅ (generic patterns worked)

---

## Root Cause Analysis

### Primary Issue: Data Quality

The training dataset (`ainative_train.jsonl`) contains:
- Task-oriented prompts ("Implement X") instead of Q&A ("How do I...?")
- Placeholder responses instead of complete working code
- No specific AINative patterns (API endpoints, package names, hooks)

### Secondary Issue: Insufficient Data

- Only 88 training examples for 5 distinct technical domains
- Approximately 17 examples per category
- Not enough repetition for the 1B model to learn new patterns

### Tertiary Issue: Base Model Size

- Llama-3.2-1B (1 billion parameters) has limited capacity
- Struggled to learn domain-specific knowledge
- Fell back to hallucinating similar-sounding patterns

---

## Corrective Actions

### Phase 1: Data Improvement (Priority 1 - CRITICAL)

#### Goal
Create high-quality dataset with 500-1000 complete, working examples

#### Approach
**Option A: Manual Curation with Templates** (RECOMMENDED)
- Create 10 perfect examples per category (50 total)
- Use as templates for expansion to 500-1000
- Ensure every example includes working code
- Test each code snippet before including

**Timeline**: 5-7 days
**Success Probability**: 80%+

**Option B: Extract from Documentation**
- Scrape https://api.ainative.studio/v1/openapi.json
- Extract examples from AIkit SDK repositories
- Convert to Q&A format
- Augment with variations

**Timeline**: 3-5 days
**Success Probability**: 70%+ (depends on doc quality)

**Recommended**: Hybrid approach - manual templates + documentation extraction

---

#### Data Quality Standards

Every training example MUST include:

**Format**:
```json
{
  "messages": [
    {
      "role": "system",
      "content": "[Concise system prompt defining AINative expert role]"
    },
    {
      "role": "user",
      "content": "How do I [specific technical question]?"
    },
    {
      "role": "assistant",
      "content": "To [answer], follow these steps:\n\n1. [Step with code]\n```python\n[Complete working code]\n```\n\n2. [Explanation]\n\n[Additional details, related patterns, gotchas]"
    }
  ],
  "metadata": {
    "category": "[category]",
    "patterns": ["[key_pattern_1]", "[key_pattern_2]"],
    "tested": true
  }
}
```

**Content Requirements**:
- ✅ Complete, working code (not TODO)
- ✅ Import statements included
- ✅ Actual package names (@ainative/react, not fictional)
- ✅ Real API endpoints (POST /api/v1/vectors, not invented)
- ✅ Error handling shown
- ✅ Example usage demonstrated
- ❌ No placeholder text
- ❌ No "TODO" comments
- ❌ No echoing question

---

#### Pattern Coverage Requirements

**Agent Swarm** (≥100 examples):
- ✅ POST /api/v1/swarms (parallel execution)
- ✅ POST /api/v1/swarms (sequential execution)
- ✅ GET /api/v1/swarms/{id}/status
- ✅ Agent configuration patterns
- ✅ Error handling (timeouts, failures)

**AIkit SDK** (≥100 examples):
- ✅ React: AINativeProvider initialization
- ✅ React: useAgentSwarm hook
- ✅ React: useVectorSearch hook
- ✅ Next.js: Server-side usage
- ✅ Vue/Svelte: SDK integration

**ZeroDB** (≥100 examples):
- ✅ POST /api/v1/vectors/upsert (store embeddings)
- ✅ POST /api/v1/vectors/search (semantic search)
- ✅ GET /api/v1/vectors/{id}
- ✅ DELETE /api/v1/vectors/{id}
- ✅ Embedding generation (1536 dimensions)

**TDD/BDD** (≥100 examples):
- ✅ Pytest test structure (class-based)
- ✅ BDD naming (test_when_should)
- ✅ Fixtures and mocks
- ✅ Async test patterns
- ✅ FastAPI test client usage

**OpenAPI** (≥100 examples):
- ✅ Endpoint definitions (paths)
- ✅ Request body schemas
- ✅ Response schemas
- ✅ Validation rules
- ✅ Authentication requirements

---

### Phase 2: Validation Improvement (Priority 2)

#### Enhanced Validation Script

Update validation to check:
- ❌ Presence of TODO comments in responses
- ❌ Placeholder text detection
- ✅ Code block presence (```python, ```javascript)
- ✅ Import statement presence
- ✅ Specific pattern keywords (POST, endpoint, import, etc.)
- ✅ Response length (minimum 200 characters for code examples)

#### Validation Metrics

Add semantic checks:
- Code syntax validation (ast.parse for Python, eslint for JS)
- Pattern matching for required keywords
- Similarity scoring against reference answers
- Hallucination detection (check if mentioned packages exist)

---

### Phase 3: Training Configuration Optimization (Priority 3)

#### Increase Epochs

**Current**: 4 epochs
**Proposed**: 10-15 epochs

**Rationale**: With quality data, more epochs will improve learning

#### Add Validation Monitoring

- Track validation loss during training
- Implement early stopping (patience=3 epochs)
- Save best checkpoint based on validation performance

#### Consider Larger Base Model

**If 1B model continues to struggle**:
- Switch to Llama-3.2-3B (3 billion parameters)
- Or Llama-3.1-7B (7 billion parameters)

**Trade-offs**:
- Larger model = better capacity for new knowledge
- Longer training time (3-7x)
- Higher memory requirements (6-14GB VRAM)

---

## Implementation Timeline

### Week 1: Data Creation (Days 1-7)

**Day 1-2**: Manual template creation
- Create 10 perfect examples per category (50 total)
- Test all code examples
- Document pattern structure

**Day 3-4**: Documentation extraction
- Scrape OpenAPI spec
- Extract SDK examples from GitHub
- Convert to Q&A format

**Day 5-6**: Data expansion
- Use templates to create variations
- Expand to 500 examples
- Ensure pattern coverage

**Day 7**: Quality validation
- Run enhanced validation script
- Manual review of random sample (50 examples)
- Fix any quality issues

---

### Week 2: Training and Validation (Days 8-14)

**Day 8**: Training preparation
- Upload new dataset to HuggingFace
- Update training configuration (15 epochs, validation monitoring)
- Prepare training environment

**Day 9-10**: Training execution
- Train adapter with new dataset
- Monitor validation loss
- Save best checkpoint

**Day 11**: Validation testing
- Download trained adapter
- Run comprehensive validation suite
- Analyze results

**Day 12-13**: Iteration (if needed)
- If validation < 70%: Analyze failures
- Add more targeted examples
- Retrain if necessary

**Day 14**: Deployment preparation
- If validation ≥70%: Prepare for integration
- Update documentation
- Close Issue #77

---

## Success Criteria

### Minimum Thresholds

| Metric | Target |
|--------|--------|
| Overall Score | ≥ 70% |
| Agent Swarm | ≥ 70% |
| AIkit SDK | ≥ 70% |
| ZeroDB | ≥ 70% |
| TDD/BDD | ≥ 70% |
| OpenAPI | ≥ 70% |
| Zero AI Attribution | PASS |
| Zero Inappropriate Refusals | PASS |

### Quality Indicators

- ✅ All REST API endpoints mentioned correctly
- ✅ All package names spelled correctly
- ✅ No hallucinated classes or methods
- ✅ No "I can't help with that" refusals for legitimate questions
- ✅ Code examples are syntactically valid
- ✅ Responses include working imports

---

## Risk Mitigation

### Risk 1: Data Creation Takes Longer Than Expected

**Mitigation**:
- Start with smaller high-quality dataset (200 examples)
- Test with smaller dataset first
- Expand based on results

### Risk 2: 1B Model Insufficient Even With Good Data

**Mitigation**:
- Prepare Llama-3.2-3B training configuration in parallel
- If 1B fails twice, switch to 3B immediately
- Budget extra 2-3 days for larger model training

### Risk 3: Validation Still Fails After Retraining

**Mitigation**:
- Analyze specific failure patterns
- Add targeted examples for failures
- Consider few-shot prompting approach (include examples in system prompt)

---

## Resource Requirements

### Human Effort

- Data creation: 30-40 hours
- Training monitoring: 5-10 hours
- Validation and iteration: 10-15 hours
- Total: 45-65 hours (~1.5-2 weeks full-time equivalent)

### Compute Resources

**Training (1B model)**:
- ZeroGPU A100: 2-3 hours
- Cost: ~$0-5 (free tier or low-cost space)

**Training (3B model, if needed)**:
- A100 40GB: 6-9 hours
- Cost: ~$10-20

**Validation**:
- Local CPU (Apple Silicon): 30-45 minutes
- No additional cost

---

## Deliverables

### Phase 1 (Data Improvement)
1. ✅ New training dataset (500-1000 examples)
2. ✅ Enhanced validation script (semantic checks)
3. ✅ Data quality report (showing improvements)
4. ✅ Pattern coverage matrix (verifying all patterns covered)

### Phase 2 (Training)
1. ✅ Trained adapter (new version)
2. ✅ Training logs (showing validation improvement)
3. ✅ Best checkpoint saved

### Phase 3 (Validation)
1. ✅ Validation results (≥70% overall)
2. ✅ Per-category breakdown
3. ✅ Sample responses showing correct patterns
4. ✅ Comparison report (old vs new adapter)

### Phase 4 (Documentation)
1. ✅ Updated training documentation
2. ✅ Integration guide for backend
3. ✅ GitHub Issue #77 closure comment
4. ✅ GitHub Issue #78 kickoff (backend integration)

---

## Immediate Next Steps (Today)

### 1. Check if Better Data Extraction Already Ran

There's a background process running:
```bash
python3 scripts/extract_ainative_training_data.py \
  --core-path /Users/aideveloper/core \
  --output data/training/ainative_train_extracted.jsonl
```

**Action**: Check if this produced better quality data

### 2. Review OpenAPI Spec

**Action**: Download and review official API specification
```bash
curl https://api.ainative.studio/v1/openapi.json -o data/ainative_openapi_spec.json
```

### 3. Create First 10 Perfect Examples

**Categories**:
- 2 ZeroDB examples (vector upsert, semantic search)
- 2 Agent Swarm examples (parallel, sequential)
- 2 AIkit SDK examples (provider, hook)
- 2 TDD examples (pytest class, fixtures)
- 2 OpenAPI examples (POST endpoint, validation)

### 4. Update Issue #77

**Title**: "Validate AINative Adapter Quality"
**Status**: Update with failure analysis

**Comment**:
```markdown
## Validation Results: FAILED (47%)

The adapter validation failed with a 47% overall score (threshold: 70%).

### Scores by Category
- ZeroDB: 0% ❌ (hallucinated fictional APIs)
- Agent Swarm: 45% ❌ (wrong paradigm)
- AIkit SDK: 40% ❌ (fictional packages, refusals)
- TDD/BDD: 70% ✅
- OpenAPI: 80% ✅

### Root Cause
Training data contains placeholder responses ("TODO: Add full implementation") instead of actual working code. The dataset has:
- 0 REST API endpoint examples
- 0 SDK initialization patterns
- 0 React hook examples

**See**: TRAINING_DATA_QUALITY_REPORT.md, AINATIVE_VALIDATION_FAILURE_ANALYSIS.md

### Corrective Action
Creating new high-quality dataset with 500-1000 complete, working examples. ETA: 1-2 weeks

**See**: CORRECTIVE_ACTION_PLAN.md
```

---

## Long-term Improvements

### 1. Continuous Data Collection

- Collect real user queries from AINative platform
- Extract common patterns and questions
- Expand training dataset over time

### 2. Multi-stage Training

- Stage 1: General AINative knowledge (current goal)
- Stage 2: Platform-specific optimizations
- Stage 3: User preference learning (RLHF)

### 3. Automated Quality Assurance

- CI/CD pipeline for dataset validation
- Automated semantic checks before training
- Pre-training quality gates

---

## Decision Points

### Decision 1: Proceed with 1B or Switch to 3B Now?

**Recommendation**: Start with 1B + quality data
- Faster iteration
- If still fails → Switch to 3B
- Data quality likely more important than model size

**Decision**: Proceed with Llama-3.2-1B + improved data

### Decision 2: Manual vs Automated Data Creation?

**Recommendation**: Hybrid approach
- Manual: 50 perfect template examples
- Automated: Expand templates with variations
- Extraction: Pull from OpenAPI spec and SDK docs

**Decision**: Use hybrid approach for best quality + speed

### Decision 3: Immediate Retraining or Wait for Full Dataset?

**Recommendation**: Wait for 500+ quality examples
- Avoid another failure
- Better to take 1-2 weeks and get it right
- Can test with smaller dataset (200) first if needed

**Decision**: Wait for substantial dataset improvement

---

## Conclusion

The adapter validation failure is entirely due to **training data quality issues**, not model capacity or training configuration. The corrective action is clear:

1. **Create high-quality dataset** (500-1000 examples with working code)
2. **Enhance validation** (semantic checks for quality)
3. **Retrain with improved data** (same 1B model initially)
4. **Validate thoroughly** (≥70% threshold)

**Timeline**: 1-2 weeks
**Success Probability**: 80%+ with quality data
**Next Milestone**: 50 perfect template examples created

---

**Status**: Plan approved, execution begins immediately
**Owner**: Development team
**Review Date**: After Phase 1 completion (Day 7)
