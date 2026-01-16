"""SQLAlchemy ORM models for Kwanzaa database tables.

This module defines the core database schema for:
- sources: Source manifest registry
- documents: Document-level records with provenance
- chunks: Chunk-level records linked to vector embeddings
- collections: Namespace/collection groupings
- ingestion_logs: Ingestion job tracking
- evaluations: Evaluation results and metrics
"""

from datetime import datetime
from typing import Optional
from uuid import uuid4

from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


class Source(Base):
    """Source manifest registry tracking all data sources.

    This table stores information about where data comes from, including
    licensing, access methods, and prioritization.
    """

    __tablename__ = "sources"

    # Primary key
    source_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    # Required fields
    source_name = Column(String(255), nullable=False, unique=True, index=True)
    source_type = Column(
        String(50),
        nullable=False,
        index=True,
        comment="Type: government, press, archive, academic, museum, community, other",
    )
    canonical_url = Column(String(500), nullable=False)
    license = Column(String(255), nullable=False)
    access_method = Column(
        String(50),
        nullable=False,
        comment="How data is accessed: api, scrape, manual, download",
    )

    # Optional fields
    priority = Column(
        Integer,
        nullable=True,
        default=0,
        comment="Priority level for ingestion (0=lowest, 5=highest)",
    )
    tags = Column(ARRAY(String), nullable=True, default=list)

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = Column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    documents = relationship("Document", back_populates="source", cascade="all, delete-orphan")

    # Constraints
    __table_args__ = (
        CheckConstraint("priority >= 0 AND priority <= 5", name="check_priority_range"),
        CheckConstraint(
            "source_type IN ('government', 'press', 'archive', 'academic', 'museum', 'community', 'other')",
            name="check_source_type",
        ),
        CheckConstraint(
            "access_method IN ('api', 'scrape', 'manual', 'download')",
            name="check_access_method",
        ),
    )


