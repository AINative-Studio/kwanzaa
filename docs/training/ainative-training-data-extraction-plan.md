# AINative Coding Assistant - Training Data Extraction Plan

## Executive Summary

This plan outlines the comprehensive strategy for extracting high-quality training data from the AINative platform codebase to create a specialized coding assistant adapter for Llama-3.2-1B-Instruct. The goal is to train the model to generate AINative platform-specific code following project standards, API patterns, and TDD/BDD practices.

**Target**: 320-380 training examples across 8 categories
**Estimated Effort**: 3-4 weeks
**Training Cost**: ~$8-15 (40-60 minutes on A10G GPU)
**Expected ROI**: 40-60% faster boilerplate generation, 80%+ test coverage compliance

---

## 1. Codebase Analysis Summary

### 1.1 Platform Architecture

**Core Technologies**:
- **Backend**: FastAPI + SQLAlchemy + PostgreSQL (via PgBouncer port 6432)
- **Frontend SDKs**: React, Vue, Svelte, Next.js hooks
- **Database**: ZeroDB (vector storage, NoSQL tables, file storage, events)
- **MCP Servers**: Model Context Protocol integrations (Strapi, ZeroDB)
- **Infrastructure**: Railway deployment, Kong API Gateway
- **Testing**: pytest with TDD/BDD patterns, 80%+ coverage requirement

**Key Services**:
- ZeroDB: Vector embeddings (384/768/1024/1536 dimensions), semantic search, quantum operations
- Agent Swarm: Multi-agent orchestration, task coordination
- Memory Service: Agent memory with semantic search
- RAG Service: Retrieval-augmented generation workflows
- Managed Chat: LLM chat completions with streaming

### 1.2 Critical Standards (Zero Tolerance)

From `.ainative/` and `.claude/`:

1. **No AI Attribution**: NEVER include "Claude", "Anthropic", "AI-generated", or tool attribution
2. **File Placement**:
   - Documentation → `docs/{category}/`
   - Scripts → `scripts/`
   - Root .md allowed: Only `README.md`, `CLAUDE.md`
3. **Issue Tracking**: Every PR links to issue, branches: `[type]/[issue-number]-[slug]`
4. **TDD Required**: Tests pass before commits, coverage >= 80%
5. **Security**: No secrets/PII in logs, validate inputs, no credentials in code
6. **Database**: Use PgBouncer port 6432, check connection pool before queries

---

## 2. Data Sources Identified

### 2.0 Primary API Reference: OpenAPI Specification

**Location**: https://api.ainative.studio/v1/openapi.json

**Critical Importance**: This is the **authoritative source** for all AINative API endpoints, schemas, and specifications.

**Extraction Strategy**:
- Download and parse OpenAPI spec programmatically
- Extract all endpoint definitions with request/response models
- Generate training examples for each API operation
- Include authentication patterns, error responses, validation rules
- Cross-reference with actual implementation in codebase

**Expected Examples**: 40-50 (covering all major API operations)

**NPM Packages**: https://www.npmjs.com/~ainative-studio
**PyPI Packages**: https://pypi.org/user/ainative/

These published packages represent production-ready code patterns that should be included in training data extraction.

### 2.1 Backend API Patterns

**Location**: `/Users/aideveloper/core/src/backend/app/`

**Key Patterns to Extract**:
- FastAPI router setup with dependency injection (src/backend/app/zerodb/api/embeddings.py)
- Pydantic request/response models
- Async endpoint handlers with error handling
- ZeroDB service integration patterns
- Authentication with `get_current_user_flexible`
- Database session management with `get_db`

**Example Files**:
- `app/zerodb/api/embeddings.py` - Embedding generation and storage
- `app/zerodb/api/database.py` - NoSQL table operations
- `app/zerodb/api/file_storage.py` - File upload/download
- `app/api/*.py` - Public API endpoints

### 2.2 TDD/BDD Test Patterns

**Location**: `/Users/aideveloper/core/src/backend/tests/`

**Test Patterns**:
- pytest with `@pytest.mark.asyncio` for async tests
- Mock patterns with `unittest.mock.patch`, `AsyncMock`
- Test class organization: `class TestFeatureName`
- BDD-style test names: `test_should_do_something_when_condition()`
- Fixture usage for setup/teardown
- Coverage assertions

