# Kwanzaa UI - RAGBot Upload + Preview Interface

React-based document curation interface with AIKit components, safety scanning, and observability.

## Overview

This UI implements the complete RAGBot document upload and curation workflow as specified in Epic 7, Issue #38.

## Features

- **6-Step Workflow**: Upload → Metadata → Safety Scan → Preview → Review → Publish
- **AIKit Components**: Custom component library with Progress, Streaming, Code, and Markdown renderers
- **Safety Integration**: PII detection and content moderation
- **Observability**: Comprehensive metrics tracking
- **ZeroDB Integration**: Vector database operations

## Quick Start

```bash
npm run dev
```

Access at: http://localhost:5173

## Documentation

- [Curator Workflow Guide](../docs/development-guides/ragbot-curator-workflow.md)
- [Implementation Summary](../docs/reports/ragbot-upload-preview-implementation.md)

---

**Version**: 1.0.0 | **Issue**: #38 (Epic 7)
