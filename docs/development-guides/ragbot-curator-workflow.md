# RAGBot Upload + Preview Curator Workflow

**Epic 7 - Issue #38 Implementation**

Complete guide for document curators using the RAGBot Upload + Preview UI with AIKit components, safety scanning, and observability.

## Overview

The RAGBot curation workflow ensures high-quality, properly attributed documents are added to the vector database with comprehensive safety checks and provenance tracking.

## Workflow Steps

### 1. Upload Document

**Purpose**: Upload documents for processing and curation.

**Supported Formats**:
- PDF (`.pdf`)
- Plain Text (`.txt`)
- Markdown (`.md`)
- Word Documents (`.docx`)

**Size Limit**: 50MB

**UI Features**:
- Drag-and-drop interface
- File validation
- AIKit `ProgressBar` for upload tracking
- Real-time size/type validation

**API Endpoint**: `POST /api/v1/ragbot/upload`

```bash
curl -X POST \
  -F "file=@document.pdf" \
  https://api.example.com/api/v1/ragbot/upload
```

**Response**:
```json
{
  "document_id": "a1b2c3d4-...",
  "filename": "document.pdf",
  "size": 1234567,
  "status": "uploaded"
}
```

---

### 2. Enter Metadata

**Purpose**: Capture provenance information for attribution.

**Required Fields**:
- **Source Organization**: Origin of the document
- **Canonical URL**: Permanent reference URL
- **License**: Copyright/license status
- **Year**: Publication year
- **Content Type**: Document category

**Optional Fields**:
- Author
- Title
- Tags (comma-separated)

**Validation Rules**:
- URL must be valid (https:// or http://)
- Year must be between 1800 and current year
- All required fields must be non-empty

**UI Features**:
- Auto-complete for common values
- Inline validation
- License dropdown with common options

**Example Metadata**:
```json
{
  "source_org": "Library of Congress",
  "canonical_url": "https://www.loc.gov/item/example/",
  "license": "Public Domain",
  "year": 1963,
  "content_type": "speech",
  "author": "Dr. Martin Luther King Jr.",
  "title": "I Have a Dream",
  "tags": ["civil-rights", "speech", "primary-source"]
}
```

---

### 3. Safety Scan

**Purpose**: Detect PII and harmful content before publication.

**CRITICAL**: This step is **mandatory** per Issue #38 requirements.

#### PII Detection

**Detected Types**:
- Email addresses
- Phone numbers
- Social Security Numbers (SSN)
- Credit card numbers
- Physical addresses (future)
- Personal names (future)

**UI Components**:
- AIKit `PIIDetector` with visual highlighting
- Color-coded by PII type
- Confidence scores
- Count summary

**Example PII Detection**:
```
⚠ PII Detected: 3 instances found

EMAIL: 2
PHONE: 1
```

#### Content Moderation

**Categories Checked**:
- Hate speech
- Violence
- Sexual content
- Harassment
- Self-harm
- Spam

**Severity Levels**:
- **LOW**: Proceed with caution
- **MEDIUM**: Review recommended
- **HIGH**: Manual review required
- **CRITICAL**: Publication blocked

**UI Components**:
- AIKit `ContentModerator` with results table
- Severity indicators
- Recommended actions
- Detailed reports

**Curator Decisions**:

1. **Proceed**: Continue if no critical issues
2. **Auto-Redact PII**: Checkbox to redact detected PII
3. **Cancel**: Return to previous step
4. **Cannot Proceed**: Automatic if critical violations detected

**API Endpoint**: `POST /api/v1/ragbot/scan-safety`

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "document_id": "a1b2c3d4-...",
    "text": "Document text here...",
    "metadata": {...}
  }' \
  https://api.example.com/api/v1/ragbot/scan-safety