**Example Files**:
- `tests/test_zerodb_caching.py` - Caching integration tests
- `tests/paipalooza/test_api_*.py` - API endpoint tests
- `tests/middleware/test_api_usage_middleware.py` - Middleware tests

### 2.3 AIkit SDK & Platform SDKs (CRITICAL)

**Primary Focus**: AIkit SDK - the core platform SDK
**Secondary**: Framework-specific SDKs (React, Vue, Svelte, Next.js)

**AIkit SDK Location**: `/Users/aideveloper/core/packages/sdks/aikit/` (if exists) or check NPM @ainative-studio/aikit

**Platform SDK Locations**:
- React: `/Users/aideveloper/core/packages/sdks/react/src/`
- Vue: `/Users/aideveloper/core/packages/sdks/vue/src/`
- Svelte: `/Users/aideveloper/core/packages/sdks/svelte/src/`
- Next.js: `/Users/aideveloper/core/packages/sdks/nextjs/src/`

**NPM Published Packages**: https://www.npmjs.com/~ainative-studio
- @ainative-studio/aikit
- @ainative-studio/react-sdk
- @ainative-studio/vue-sdk
- Other published SDKs

**Hook Patterns to Extract**:
- `useState` and `useCallback` for state management
- Custom hooks returning state + actions (useChat.ts:144-150)
- TypeScript types from shared types file
- Error handling with error states
- API calls with fetch + Authorization headers
- Context integration with `useAINativeContext`
- Cross-framework patterns (React vs Vue vs Svelte)

**Example Files**:
- `hooks/useChat.ts` - Chat completion hook
- `hooks/useCredits.ts` - Credit usage tracking
- `hooks/useZeroDB.ts` - ZeroDB operations
- `AINativeProvider.tsx` - Context provider

### 2.4 MCP Server Implementation

**Location**: `/Users/aideveloper/core/zerodb-mcp-server/index.js`

**MCP Patterns**:
- Tool registration with input schemas
- Async request handlers
- Authentication token management with auto-renewal
- Error handling with descriptive messages
- Validation of inputs (e.g., vector dimensions: 384, 768, 1024, 1536)
- API client with axios + retry logic

**Categories** (76 operations across 11 categories):
- Vector, Quantum, Table, File, Event, Project, RLHF, Memory, Admin, PostgreSQL, Embedding

### 2.5 Coding Standards

**Location**: `/Users/aideveloper/core/.ainative/` and `.claude/`

**Standards to Encode**:
- File placement rules (CRITICAL_FILE_PLACEMENT_RULES.md)
- Git commit format (git-rules.md)
- Issue tracking requirements (ISSUE_TRACKING_ENFORCEMENT.md)
- SDK publishing guidelines (SDK_PUBLISHING_GUIDELINES.md)
- Database query best practices (.claude/skills/database-query-best-practices.md)
- Database schema sync (.claude/skills/database-schema-sync.md)

### 2.6 Agent Swarm Orchestration (CRITICAL)

**Location**: `/Users/aideveloper/core/src/backend/app/agents/swarm/` or `/Users/aideveloper/core/src/backend/app/agents/`

**Critical Importance**: Agent Swarm is a core platform feature for multi-agent orchestration and task coordination.

**Patterns to Extract**:
- **Multi-Agent Coordination**: How multiple agents work together on complex tasks
- **Task Distribution**: Breaking down tasks and assigning to specialized agents
- **Agent Spawning & Lifecycle**: Creating, managing, and terminating agents
- **Communication Patterns**: Inter-agent messaging and data sharing
- **Workflow Management**: Sequential and parallel agent execution patterns
- **State Management**: Tracking agent progress and results
- **Error Recovery**: Handling agent failures and retries
- **Result Aggregation**: Combining outputs from multiple agents

**Example Files**:
- `swarm/orchestrator.py` - Main swarm coordination logic
- `swarm/agent_manager.py` - Agent lifecycle management
- `swarm/task_distributor.py` - Task assignment logic
- `agents/base_agent.py` - Base agent interface
- `agents/specialized_agents/*.py` - Domain-specific agents

**Expected Examples**: 35-40 (critical platform feature)

**Use Cases to Cover**:
- Multi-step data processing workflows
- Parallel research/analysis tasks
- Code generation with review agents
- Complex query decomposition
- Agent collaboration patterns

