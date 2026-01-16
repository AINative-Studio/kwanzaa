"""
RAGBot Upload + Preview API Endpoints

Epic 7 - Issue #38: Document upload and curation workflow
with safety scanning and observability.

Endpoints:
- POST /api/v1/ragbot/upload - Upload document
- POST /api/v1/ragbot/scan-safety - Run safety scan
- POST /api/v1/ragbot/chunk-preview - Generate chunk preview
- POST /api/v1/ragbot/publish - Publish to ZeroDB
- POST /api/v1/ragbot/reject - Reject document
- GET /api/v1/ragbot/document/{document_id}/text - Get document text
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
import os

from app.services.safety_scanner import SafetyScanner, SafetyScanResult
from app.services.document_processor import DocumentProcessor
from app.services.observability import ObservabilityService
from app.services.zerodb_integration import ZeroDBService

router = APIRouter(prefix="/api/v1/ragbot", tags=["ragbot"])

# Pydantic Models
class DocumentMetadata(BaseModel):
    source_org: str
    canonical_url: HttpUrl
    license: str
    year: int
    content_type: str
    author: Optional[str] = None
    title: Optional[str] = None
    tags: Optional[List[str]] = None


class SafetyScanRequest(BaseModel):
    document_id: str
    text: str
    metadata: DocumentMetadata


class ChunkPreviewRequest(BaseModel):
    document_id: str


class PublishRequest(BaseModel):
    document_id: str
    namespace: str
    chunks: List[Dict[str, Any]]
    metadata: DocumentMetadata


class RejectRequest(BaseModel):
    document_id: str
    reason: Optional[str] = None


# Service Dependencies
def get_safety_scanner() -> SafetyScanner:
    return SafetyScanner()


def get_document_processor() -> DocumentProcessor:
    return DocumentProcessor()


def get_observability() -> ObservabilityService:
    return ObservabilityService()


def get_zerodb() -> ZeroDBService:
    return ZeroDBService()


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    doc_processor: DocumentProcessor = Depends(get_document_processor),
    observability: ObservabilityService = Depends(get_observability),
):
    """
    Upload a document for curation.

    Accepts: PDF, TXT, MD, DOCX (max 50MB)
    Returns: document_id for tracking
    """
    try:
        # Validate file type
        allowed_types = ["application/pdf", "text/plain", "text/markdown",
                        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]
        if file.content_type not in allowed_types and not file.filename.endswith(('.pdf', '.txt', '.md', '.docx')):
            raise HTTPException(status_code=400, detail="Invalid file type")

        # Validate file size (50MB)
        contents = await file.read()
        if len(contents) > 50 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File exceeds 50MB limit")

        # Generate document ID
        document_id = str(uuid.uuid4())

        # Save file temporarily
        upload_dir = "/tmp/ragbot_uploads"
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, f"{document_id}_{file.filename}")

        with open(file_path, "wb") as f:
            f.write(contents)

        # Track upload metrics
        await observability.track_upload(
            document_id=document_id,
            file_size=len(contents),
            file_type=file.content_type,
            filename=file.filename,
        )

        return {
            "document_id": document_id,
            "filename": file.filename,
            "size": len(contents),
            "status": "uploaded",
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/scan-safety")
async def scan_safety(
    request: SafetyScanRequest,
    safety_scanner: SafetyScanner = Depends(get_safety_scanner),
    observability: ObservabilityService = Depends(get_observability),
):
    """
    Run safety scan on document text.

    Detects:
    - PII (emails, phones, SSNs, credit cards)
    - Harmful content (hate speech, violence, etc.)
    """
    try:
        # Run safety scan
        scan_result = await safety_scanner.scan(request.text)

        # Track safety scan metrics
        await observability.track_safety_scan(
            document_id=request.document_id,
            pii_matches=len(scan_result.pii_matches),
            moderation_flags=len([r for r in scan_result.moderation_results if r.detected]),
        )

        return {
            "document_id": request.document_id,
            "pii_matches": scan_result.pii_matches,
            "moderation_results": scan_result.moderation_results,
            "scan_timestamp": datetime.utcnow().isoformat(),
            "passed": scan_result.passed,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/document/{document_id}/text")
async def get_document_text(
    document_id: str,
    doc_processor: DocumentProcessor = Depends(get_document_processor),
):
    """Get extracted text from uploaded document."""
    try:
        text = await doc_processor.extract_text(document_id)
        return {"document_id": document_id, "text": text}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Document not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chunk-preview")
async def chunk_preview(
    request: ChunkPreviewRequest,
    doc_processor: DocumentProcessor = Depends(get_document_processor),
    observability: ObservabilityService = Depends(get_observability),
):
    """
    Generate and preview document chunks.

    Returns chunks with embeddings and metadata.
    """
    try:
        start_time = datetime.utcnow()

        # Generate chunks
        chunks = await doc_processor.generate_chunks(request.document_id)

        # Track chunking metrics
        duration = (datetime.utcnow() - start_time).total_seconds() * 1000
        await observability.track_chunk_generation(
            document_id=request.document_id,
            chunk_count=len(chunks),
            duration_ms=duration,
        )

        return {
            "document_id": request.document_id,
            "chunks": chunks,
            "chunk_count": len(chunks),
            "generation_time_ms": duration,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/publish")
async def publish_document(
    request: PublishRequest,
    zerodb: ZeroDBService = Depends(get_zerodb),
    observability: ObservabilityService = Depends(get_observability),
):
    """
    Publish document chunks to ZeroDB.

    Stores vectors with provenance metadata in specified namespace.
    """
    try:
        start_time = datetime.utcnow()

        # Publish to ZeroDB
        result = await zerodb.publish_chunks(
            document_id=request.document_id,
            namespace=request.namespace,
            chunks=request.chunks,
            metadata=request.metadata.dict(),
        )

        # Track publication
        duration = (datetime.utcnow() - start_time).total_seconds() * 1000
        await observability.track_curator_action(
            action="publish",
            document_id=request.document_id,
            namespace=request.namespace,
            chunk_count=len(request.chunks),
        )

        return {
            "document_id": request.document_id,
            "namespace": request.namespace,
            "vectors_created": result["vector_count"],
            "status": "published",
            "duration_ms": duration,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reject")
async def reject_document(
    request: RejectRequest,
    observability: ObservabilityService = Depends(get_observability),
):
    """
    Reject document and clean up temporary files.
    """
    try:
        # Clean up temporary files
        upload_dir = "/tmp/ragbot_uploads"
        for filename in os.listdir(upload_dir):
            if filename.startswith(request.document_id):
                os.remove(os.path.join(upload_dir, filename))

        # Track rejection
        await observability.track_curator_action(
            action="reject",
            document_id=request.document_id,
            reason=request.reason,
        )

        return {
            "document_id": request.document_id,
            "status": "rejected",
            "reason": request.reason,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics")
async def get_metrics(
    observability: ObservabilityService = Depends(get_observability),
):
    """
    Get ingestion pipeline metrics.

    Returns:
    - Upload counts
    - Safety scan statistics
    - Chunk generation stats
    - Curator actions
    """
    try:
        metrics = await observability.get_pipeline_metrics()
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
