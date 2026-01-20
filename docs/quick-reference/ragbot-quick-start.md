# RAGBot Quick Start Guide

**Get the RAGBot Upload + Preview UI running in 5 minutes**

## Prerequisites

- Python 3.9+
- Node.js 18+
- ZeroDB API credentials

## Backend Setup

```bash
cd backend
pip install -r requirements.txt

# Configure
echo "ZERODB_API_URL=https://api.ainative.studio" > .env
echo "ZERODB_PROJECT_ID=your-project-id" >> .env
echo "ZERODB_API_KEY=your-api-key" >> .env

# Run
uvicorn app.main:app --reload --port 8000
```

Backend: http://localhost:8000

## Frontend Setup

```bash
cd ui
npm install

# Configure
echo "VITE_API_URL=http://localhost:8000" > .env

# Run
npm run dev
```

Frontend: http://localhost:5173

## Test Workflow

1. Open http://localhost:5173
2. Upload PDF/TXT
3. Enter metadata
4. Review safety scan
5. Preview chunks
6. Complete checklist
7. Publish

## Documentation

- [Full Guide](../development-guides/ragbot-curator-workflow.md)
- [Implementation](../reports/ragbot-upload-preview-implementation.md)

---

**Issue #38** | January 16, 2026