### 2.7 Common Code Patterns

**Identified Patterns**:
1. **Error Handling**:
   ```python
   try:
       # operation
   except SpecificError as e:
       logger.error(f"Operation failed: {str(e)}")
       raise HTTPException(status_code=status.HTTP_XXX, detail="Message")
   ```

2. **Dependency Injection**:
   ```python
   def get_service(db: Session = Depends(get_db)) -> Service:
       return Service(db)
   ```

3. **Async Patterns**:
   ```python
   async def process_data(data: Data) -> Result:
       async with httpx.AsyncClient() as client:
           response = await client.post(url, json=data)
       return response.json()
   ```

4. **Type Hints**:
   ```python
   from typing import List, Optional, Dict, Any
   from uuid import UUID
   ```

5. **Pydantic Models**:
   ```python
   class RequestModel(BaseModel):
       field: str = Field(..., description="Description", min_length=1)
   ```

---

## 3. Training Dataset Categories

### Category 1: ZeroDB API Usage (50 examples)

**Focus**: Generate correct ZeroDB API calls for vector storage, semantic search, tables

**Example Template**:
```json
{
  "messages": [
    {
      "role": "system",
      "content": "You are an expert AINative platform developer. Generate code following project standards: FastAPI with Pydantic, async patterns, type hints, error handling. NEVER include AI attribution. Write TDD/BDD tests with 80%+ coverage."
    },
    {
      "role": "user",
      "content": "Task: Create an API endpoint to embed documents and store them in ZeroDB\n\nContext:\n- Available: CachedDatabaseService, get_current_user_flexible, get_db\n- Embedding dimensions: 384 (bge-small), 768 (bge-base), 1024 (bge-large)\n- Must validate inputs, handle errors, return proper response model\n\nRequirements:\n- POST /api/v1/embeddings/store\n- Accept list of documents with metadata\n- Generate embeddings using specified model\n- Store in ZeroDB with project scope\n- Include tests"
    },
    {
      "role": "assistant",
      "content": "```python\n# src/backend/app/api/embeddings.py\nfrom fastapi import APIRouter, Depends, HTTPException, status\nfrom pydantic import BaseModel, Field\nfrom typing import List, Optional, Dict, Any\nfrom uuid import UUID\nfrom sqlalchemy.orm import Session\nimport logging\n\nfrom app.api.deps import get_current_user_flexible, get_database_session as get_db\nfrom app.models.user import User\nfrom app.zerodb.services.cached_database_service import CachedDatabaseService\n\nlogger = logging.getLogger(__name__)\nrouter = APIRouter()\n\nclass DocumentInput(BaseModel):\n    text: str = Field(..., min_length=1, description=\"Document text\")\n    metadata: Optional[Dict[str, Any]] = Field(None, description=\"Document metadata\")\n\nclass StoreEmbeddingsRequest(BaseModel):\n    documents: List[DocumentInput] = Field(..., min_items=1, max_items=100)\n    model: str = Field(default=\"BAAI/bge-small-en-v1.5\", description=\"Embedding model\")\n    namespace: str = Field(default=\"default\", description=\"ZeroDB namespace\")\n\nclass StoreEmbeddingsResponse(BaseModel):\n    success: bool\n    vectors_stored: int\n    project_id: UUID\n    dimensions: int\n\ndef get_cached_db_service(db: Session = Depends(get_db)) -> CachedDatabaseService:\n    return CachedDatabaseService(db)\n\n@router.post(\"/embeddings/store\", response_model=StoreEmbeddingsResponse)\nasync def store_embeddings(\n    request: StoreEmbeddingsRequest,\n    current_user: User = Depends(get_current_user_flexible),\n    db_service: CachedDatabaseService = Depends(get_cached_db_service)\n):\n    \"\"\"Store document embeddings in ZeroDB\"\"\"\n    try:\n        # Validate project access\n        project = await db_service.get_user_default_project(current_user.user_id)\n        if not project:\n            raise HTTPException(\n                status_code=status.HTTP_404_NOT_FOUND,\n                detail=\"No active project found\"\n            )\n        \n        # Determine dimensions from model\n        model_dims = {\n            \"BAAI/bge-small-en-v1.5\": 384,\n            \"BAAI/bge-base-en-v1.5\": 768,\n            \"BAAI/bge-large-en-v1.5\": 1024\n        }\n        dimensions = model_dims.get(request.model, 384)\n        \n        # TODO: Call embedding service to generate vectors\n        # TODO: Store vectors in ZeroDB\n        \n        return StoreEmbeddingsResponse(\n            success=True,\n            vectors_stored=len(request.documents),\n            project_id=project.project_id,\n            dimensions=dimensions\n        )\n        \n    except HTTPException:\n        raise\n    except Exception as e:\n        logger.error(f\"Failed to store embeddings: {str(e)}\")\n        raise HTTPException(\n            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,\n            detail=\"Failed to store embeddings\"\n        )\n```\n\n```python\n# tests/test_embeddings_store.py\nimport pytest\nfrom unittest.mock import AsyncMock, MagicMock\nfrom uuid import uuid4\nfrom fastapi import status\n\nclass TestStoreEmbeddings:\n    \"\"\"Test embeddings storage endpoint\"\"\"\n    \n    @pytest.mark.asyncio\n    async def test_should_store_embeddings_successfully(self):\n        \"\"\"Should store embeddings when valid request\"\"\"\n        # Arrange\n        project_id = uuid4()\n        mock_project = MagicMock(project_id=project_id)\n        mock_db_service = AsyncMock()\n        mock_db_service.get_user_default_project.return_value = mock_project\n        \n        request = {\n            \"documents\": [\n                {\"text\": \"Test document 1\", \"metadata\": {\"source\": \"test\"}},\n                {\"text\": \"Test document 2\"}\n            ],\n            \"model\": \"BAAI/bge-small-en-v1.5\",\n            \"namespace\": \"default\"\n        }\n        \n        # Act\n        # response = await store_embeddings(...)\n        \n        # Assert\n        # assert response.success is True\n        # assert response.vectors_stored == 2\n        # assert response.dimensions == 384\n    \n    @pytest.mark.asyncio\n    async def test_should_reject_when_no_project(self):\n        \"\"\"Should return 404 when user has no project\"\"\"\n        # Arrange\n        mock_db_service = AsyncMock()\n        mock_db_service.get_user_default_project.return_value = None\n        \n        # Act & Assert\n        # with pytest.raises(HTTPException) as exc_info:\n        #     await store_embeddings(...)\n        # assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND\n```\n"
    }
  ]
}
```

**Subcategories**:
- Vector upsert and search (10 examples)
- NoSQL table operations (10 examples)
- File storage operations (10 examples)
- Memory operations (10 examples)
- Combined workflows (10 examples)

### Category 2: TDD/BDD Test Generation (60 examples)

**Focus**: Generate pytest tests following project patterns

**Pattern**:
- Class-based test organization
- Async test support
- Mock usage for external dependencies
- BDD-style naming
- Multiple test cases per feature

**Subcategories**:
- API endpoint tests (20 examples)
- Service layer tests (15 examples)
- Middleware tests (10 examples)
- Integration tests (15 examples)

### Category 3: AIkit SDK & Platform SDKs (45 examples)

**Focus**: Generate code using AIkit SDK and framework-specific platform SDKs

**Primary Focus**: AIkit SDK patterns (the core platform SDK)
**Secondary**: React, Vue, Svelte, Next.js specific implementations

**Pattern**:
- TypeScript with proper types
- useState/useCallback patterns (React)
- Composition API patterns (Vue)
- Svelte stores and reactive declarations
- Next.js App Router patterns
- Error handling with error states
- Context integration with `useAINativeContext`
- API authentication with Bearer tokens
- Cross-framework compatibility patterns

**Subcategories**:
- AIkit core SDK patterns (15 examples)
- Chat completion hooks (10 examples)
- ZeroDB operations hooks (10 examples)
- Agent interaction hooks (5 examples)
- Utility hooks (5 examples)

### Category 4: MCP Server Tool Implementation (30 examples)

**Focus**: Generate MCP server tool handlers

**Pattern**:
- Tool registration with schemas
- Input validation
- Authentication token management
- Error handling with descriptive messages
- API client patterns

**Subcategories**:
- ZeroDB MCP tools (15 examples)
- Strapi MCP tools (10 examples)
- Custom MCP tools (5 examples)

### Category 5: File Placement & Standards Compliance (30 examples)

**Focus**: Enforce file placement rules, git commit format, issue tracking

**Pattern**:
- Detect wrong file placements and suggest corrections
- Generate proper git commit messages
- Create issue-linked branch names
- Follow coding standards

**Example**:
```json
{
  "messages": [
    {
      "role": "system",
      "content": "You are an AINative platform expert. Enforce strict file placement rules and coding standards."
    },
    {
      "role": "user",
      "content": "I need to create a guide for the new database migration process. Where should I put the file and what should I name it?"
    },
    {
      "role": "assistant",
      "content": "Based on AINative file placement rules:\n\n**Location**: `docs/database/`\n**Filename**: `MIGRATION_GUIDE.md` or `DATABASE_MIGRATION_PROCESS.md`\n\nRULES:\n- Documentation MUST go in `docs/{category}/`\n- Root-level .md files are FORBIDDEN except README.md and CLAUDE.md\n- Use UPPERCASE for important guides\n- Category should match the content (database docs → docs/database/)\n\nIncorrect placements that will be REJECTED:\n- ✗ `/migration-guide.md` (root level)\n- ✗ `/guides/migration.md` (wrong directory)\n- ✗ `scripts/migration-guide.md` (scripts are for .sh/.py only)\n\nGit workflow:\n1. Create issue first (e.g., #123)\n2. Branch: `docs/123-database-migration-guide`\n3. Commit: \"Add database migration guide\\n\\nRefs #123\""
    }
  ]
}
```

### Category 6: Agent Swarm Orchestration (35 examples)

**Focus**: Multi-agent coordination, task distribution, and swarm workflows

**Critical Importance**: This is a core AINative platform feature that enables complex multi-agent applications.

**Pattern**:
- Agent spawning and lifecycle management
- Task decomposition and distribution
- Inter-agent communication patterns
- Sequential and parallel agent execution
- State management across agents
- Error recovery and retry logic
- Result aggregation from multiple agents
- Agent specialization patterns

**Subcategories**:
- Swarm orchestration patterns (10 examples)
- Multi-agent workflows (10 examples)
- Agent communication (8 examples)
- Task distribution logic (7 examples)

**Example Training Template**:
```json
{
  "messages": [
    {
      "role": "system",
      "content": "You are an expert AINative platform developer specializing in Agent Swarm orchestration..."
    },
    {
      "role": "user",
      "content": "Create an agent swarm workflow that processes a research paper: one agent extracts key points, another generates citations, and a third summarizes findings. Coordinate the agents and aggregate results."
    },
    {
      "role": "assistant",
      "content": "# Agent Swarm implementation with orchestration, task distribution, and result aggregation"
    }
  ]
}
```

### Category 7: Common Coding Patterns (40 examples)

**Focus**: FastAPI patterns, async/await, error handling, type hints

**Pattern**:
- Dependency injection
- Error handling with HTTPException
- Async operations with httpx
- Type hints with typing module
- Pydantic models

**Subcategories**:
- FastAPI routers (15 examples)
- Service layer patterns (10 examples)
- Database operations (10 examples)
- Error handling (5 examples)

### Category 8: OpenAPI Spec Integration (40 examples)

**Focus**: Generate code based on OpenAPI specification patterns

**Data Source**: https://api.ainative.studio/v1/openapi.json

**Critical Importance**: The OpenAPI spec is the authoritative source for all public API endpoints and should be the primary reference for API usage patterns.

**Pattern**:
- Parse OpenAPI spec to extract endpoint definitions
- Generate client code for API consumption
- Create request/response models from schemas
- Implement authentication patterns (Bearer token)
- Handle API errors according to spec
- Generate SDK methods from operations
- Create typed interfaces from OpenAPI schemas

**Subcategories**:
- Public API client generation (15 examples)
- Authentication and authorization (8 examples)
- Request/response model creation (10 examples)
- Error handling per API spec (7 examples)

**Example Training Template**:
```json
{
  "messages": [
    {
      "role": "system",
      "content": "You are an expert AINative platform developer. Use the OpenAPI specification as the authoritative source for API patterns..."
    },
    {
      "role": "user",
      "content": "Based on the OpenAPI spec at https://api.ainative.studio/v1/openapi.json, create a TypeScript client for the /v1/managed-chat/chat/completions endpoint with proper types and error handling."
    },
    {
      "role": "assistant",
      "content": "```typescript\n// Client implementation derived from OpenAPI spec\n// Includes proper types, authentication, error handling\n```"
    }
  ]
}
```

---

## 4. Extraction Methodology

### 4.1 Automated Extraction Script

**Script**: `scripts/extract_ainative_training_data.py`

```python
#!/usr/bin/env python3
"""
Extract training data from AINative codebase for adapter training.
Analyzes code patterns, tests, and documentation to generate JSONL training examples.
"""