```

**Response**:
```json
{
  "document_id": "a1b2c3d4-...",
  "pii_matches": [
    {
      "type": "email",
      "value": "user@example.com",
      "start": 145,
      "end": 161,
      "confidence": 0.9
    }
  ],
  "moderation_results": [
    {
      "category": "hate_speech",
      "detected": false,
      "confidence": 0.1,
      "severity": "low"
    }
  ],
  "scan_timestamp": "2026-01-16T23:30:00Z",
  "passed": true
}
```

---

### 4. Chunk Preview

**Purpose**: Review document chunks and embeddings.

**Features**:
- Chunk-by-chunk navigation
- AIKit `MarkdownRenderer` for content display
- AIKit `CodeBlock` for metadata JSON
- Embedding preview (first 10 dimensions)
- Chunk boundaries visualization

**Chunking Strategy**:
- **Chunk Size**: 500 characters
- **Overlap**: 50 characters
- **Embeddings**: 384-dimensional vectors (all-MiniLM-L6-v2)

**UI Layout**:
```
[Chunk List]  |  [Chunk Content]
Chunk 1       |  Rendered text with MarkdownRenderer
Chunk 2       |
Chunk 3       |  [Show Metadata] (expandable)
...           |  - JSON preview with CodeBlock
```

**API Endpoint**: `POST /api/v1/ragbot/chunk-preview`

**Response**:
```json
{
  "document_id": "a1b2c3d4-...",
  "chunks": [
    {
      "chunk_id": "a1b2c3d4-..._chunk_0",
      "text": "Chunk text content...",
      "chunk_index": 0,
      "embedding_preview": [0.123, -0.456, ...],
      "metadata": {
        "document_id": "a1b2c3d4-...",
        "chunk_index": 0,
        "start_char": 0,
        "end_char": 500
      }
    }
  ],
  "chunk_count": 42,
  "generation_time_ms": 1234
}
```

---

### 5. Review & Validation

**Purpose**: Final verification before publication.

**Validation Checklist**:
- [ ] Provenance information verified and accurate
- [ ] License allows publication and attribution is correct
- [ ] Content reviewed and appropriate for publication
- [ ] Safety scan results reviewed and acceptable

**All checkboxes must be checked to proceed.**

**Components**:
1. **Provenance Summary**: Display all metadata
2. **Safety Summary**: PII/moderation flags count
3. **Content Summary**: Chunk statistics
4. **Namespace Selection**: Choose target namespace

**Available Namespaces**:
- `kwanzaa_primary_sources` - Historical primary sources
- `kwanzaa_black_press` - Black newspaper archives
- `kwanzaa_speeches_letters` - Speeches and correspondence
- `kwanzaa_black_stem` - STEM contributions
- `kwanzaa_teaching_kits` - Educational materials

---

### 6. Publish / Reject

**Purpose**: Final decision and execution.

#### Publish

**Process**:
1. Confirm publication details
2. Upload vectors to ZeroDB
3. Track metrics
4. Return success confirmation

**UI Components**:
- AIKit `ProgressBar` during publication
- AIKit `ToolResult` for result display
- Success/error notifications

**API Endpoint**: `POST /api/v1/ragbot/publish`

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "document_id": "a1b2c3d4-...",
    "namespace": "kwanzaa_primary_sources",
    "chunks": [...],
    "metadata": {...}
  }' \
  https://api.example.com/api/v1/ragbot/publish
```

**Response**:
```json
{
  "document_id": "a1b2c3d4-...",
  "namespace": "kwanzaa_primary_sources",
  "vectors_created": 42,
  "status": "published",
  "duration_ms": 3456
}
```

#### Reject

**Reasons for Rejection**:
- Quality issues
- Licensing concerns
- Safety violations
- Duplicate content
- Out of scope

**API Endpoint**: `POST /api/v1/ragbot/reject`

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "document_id": "a1b2c3d4-...",
    "reason": "Quality issues"
  }' \
  https://api.example.com/api/v1/ragbot/reject