class Document(Base):
    """Document-level records with complete provenance metadata.

    Each document represents a single source document (speech, letter, etc.)
    with full provenance tracking as required by the Imani principle.
    """

    __tablename__ = "documents"

    # Primary key
    document_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    # Foreign keys
    source_id = Column(
        UUID(as_uuid=True),
        ForeignKey("sources.source_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Required provenance fields (Imani - Faith in provenance)
    canonical_url = Column(String(500), nullable=False, unique=True, index=True)
    source_org = Column(String(255), nullable=False, index=True)
    year = Column(Integer, nullable=False, index=True)
    content_type = Column(
        String(50),
        nullable=False,
        index=True,
        comment="Type: speech, letter, document, article, book, interview, multimedia, other",
    )
    license = Column(String(255), nullable=False)

    # Optional fields
    title = Column(String(500), nullable=True)
    full_text = Column(Text, nullable=True)
    extra_metadata = Column(JSONB, nullable=True, default=dict)

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = Column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    source = relationship("Source", back_populates="documents")
    chunks = relationship("Chunk", back_populates="document", cascade="all, delete-orphan")

    # Constraints
    __table_args__ = (
        CheckConstraint("year >= 1600 AND year <= 2100", name="check_year_range"),
        CheckConstraint(
            "content_type IN ('speech', 'letter', 'document', 'article', 'book', 'interview', 'multimedia', 'other')",
            name="check_content_type",
        ),
        Index("idx_document_year_content", "year", "content_type"),
    )


class Chunk(Base):
    """Chunk-level records linked to vector embeddings.

    Each chunk represents a portion of a document that has been embedded
    and stored in the ZeroDB vector store. This table maintains the link
    between the vector ID and the document metadata.
    """

    __tablename__ = "chunks"

    # Primary key
    chunk_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    # Foreign keys
    document_id = Column(
        UUID(as_uuid=True),
        ForeignKey("documents.document_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Required fields
    chunk_index = Column(Integer, nullable=False)
    chunk_text = Column(Text, nullable=False)
    citation_label = Column(String(500), nullable=False)
    namespace = Column(
        String(100),
        nullable=False,
        index=True,
        comment="Namespace: founding, core_texts, speeches, letters, multimedia, supplemental",
    )

    # Optional fields
    vector_id = Column(
        String(255),
        nullable=True,
        index=True,
        comment="Reference to vector embedding in ZeroDB",
    )
    retrieved_at = Column(
        DateTime,
        nullable=True,
        comment="Timestamp when chunk was last retrieved/accessed",
    )
    provenance_metadata = Column(
        JSONB,
        nullable=False,
        default=dict,
        comment="Complete provenance metadata (canonical_url, license, year, source_org, content_type, etc.)",
    )

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = Column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    document = relationship("Document", back_populates="chunks")

    # Constraints
    __table_args__ = (
        CheckConstraint("chunk_index >= 0", name="check_chunk_index_positive"),
        CheckConstraint(
            "namespace IN ('founding', 'core_texts', 'speeches', 'letters', 'multimedia', 'supplemental')",
            name="check_namespace",
        ),
        Index("idx_chunk_document_index", "document_id", "chunk_index", unique=True),
        Index("idx_chunk_namespace_vector", "namespace", "vector_id"),
    )


class Collection(Base):
    """Collections and namespace groupings.

    This table defines the 6-namespace strategy for organizing content:
    founding, core_texts, speeches, letters, multimedia, supplemental
    """

    __tablename__ = "collections"

    # Primary key
    collection_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    # Required fields
    collection_name = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)

    # Optional fields
    default_threshold = Column(
        Float,
        nullable=True,
        comment="Default similarity threshold for semantic search (0.0 to 1.0)",
    )

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = Column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "default_threshold IS NULL OR (default_threshold >= 0.0 AND default_threshold <= 1.0)",
            name="check_threshold_range",
        ),
    )


class IngestionLog(Base):
    """Ingestion job tracking with run metrics and error tracking.

    This table provides audit trail for all ingestion operations,
    supporting the Ujima (Collective Work) principle through transparency.
    """

    __tablename__ = "ingestion_logs"

    # Primary key
    run_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    # Required fields
    source_name = Column(String(255), nullable=False, index=True)
    started_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    status = Column(
        String(50),
        nullable=False,
        index=True,
        comment="Status: running, completed, failed, partial",
    )

    # Optional fields
    completed_at = Column(DateTime, nullable=True)
    documents_processed = Column(Integer, nullable=True, default=0)
    chunks_created = Column(Integer, nullable=True, default=0)
    errors = Column(
        JSONB,
        nullable=True,
        default=list,
        comment="Array of error objects encountered during ingestion",
    )
    run_metadata = Column(
        JSONB,
        nullable=True,
        default=dict,
        comment="Additional run metadata and configuration",
    )

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "status IN ('running', 'completed', 'failed', 'partial')",
            name="check_status",
        ),
        CheckConstraint(
            "documents_processed IS NULL OR documents_processed >= 0",
            name="check_documents_processed",
        ),
        CheckConstraint(
            "chunks_created IS NULL OR chunks_created >= 0",
            name="check_chunks_created",
        ),
        Index("idx_ingestion_source_status", "source_name", "status"),
        Index("idx_ingestion_started", "started_at", postgresql_ops={"started_at": "DESC"}),
    )


class Evaluation(Base):
    """Evaluation results and metrics.

    This table stores evaluation results for testing RAG quality,
    citation coverage, hallucination detection, and other metrics.
    """

    __tablename__ = "evaluations"

    # Primary key
    eval_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    # Required fields
    eval_type = Column(
        String(100),
        nullable=False,
        index=True,
        comment="Type: citation_coverage, refusal_accuracy, hallucination, retrieval_quality, answer_quality, other",
    )
    run_date = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    metrics = Column(
        JSONB,
        nullable=False,
        comment="Evaluation metrics (accuracy, precision, recall, F1, etc.)",
    )
    test_cases = Column(Integer, nullable=False)
    passed = Column(Integer, nullable=False)
    failed = Column(Integer, nullable=False)

    # Optional fields
    model_name = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Constraints
    __table_args__ = (
        CheckConstraint("test_cases >= 0", name="check_test_cases"),
        CheckConstraint("passed >= 0", name="check_passed"),
        CheckConstraint("failed >= 0", name="check_failed"),
        CheckConstraint(
            "passed + failed <= test_cases",
            name="check_passed_failed_sum",
        ),
        CheckConstraint(
            "eval_type IN ('citation_coverage', 'refusal_accuracy', 'hallucination', 'retrieval_quality', 'answer_quality', 'other')",
            name="check_eval_type",
        ),
        Index("idx_evaluation_type_date", "eval_type", "run_date"),
    )