import os
import json
import re
from pathlib import Path
from typing import List, Dict, Any
import ast

class AINativeTrainingDataExtractor:
    def __init__(self, core_path: str):
        self.core_path = Path(core_path)
        self.training_data = []

    def extract_api_endpoints(self) -> List[Dict]:
        """Extract API endpoint patterns from backend"""
        api_files = self.core_path.glob("src/backend/app/*/api/*.py")
        examples = []

        for file_path in api_files:
            # Parse AST to extract router definitions, Pydantic models, endpoints
            with open(file_path) as f:
                tree = ast.parse(f.read())

            # Extract patterns and create training examples
            # TODO: Implement AST analysis

        return examples

    def extract_test_patterns(self) -> List[Dict]:
        """Extract TDD/BDD test patterns"""
        test_files = self.core_path.glob("src/backend/tests/**/test_*.py")
        examples = []

        for file_path in test_files:
            # Parse test classes, fixtures, assertions
            # TODO: Implement test pattern extraction

        return examples

    def extract_sdk_hooks(self) -> List[Dict]:
        """Extract React SDK hook patterns"""
        hook_files = self.core_path.glob("packages/sdks/react/src/hooks/*.ts")
        # TODO: Implement hook extraction
        return []

    def extract_standards(self) -> List[Dict]:
        """Extract coding standards from .ainative"""
        standard_files = self.core_path.glob(".ainative/*.md")
        # TODO: Create Q&A examples from standards
        return []

    def generate_jsonl(self, output_path: str):
        """Generate JSONL training file"""
        all_examples = []
        all_examples.extend(self.extract_api_endpoints())
        all_examples.extend(self.extract_test_patterns())
        all_examples.extend(self.extract_sdk_hooks())
        all_examples.extend(self.extract_standards())

        with open(output_path, 'w') as f:
            for example in all_examples:
                f.write(json.dumps(example) + '\\n')