```

---

## Safety Integration (REQUIRED)

### PII Detection

**Implementation**: `app/services/safety_scanner.py`

**Patterns**:
```python
EMAIL: r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
PHONE: r'\b(\+?1?[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b'
SSN: r'\b\d{3}-\d{2}-\d{4}\b'
CREDIT_CARD: r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'
```

**Auto-Redaction**:
```python
# Before: "Contact me at john@example.com"
# After: "Contact me at [EMAIL_REDACTED]"
```

### Content Moderation

**Categories**: hate_speech, violence, sexual, harassment, self_harm, spam

**Severity Mapping**:
- Confidence > 0.8 → **CRITICAL**
- Confidence > 0.6 → **HIGH**
- Confidence > 0.4 → **MEDIUM**
- Confidence ≤ 0.4 → **LOW**

**Blocking Rules**:
- **CRITICAL** violations → Cannot proceed
- **HIGH** violations → Manual review warning
- **MEDIUM/LOW** → Proceed with acknowledgment

---

## Observability (REQUIRED)

### Tracked Metrics

**Upload Metrics**:
- File size
- File type
- Upload duration
- Success/failure rate

**Safety Scan Metrics**:
- PII detection rate
- Moderation flag frequency
- Scan duration
- False positive tracking

**Chunk Generation Metrics**:
- Chunks per document (avg)
- Generation duration
- Embedding quality scores

**Curator Actions**:
- Publish count
- Reject count with reasons
- Edit operations
- Time per document

### Metrics Dashboard

**API Endpoint**: `GET /api/v1/ragbot/metrics`

**Response**:
```json
{
  "total_uploads": 156,
  "total_safety_scans": 156,
  "total_chunks_generated": 6540,
  "curator_actions": {
    "publish": 142,
    "reject": 14
  },
  "avg_chunk_generation_time_ms": 1234,
  "pii_detection_rate": 0.23
}
```

**UI Components**:
- Time-series charts
- Action breakdown pie charts
- Performance metrics
- Alert thresholds

---

## ZeroDB Integration

### Vector Storage

**Batch Upsert**: `/api/v1/vectors/batch-upsert`

**Vector Structure**:
```json
{
  "vector_embedding": [0.123, -0.456, ...],  // 384 dimensions
  "document": "Chunk text",
  "metadata": {
    "document_id": "a1b2c3d4-...",
    "chunk_index": 0,
    "source_org": "Library of Congress",
    "canonical_url": "https://...",
    "license": "Public Domain",
    "year": 1963,
    "content_type": "speech",
    "namespace": "kwanzaa_primary_sources"
  },
  "namespace": "kwanzaa_primary_sources"
}
```

### Namespace Strategy

**Isolation**: Each namespace is separate for targeted search

**Naming Convention**: `kwanzaa_{category}`

**Search Filters**: Metadata filters for year, source, license

---

## Error Handling

### Common Errors

1. **Upload Failed**
   - Check file size (<50MB)
   - Verify file type
   - Check network connection

2. **Safety Scan Failed**
   - Retry scan
   - Check document text extraction
   - Review API logs

3. **Publication Failed**
   - Verify ZeroDB credentials
   - Check namespace permissions
   - Review vector dimensions (must be 384)

4. **Critical Content Detected**
   - Cannot proceed automatically
   - Requires manual curator review
   - Document safety report
   - Escalate if uncertain

---

## Best Practices

### For Curators

1. **Always verify provenance** - Double-check source and URL
2. **Review safety reports** - Don't skip PII warnings
3. **Check chunk quality** - Ensure meaningful boundaries
4. **Use consistent tags** - Follow established taxonomy
5. **Document rejections** - Provide clear reasons

### For Developers

1. **Test with real documents** - Use diverse content
2. **Monitor metrics** - Watch for pipeline bottlenecks
3. **Update PII patterns** - Add new detection rules
4. **Tune chunking** - Optimize for content type
5. **Log safety events** - Track all detections

---

## AIKit Components Used

### React Components
- `ProgressBar` - Upload/processing progress
- `StreamingIndicator` - Loading states
- `CodeBlock` - JSON preview
- `MarkdownRenderer` - Chunk text display
- `ToolResult` - Extraction results
- `StreamingToolResult` - Real-time chunking

### Safety Components
- `PIIDetector` - PII scanning and highlighting
- `ContentModerator` - Content policy enforcement

### Observability
- `MetricsTracker` - Event tracking and reporting

### ZeroDB
- `ZeroDBClient` - Vector database operations

---

## Deployment

### Environment Variables

```bash
# Backend (.env)
ZERODB_API_URL=https://api.ainative.studio
ZERODB_PROJECT_ID=your-project-id
ZERODB_API_KEY=your-api-key

# Frontend
VITE_API_URL=https://api.example.com
```

### Running Locally

**Backend**:
```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

**Frontend**:
```bash
cd ui
npm run dev
```

### Testing

```bash
# Backend tests
cd backend
pytest tests/test_ragbot_api.py -v

# Frontend tests
cd ui
npm test
```

---

## Support

For issues or questions:
- GitHub Issues: [Project Issues](https://github.com/yourorg/kwanzaa/issues)
- Documentation: `/docs/`
- Slack: #kwanzaa-support

---

**Last Updated**: January 16, 2026
**Version**: 1.0.0
**Issue**: #38 (Epic 7)
