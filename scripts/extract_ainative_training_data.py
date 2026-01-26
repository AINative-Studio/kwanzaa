#!/usr/bin/env python3
"""
Extract Training Data from AINative Codebase

This script analyzes the AINative core codebase to extract high-quality
training examples for the coding assistant adapter.

Categories:
1. ZeroDB API Usage (50 examples)
2. TDD/BDD Test Generation (60 examples)
3. React SDK Hooks (40 examples)
4. MCP Server Tools (30 examples)
5. File Placement & Standards (30 examples)
6. Common Coding Patterns (40 examples)

Issue: #70
Epic: #69
"""

import os
import json
import re
import ast
from pathlib import Path
from typing import List, Dict, Any, Optional
import argparse
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class AINativeTrainingDataExtractor:
    """
    Extract training examples from AINative codebase.

    Analyzes Python/TypeScript code to create JSONL training examples
    following the format used in Kwanzaa adapter training.
    """

    def __init__(self, core_path: str, output_path: str):
        self.core_path = Path(core_path)
        self.output_path = Path(output_path)
        self.training_examples: List[Dict] = []

        # Validation tracking
        self.stats = {
            "api_endpoints": 0,
            "test_patterns": 0,
            "sdk_hooks": 0,
            "mcp_tools": 0,
            "standards": 0,
            "patterns": 0,
            "agent_swarm": 0,
            "openapi_spec": 0,
            "total": 0
        }

    def extract_all(self) -> List[Dict]:
        """Extract all training examples from codebase."""
        logger.info("Starting extraction from %s", self.core_path)

        # Extract from each category
        logger.info("Extracting API endpoints...")
        self.extract_api_endpoints()

        logger.info("Extracting test patterns...")
        self.extract_test_patterns()

        logger.info("Extracting SDK hooks...")
        self.extract_sdk_hooks()

        logger.info("Extracting MCP tools...")
        self.extract_mcp_tools()

        logger.info("Extracting standards examples...")
        self.extract_standards()

        logger.info("Extracting common patterns...")
        self.extract_common_patterns()

        logger.info("Extracting Agent Swarm patterns...")
        self.extract_agent_swarm()

        logger.info("Extracting from OpenAPI spec...")
        self.extract_openapi_spec()

        return self.training_examples

    def extract_api_endpoints(self) -> List[Dict]:
        """Extract FastAPI endpoint patterns from backend."""
        examples = []

        # Find all API files in ZeroDB
        api_path = self.core_path / "src" / "backend" / "app" / "zerodb" / "api"
        if not api_path.exists():
            logger.warning("API path does not exist: %s", api_path)
            return examples

        api_files = list(api_path.glob("*.py"))
        logger.info("Found %d API files to analyze", len(api_files))

        for file_path in api_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Parse AST to find endpoints
                tree = ast.parse(content)

                # Extract router definitions, Pydantic models, endpoints
                example = self._analyze_api_file(file_path, tree, content)
                if example:
                    examples.append(example)
                    self.stats["api_endpoints"] += 1

            except Exception as e:
                logger.error("Failed to parse %s: %s", file_path, e)

        self.training_examples.extend(examples)
        return examples

    def _analyze_api_file(self, file_path: Path, tree: ast.AST, content: str) -> Optional[Dict]:
        """Analyze a single API file and create training example."""
        # TODO: Implement detailed AST analysis
        # For now, create placeholder structure

        # Extract class definitions (Pydantic models)
        models = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]

        # Extract function definitions (endpoints)
        functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]

        if not functions:
            return None

        # Create training example from first endpoint found
        for func in functions:
            if any(decorator.id == 'router' for decorator in func.decorator_list
                   if isinstance(decorator, ast.Attribute)):
                # Found an API endpoint
                return self._create_api_example(file_path, func, models, content)

        return None

    def _create_api_example(self, file_path: Path, func: ast.FunctionDef,
                           models: List[ast.ClassDef], content: str) -> Dict:
        """Create a training example from API endpoint."""
        # TODO: Create full training example with context
        # For now, return placeholder
        return {
            "messages": [
                {
                    "role": "system",
                    "content": self._get_system_prompt()
                },
                {
                    "role": "user",
                    "content": f"Create an API endpoint similar to the one in {file_path.name}"
                },
                {
                    "role": "assistant",
                    "content": f"# Extracted from {file_path}\n# TODO: Add full implementation"
                }
            ]
        }

    def extract_test_patterns(self) -> List[Dict]:
        """Extract pytest test patterns from test files."""
        examples = []

        # Find test files
        test_path = self.core_path / "src" / "backend" / "tests"
        if not test_path.exists():
            logger.warning("Test path does not exist: %s", test_path)
            return examples

        test_files = list(test_path.rglob("test_*.py"))
        logger.info("Found %d test files to analyze", len(test_files))

        for file_path in test_files[:30]:  # Extract from 30 test files
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                tree = ast.parse(content)

                # Extract test classes and methods
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef) and node.name.startswith('Test'):
                        example = self._create_test_example(file_path, node, content)
                        if example:
                            examples.append(example)
                            self.stats["test_patterns"] += 1
                            break  # One example per file for now

            except Exception as e:
                logger.error("Failed to parse test file %s: %s", file_path, e)

        self.training_examples.extend(examples)
        return examples

    def _create_test_example(self, file_path: Path, test_class: ast.ClassDef,
                            content: str) -> Optional[Dict]:
        """Create training example from test class."""
        # TODO: Extract full test pattern
        # For now, return placeholder
        return {
            "messages": [
                {
                    "role": "system",
                    "content": self._get_system_prompt()
                },
                {
                    "role": "user",
                    "content": f"Create pytest tests for a feature similar to {test_class.name}"
                },
                {
                    "role": "assistant",
                    "content": f"# Test pattern from {file_path.name}\n# TODO: Add full test implementation"
                }
            ]
        }

    def extract_sdk_hooks(self) -> List[Dict]:
        """Extract React SDK hook patterns."""
        examples = []

        # Find React SDK hooks
        hooks_path = self.core_path / "packages" / "sdks" / "react" / "src" / "hooks"
        if not hooks_path.exists():
            logger.warning("React hooks path does not exist: %s", hooks_path)
            return examples

        hook_files = list(hooks_path.glob("*.ts"))
        logger.info("Found %d React hook files", len(hook_files))

        for file_path in hook_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Simple pattern matching for hook function
                if 'export function use' in content:
                    example = self._create_hook_example(file_path, content)
                    if example:
                        examples.append(example)
                        self.stats["sdk_hooks"] += 1

            except Exception as e:
                logger.error("Failed to read hook file %s: %s", file_path, e)

        self.training_examples.extend(examples)
        return examples

    def _create_hook_example(self, file_path: Path, content: str) -> Optional[Dict]:
        """Create training example from React hook."""
        # TODO: Parse TypeScript and extract full hook pattern
        return {
            "messages": [
                {
                    "role": "system",
                    "content": self._get_system_prompt()
                },
                {
                    "role": "user",
                    "content": f"Create a React hook for AINative platform integration"
                },
                {
                    "role": "assistant",
                    "content": f"// Hook pattern from {file_path.name}\n// TODO: Add full hook implementation"
                }
            ]
        }

    def extract_mcp_tools(self) -> List[Dict]:
        """Extract MCP server tool definitions."""
        examples = []

        # Find MCP server index
        mcp_path = self.core_path / "zerodb-mcp-server" / "index.js"
        if not mcp_path.exists():
            logger.warning("MCP server path does not exist: %s", mcp_path)
            return examples

        try:
            with open(mcp_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Simple extraction - find tool definitions
            # TODO: Parse JavaScript properly
            self.stats["mcp_tools"] += 1

        except Exception as e:
            logger.error("Failed to read MCP server: %s", e)

        return examples

    def extract_standards(self) -> List[Dict]:
        """Extract coding standards and file placement rules."""
        examples = []

        # Find .ainative standards docs
        ainative_path = self.core_path / ".ainative"
        if not ainative_path.exists():
            logger.warning(".ainative path does not exist: %s", ainative_path)
            return examples

        standard_files = list(ainative_path.glob("*.md"))
        logger.info("Found %d standards files", len(standard_files))

        for file_path in standard_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Create Q&A examples from standards
                if "FILE_PLACEMENT" in file_path.name:
                    example = self._create_file_placement_example(content)
                    if example:
                        examples.append(example)
                        self.stats["standards"] += 1

            except Exception as e:
                logger.error("Failed to read standards file %s: %s", file_path, e)

        self.training_examples.extend(examples)
        return examples

    def _create_file_placement_example(self, content: str) -> Optional[Dict]:
        """Create file placement training example."""
        # TODO: Parse markdown and create Q&A examples
        return {
            "messages": [
                {
                    "role": "system",
                    "content": self._get_system_prompt()
                },
                {
                    "role": "user",
                    "content": "Where should I place a database migration guide?"
                },
                {
                    "role": "assistant",
                    "content": "Based on AINative file placement rules:\n\nLocation: `docs/database/`\nFilename: `MIGRATION_GUIDE.md`\n\nRULES:\n- Documentation MUST go in `docs/{category}/`\n- Root-level .md files are FORBIDDEN except README.md and CLAUDE.md"
                }
            ]
        }

    def extract_common_patterns(self) -> List[Dict]:
        """Extract common coding patterns."""
        examples = []

        # TODO: Extract dependency injection, error handling, async patterns
        self.stats["patterns"] += 1

        return examples

    def extract_agent_swarm(self) -> List[Dict]:
        """Extract Agent Swarm orchestration patterns."""
        examples = []

        # Find Agent Swarm files
        swarm_paths = [
            self.core_path / "src" / "backend" / "app" / "agents" / "swarm",
            self.core_path / "src" / "backend" / "app" / "agents"
        ]

        for swarm_path in swarm_paths:
            if not swarm_path.exists():
                logger.warning("Agent Swarm path does not exist: %s", swarm_path)
                continue

            swarm_files = list(swarm_path.rglob("*.py"))
            logger.info("Found %d Agent Swarm files in %s", len(swarm_files), swarm_path)

            for file_path in swarm_files[:15]:  # Extract from 15 swarm files
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # Look for orchestration patterns
                    if 'swarm' in file_path.name.lower() or 'orchestrat' in content.lower():
                        example = self._create_agent_swarm_example(file_path, content)
                        if example:
                            examples.append(example)
                            self.stats["agent_swarm"] += 1

                except Exception as e:
                    logger.error("Failed to read agent swarm file %s: %s", file_path, e)

        self.training_examples.extend(examples)
        return examples

    def _create_agent_swarm_example(self, file_path: Path, content: str) -> Optional[Dict]:
        """Create training example from Agent Swarm code."""
        # TODO: Parse and extract actual swarm patterns
        return {
            "messages": [
                {
                    "role": "system",
                    "content": self._get_system_prompt()
                },
                {
                    "role": "user",
                    "content": f"Create an Agent Swarm orchestration pattern similar to {file_path.name}"
                },
                {
                    "role": "assistant",
                    "content": f"# Agent Swarm pattern from {file_path.name}\n# TODO: Add full implementation"
                }
            ]
        }

    def extract_openapi_spec(self) -> List[Dict]:
        """Extract API patterns from OpenAPI specification."""
        examples = []

        # OpenAPI spec URL
        openapi_url = "https://api.ainative.studio/v1/openapi.json"

        try:
            import urllib.request
            logger.info("Downloading OpenAPI spec from %s", openapi_url)

            # Download OpenAPI spec
            with urllib.request.urlopen(openapi_url) as response:
                openapi_spec = json.loads(response.read().decode())

            # Extract paths (endpoints)
            paths = openapi_spec.get("paths", {})
            logger.info("Found %d API endpoints in OpenAPI spec", len(paths))

            # Create examples from first few endpoints
            for path, methods in list(paths.items())[:25]:  # Extract from 25 API endpoints
                for method, operation in methods.items():
                    if method.upper() in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']:
                        example = self._create_openapi_example(path, method, operation)
                        if example:
                            examples.append(example)
                            self.stats["openapi_spec"] += 1

        except Exception as e:
            logger.error("Failed to download OpenAPI spec: %s", e)
            logger.info("Continuing without OpenAPI examples...")

        self.training_examples.extend(examples)
        return examples

    def _create_openapi_example(self, path: str, method: str, operation: Dict) -> Optional[Dict]:
        """Create training example from OpenAPI endpoint definition."""
        summary = operation.get("summary", "")
        description = operation.get("description", "")

        # TODO: Extract full request/response schemas
        return {
            "messages": [
                {
                    "role": "system",
                    "content": self._get_system_prompt()
                },
                {
                    "role": "user",
                    "content": f"Create a client for the {method.upper()} {path} endpoint. {summary}"
                },
                {
                    "role": "assistant",
                    "content": f"# API client for {method.upper()} {path}\n# {description}\n# TODO: Add full implementation"
                }
            ]
        }

    def _get_system_prompt(self) -> str:
        """Get standard system prompt for all examples."""
        return """You are an expert AINative platform developer with deep knowledge of:
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
8. AIkit SDK integration for platform features"""

    def generate_jsonl(self):
        """Generate JSONL output file."""
        self.output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(self.output_path, 'w', encoding='utf-8') as f:
            for example in self.training_examples:
                f.write(json.dumps(example, ensure_ascii=False) + '\n')

        logger.info("Wrote %d examples to %s", len(self.training_examples), self.output_path)

    def print_stats(self):
        """Print extraction statistics."""
        self.stats["total"] = len(self.training_examples)

        print("\n" + "="*60)
        print("EXTRACTION STATISTICS")
        print("="*60)
        print(f"API Endpoints:     {self.stats['api_endpoints']}")
        print(f"Test Patterns:     {self.stats['test_patterns']}")
        print(f"SDK Hooks:         {self.stats['sdk_hooks']}")
        print(f"MCP Tools:         {self.stats['mcp_tools']}")
        print(f"Standards:         {self.stats['standards']}")
        print(f"Common Patterns:   {self.stats['patterns']}")
        print(f"Agent Swarm:       {self.stats['agent_swarm']}")
        print(f"OpenAPI Spec:      {self.stats['openapi_spec']}")
        print("-" * 60)
        print(f"TOTAL:             {self.stats['total']}")
        print("="*60)


def main():
    parser = argparse.ArgumentParser(
        description='Extract training data from AINative codebase'
    )
    parser.add_argument(
        '--core-path',
        default='/Users/aideveloper/core',
        help='Path to AINative core codebase'
    )
    parser.add_argument(
        '--output',
        default='data/training/ainative_train_extracted.jsonl',
        help='Output JSONL file path'
    )
    parser.add_argument(
        '--limit',
        type=int,
        default=None,
        help='Limit number of examples per category'
    )

    args = parser.parse_args()

    extractor = AINativeTrainingDataExtractor(args.core_path, args.output)

    try:
        extractor.extract_all()
        extractor.generate_jsonl()
        extractor.print_stats()

        print("\n✅ Extraction complete!")
        print(f"📝 Output: {args.output}")
        print(f"📊 Total examples: {extractor.stats['total']}")

    except Exception as e:
        logger.error("Extraction failed: %s", e)
        raise


if __name__ == "__main__":
    main()