if __name__ == "__main__":
    extractor = AINativeTrainingDataExtractor("/Users/aideveloper/core")
    extractor.generate_jsonl("data/training/ainative_train.jsonl")
```

### 4.2 Manual Curation

**Process**:
1. Review extracted examples for quality
2. Add hand-crafted examples for edge cases
3. Balance dataset across categories
4. Validate format compliance

**Tools**:
- `scripts/validate_training_data.py` (from Kwanzaa project)
- Manual review of 20% sample

---

## 5. Data Format Specification

### 5.1 JSONL Format

Each line is a JSON object:
```json
{
  "messages": [
    {
      "role": "system",
      "content": "System prompt defining behavior and rules"
    },
    {
      "role": "user",
      "content": "User request with context, requirements, available APIs"
    },
    {
      "role": "assistant",
      "content": "Complete code implementation with tests and documentation"
    }
  ]
}
```

### 5.2 System Prompt Template

```
You are an expert AINative platform developer with deep knowledge of:
- FastAPI backend development with async patterns
- ZeroDB vector database operations and semantic search
- AIkit SDK and platform SDKs (React, Vue, Svelte, Next.js)
- Agent Swarm multi-agent orchestration and task coordination
- TDD/BDD testing with pytest (80%+ coverage required)
- MCP server tool implementation
- OpenAPI specification and API client generation

CRITICAL RULES:
- NEVER include AI tool attribution or co-authorship markers
- File placement: docs/{category}/, scripts/, NO root .md files except README.md and project docs
- Every PR links to issue: branch [type]/[issue-number]-[slug]
- Tests MUST pass before commits, coverage >= 80%
- No secrets/PII in logs or code
- Database: Use PgBouncer port 6432, check connection pool
- Use OpenAPI spec (https://api.ainative.studio/v1/openapi.json) as authoritative API reference

Generate production-ready code with:
1. Type hints (typing module)
2. Error handling (HTTPException with proper status codes)
3. Pydantic models for validation
4. Async/await patterns
5. Comprehensive tests (class-based, BDD naming, mocks)
6. Docstrings and comments
7. Agent Swarm patterns for multi-agent workflows
8. AIkit SDK integration for platform features
```

### 5.3 Quality Standards

**Each Example Must Include**:
1. Clear task description with context
2. Available APIs/services listed
3. Requirements and constraints
4. Complete, executable code
5. Tests covering main scenarios
6. Proper error handling
7. Type hints and documentation

**Validation Checks**:
- No AI attribution anywhere
- Valid Python/TypeScript syntax
- Follows file placement rules
- Includes tests
- Has proper error handling
- Uses project patterns

---

## 6. Validation Strategy

### 6.1 Automated Validation

**Script**: `scripts/validate_ainative_training_data.py`

```python
def validate_training_example(example: Dict) -> List[str]:
    """Validate a single training example"""
    errors = []

    # Check structure
    if "messages" not in example:
        errors.append("Missing 'messages' field")

    # Check for AI attribution
    full_text = json.dumps(example).lower()
    forbidden = ["claude", "anthropic", "generated with", "co-authored-by: claude"]
    for term in forbidden:
        if term in full_text:
            errors.append(f"FORBIDDEN: Contains '{term}'")

    # Validate code syntax
    assistant_msg = example["messages"][-1]["content"]
    code_blocks = re.findall(r"```python\n(.*?)\n```", assistant_msg, re.DOTALL)
    for code in code_blocks:
        try:
            ast.parse(code)
        except SyntaxError as e:
            errors.append(f"Syntax error in code: {e}")

    # Check for tests
    if "test" not in assistant_msg.lower():
        errors.append("No tests included")

    return errors
```

### 6.2 Quality Metrics

**Target Metrics**:
- 0% AI attribution (ZERO TOLERANCE)
- 100% valid syntax
- 90%+ include tests
- 95%+ include error handling
- 80%+ include type hints

### 6.3 Review Process

**Phase 1**: Automated validation (all examples)
**Phase 2**: Manual review (20% sample)
**Phase 3**: Technical review by senior developer
**Phase 4**: Final approval

---

## 7. Implementation Roadmap

### Week 1: Extraction & Initial Dataset

**Day 1-2**: Script Development
- Implement extraction script for API endpoints
- AST parsing for Python code
- TypeScript parsing for SDK hooks

**Day 3-4**: Automated Extraction
- Run extraction on all target files
- Initial dataset: ~150 examples
- Validate format compliance

**Day 5**: Quality Review
- Manual review of extracted examples
- Fix syntax errors
- Balance categories

### Week 2: Manual Curation & Refinement

**Day 6-7**: Add Hand-Crafted Examples
- Edge cases not in codebase
- Standards compliance examples (30)
- File placement scenarios (20)

**Day 8-9**: Test Pattern Extraction
- pytest test examples (60)
- Mock patterns
- BDD naming conventions

**Day 10**: SDK & MCP Examples
- React hooks (40)
- MCP tools (30)

### Week 3: Validation & Training

**Day 11-12**: Final Validation
- Run validation script on full dataset
- Fix any issues
- Achieve target metrics

**Day 13**: Training Preparation
- Split into train/eval (90/10)
- Upload to HuggingFace
- Configure training YAML

**Day 14**: Training & Testing
- Train adapter v1 (4 epochs, 2e-4 LR)
- Test with validation scripts
- Iterate if needed

---

## 8. Expected Outcomes

### 8.1 Model Capabilities

**The adapter will be able to**:
- ✅ Generate FastAPI endpoints with proper Pydantic models
- ✅ Create ZeroDB API calls with correct dimensions and namespaces
- ✅ Write pytest tests following TDD/BDD patterns
- ✅ Generate React hooks with TypeScript types
- ✅ Implement MCP server tools with validation
- ✅ Suggest correct file placements
- ✅ Follow git commit and branch naming standards
- ✅ Add comprehensive error handling
- ✅ Include type hints and docstrings

**The adapter will NOT be able to**:
- ❌ Design complex system architectures
- ❌ Debug novel runtime errors
- ❌ Make high-level product decisions
- ❌ Handle scenarios not in training data

### 8.2 Success Metrics

**Training Metrics**:
- Loss convergence < 0.5
- Eval loss similar to train loss (no overfitting)
- Citation coverage > 0% (if using RAG patterns)

**Validation Metrics**:
- Generates syntactically correct code: 95%+
- Includes tests: 80%+
- Follows file placement rules: 100%
- No AI attribution: 100%
- Proper error handling: 90%+

**Production Metrics** (after deployment):
- Reduces boilerplate coding time: 30-50%
- Test coverage compliance: 80%+
- Code review iterations reduced: 20-30%
- Standards violations: <5%

---

## 9. Risk Mitigation

### Risk 1: Catastrophic Forgetting

**Mitigation**:
- Use conservative training (4 epochs, 2e-4 LR like Kwanzaa v4)
- Monitor validation loss
- Test on held-out examples

### Risk 2: Overfitting to Patterns

**Mitigation**:
- Diverse examples across categories
- Include variations and edge cases
- Regular evaluation during training

### Risk 3: AI Attribution Leakage

**Mitigation**:
- Automated validation script catches 100% of cases
- Manual review by human
- Zero tolerance policy

### Risk 4: Dataset Imbalance

**Mitigation**:
- Track examples per category
- Balance extraction vs manual curation
- Minimum 30 examples per category

---

## 10. Next Steps

### Immediate Actions

1. ✅ Review and approve this extraction plan
2. [ ] Implement `scripts/extract_ainative_training_data.py`
3. [ ] Run extraction on `/Users/aideveloper/core`
4. [ ] Validate initial dataset
5. [ ] Begin manual curation

### Future Enhancements

**Multi-Adapter Strategy** (Phase 2):
- Adapter 1: ZeroDB Expert (vector operations, semantic search)
- Adapter 2: TDD/BDD Generator (test patterns, coverage)
- Adapter 3: Standards Enforcer (file placement, git rules)

**Continuous Improvement**:
- Collect production usage data
- RLHF feedback loops
- Quarterly retraining with new patterns

---

## Appendix A: File Locations Reference

### Documentation
- `/Users/aideveloper/core/docs/developer/TUTORIAL.md`
- `/Users/aideveloper/core/CLAUDE.md`
- `/Users/aideveloper/core/.ainative/*.md`

### Backend Code
- `/Users/aideveloper/core/src/backend/app/zerodb/api/`
- `/Users/aideveloper/core/src/backend/app/models/`
- `/Users/aideveloper/core/src/backend/app/services/`

### Tests
- `/Users/aideveloper/core/src/backend/tests/`
- `/Users/aideveloper/core/src/backend/app/zerodb/tests/`

### SDKs
- `/Users/aideveloper/core/packages/sdks/react/src/`
- `/Users/aideveloper/core/packages/sdks/vue/src/`

### MCP Servers
- `/Users/aideveloper/core/zerodb-mcp-server/index.js`
- `/Users/aideveloper/core/packages/mcp-servers/ainative-strapi-mcp-server/`

### Standards
- `/Users/aideveloper/core/.ainative/CRITICAL_FILE_PLACEMENT_RULES.md`
- `/Users/aideveloper/core/.ainative/git-rules.md`
- `/Users/aideveloper/core/.claude/skills/*.md`

---

## Appendix B: Training Configuration

```yaml
# training/config/ainative-adapter-training.yaml
model:
  base_model: "meta-llama/Llama-3.2-1B-Instruct"
  adapter_name: "ainative-coding-assistant-v1"

lora:
  r: 16
  alpha: 32
  dropout: 0.05
  target_modules:
    - "q_proj"
    - "k_proj"
    - "v_proj"
    - "o_proj"
    - "gate_proj"
    - "up_proj"
    - "down_proj"

training:
  num_train_epochs: 4  # Conservative like Kwanzaa v4
  learning_rate: 0.0002  # 2e-4
  per_device_train_batch_size: 2
  gradient_accumulation_steps: 4
  warmup_steps: 10
  lr_scheduler_type: "cosine"
  optim: "paged_adamw_8bit"

dataset:
  train_file: "data/training/ainative_train.jsonl"
  eval_file: "data/training/ainative_eval.jsonl"
  max_seq_length: 2048

evaluation:
  eval_steps: 50
  save_steps: 100
  logging_steps: 10
```

---

**Plan Version**: 1.0
**Date**: 2026-01-22
**Author**: AI Development Team
**Status**: Ready for Review
