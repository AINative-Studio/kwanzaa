"""Metadata-first ingestion pipeline for Kwanzaa First Fruits corpus.

This module implements a robust, idempotent ingestion pipeline that:
1. Reads First Fruits manifest
2. Ingests metadata + short snippets first
3. Stores immediately in ZeroDB
4. Enables search + provenance UI functionality

Following data engineering best practices:
- Idempotent operations
- Comprehensive error handling
- Retry logic with exponential backoff
- Data quality validation
- Progress tracking and logging
- Batch processing for efficiency
"""

import hashlib
import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

logger = logging.getLogger(__name__)


class Priority(str, Enum):
    """Source priority levels."""

    P0 = "P0"  # High priority - full text expansion
    P1 = "P1"  # Medium priority - metadata only
    P2 = "P2"  # Low priority - metadata only


class AccessMethod(str, Enum):
    """Source access methods."""

    API = "api"
    BULK = "bulk"
    ALLOWED_SCRAPE = "allowed_scrape"


class SourceType(str, Enum):
    """Source types for provenance tracking."""

    GOVERNMENT = "government"
    UNIVERSITY = "university"
    LIBRARY = "library"
    MUSEUM = "museum"
    ARCHIVE = "archive"
    PRESS = "press"
    NONPROFIT = "nonprofit"
    PUBLISHER = "publisher"


class ContentType(str, Enum):
    """Content types for metadata classification."""

    SPEECH = "speech"
    LETTER = "letter"
    PROCLAMATION = "proclamation"
    NEWSPAPER_ARTICLE = "newspaper_article"
    JOURNAL_ARTICLE = "journal_article"
    BOOK_EXCERPT = "book_excerpt"
    BIOGRAPHY = "biography"
    TIMELINE_ENTRY = "timeline_entry"
    CURRICULUM = "curriculum"
    DATASET_DOC = "dataset_doc"
    DEV_DOC = "dev_doc"


class IngestionStatus(str, Enum):
    """Ingestion status tracking."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class ProvenanceMetadata:
    """Provenance metadata for data lineage tracking."""

    source_type: SourceType
    access_method: AccessMethod
    source_id: str
    source_url: str
    retrieved_at: str
    license: str
    hash: str


@dataclass
class DocumentMetadata:
    """Document-level metadata before chunking."""

    doc_id: str
    title: str
    source_org: str
    collection: str
    canonical_url: str
    license: str
    year: Optional[int]
    content_type: ContentType
    authors: List[str]
    retrieved_at: str
    access_method: AccessMethod
    priority: Priority
    tags: List[str]
    snippet: str  # Short text snippet for metadata-first ingestion

    # Optional fields
    subtitle: Optional[str] = None
    publisher: Optional[str] = None
    place: Optional[str] = None
    language: str = "en"
    abstract: Optional[str] = None
    rights_url: Optional[str] = None
    source_query: Optional[str] = None
    source_id: Optional[str] = None
    checksum: Optional[str] = None


@dataclass
class ChunkMetadata:
    """Chunk-level metadata for embedding and retrieval."""

    chunk_id: str
    doc_id: str
    chunk_index: int
    text: str
    source_org: str
    collection: str
    record_id: str
    canonical_url: str
    license: str
    year: Optional[int]
    content_type: ContentType
    retrieved_at: str
    namespace: str
    citation_label: str
    provenance: ProvenanceMetadata


@dataclass
class IngestionStats:
    """Statistics tracking for ingestion runs."""

    run_id: str
    started_at: str
    completed_at: Optional[str] = None
    total_sources: int = 0
    sources_processed: int = 0
    sources_failed: int = 0
    total_documents: int = 0
    documents_inserted: int = 0
    documents_updated: int = 0
    documents_failed: int = 0
    errors: List[Dict[str, Any]] = field(default_factory=list)

    def add_error(self, source_id: str, error_type: str, error_message: str) -> None:
        """Add an error to the tracking list."""
        self.errors.append({
            "source_id": source_id,
            "error_type": error_type,
            "error_message": error_message,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })


class ValidationError(Exception):
    """Raised when data validation fails."""

    pass


class IngestionError(Exception):
    """Base exception for ingestion pipeline errors."""

    pass


class MetadataValidator:
    """Validates metadata against schema requirements."""

    REQUIRED_DOC_FIELDS = [
        "doc_id",
        "title",
        "source_org",
        "collection",
        "canonical_url",
        "license",
        "content_type",
        "retrieved_at",
        "access_method",
        "priority",
    ]

    REQUIRED_PROVENANCE_FIELDS = [
        "source_type",
        "access_method",
        "source_id",
        "source_url",
        "retrieved_at",
        "license",
        "hash",
    ]

    @classmethod
    def validate_document_metadata(cls, doc: Dict[str, Any]) -> None:
        """Validate document metadata completeness.

        Args:
            doc: Document metadata dictionary

        Raises:
            ValidationError: If validation fails
        """
        # Check required fields
        missing_fields = [
            field for field in cls.REQUIRED_DOC_FIELDS if field not in doc
        ]
        if missing_fields:
            raise ValidationError(
                f"Missing required fields: {', '.join(missing_fields)}"
            )

        # Validate field types and values
        if not doc.get("title") or not doc["title"].strip():
            raise ValidationError("Title cannot be empty")

        if not doc.get("canonical_url") or not doc["canonical_url"].startswith("http"):
            raise ValidationError("Invalid canonical_url")

        if not doc.get("license") or not doc["license"].strip():
            raise ValidationError("License cannot be empty")

        # Validate content_type
        try:
            ContentType(doc["content_type"])
        except (ValueError, KeyError):
            raise ValidationError(
                f"Invalid content_type: {doc.get('content_type')}. "
                f"Must be one of: {[ct.value for ct in ContentType]}"
            )

        # Validate year if present
        if doc.get("year") is not None:
            try:
                year = int(doc["year"])
                if year < 1500 or year > datetime.now().year + 1:
                    raise ValidationError(f"Year {year} is out of valid range")
            except (ValueError, TypeError):
                raise ValidationError(f"Invalid year value: {doc.get('year')}")

        logger.debug(f"Document metadata validation passed: {doc['doc_id']}")

    @classmethod
    def validate_provenance(cls, provenance: Dict[str, Any]) -> None:
        """Validate provenance metadata completeness.

        Args:
            provenance: Provenance metadata dictionary

        Raises:
            ValidationError: If validation fails
        """
        missing_fields = [
            field for field in cls.REQUIRED_PROVENANCE_FIELDS if field not in provenance
        ]
        if missing_fields:
            raise ValidationError(
                f"Missing required provenance fields: {', '.join(missing_fields)}"
            )

        # Validate source_type
        try:
            SourceType(provenance["source_type"])
        except (ValueError, KeyError):
            raise ValidationError(
                f"Invalid source_type: {provenance.get('source_type')}"
            )

        logger.debug(f"Provenance validation passed for source: {provenance['source_id']}")


class MetadataIngestionPipeline:
    """Metadata-first ingestion pipeline with idempotent operations."""

    def __init__(
        self,
        manifest_path: Path,
        zerodb_client: Any,  # ZeroDB MCP client
        batch_size: int = 100,
        max_retries: int = 3,
    ):
        """Initialize the ingestion pipeline.

        Args:
            manifest_path: Path to First Fruits manifest JSON
            zerodb_client: ZeroDB MCP client for storage operations
            batch_size: Batch size for bulk operations
            max_retries: Maximum retry attempts for failed operations
        """
        self.manifest_path = manifest_path
        self.zerodb_client = zerodb_client
        self.batch_size = batch_size
        self.max_retries = max_retries
        self.validator = MetadataValidator()

        # Generate unique run ID
        self.run_id = self._generate_run_id()
        self.stats = IngestionStats(
            run_id=self.run_id,
            started_at=datetime.now(timezone.utc).isoformat(),
        )

        # Track processed documents to ensure idempotency
        self.processed_doc_ids: Set[str] = set()

    def _generate_run_id(self) -> str:
        """Generate unique run ID for tracking."""
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        return f"ingestion_run_{timestamp}"

    def _compute_hash(self, content: str) -> str:
        """Compute SHA-256 hash of content for deduplication.

        Args:
            content: Content to hash

        Returns:
            Hex-encoded SHA-256 hash
        """
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def load_manifest(self) -> Dict[str, Any]:
        """Load and validate manifest file.

        Returns:
            Manifest data dictionary

        Raises:
            IngestionError: If manifest loading fails
        """
        try:
            logger.info(f"Loading manifest from: {self.manifest_path}")
            with open(self.manifest_path, "r", encoding="utf-8") as f:
                manifest = json.load(f)

            # Validate manifest structure
            if "sources" not in manifest:
                raise IngestionError("Manifest missing 'sources' field")

            if not isinstance(manifest["sources"], list):
                raise IngestionError("Manifest 'sources' must be a list")

            self.stats.total_sources = len(manifest["sources"])
            logger.info(
                f"Manifest loaded successfully: {len(manifest['sources'])} sources"
            )
            return manifest

        except FileNotFoundError:
            raise IngestionError(f"Manifest file not found: {self.manifest_path}")
        except json.JSONDecodeError as e:
            raise IngestionError(f"Invalid JSON in manifest: {e}")
        except Exception as e:
            raise IngestionError(f"Failed to load manifest: {e}")

    def _generate_doc_id(self, source_id: str, record_id: str) -> str:
        """Generate stable document ID.

        Args:
            source_id: Source identifier
            record_id: Record identifier

        Returns:
            Stable document ID
        """
        # Ensure doc_id is stable across runs
        return f"{source_id}::{record_id}"

    def _generate_citation_label(
        self, source_org: str, year: Optional[int], title: str
    ) -> str:
        """Generate citation label for UI display.

        Args:
            source_org: Source organization
            year: Publication year
            title: Document title

        Returns:
            Formatted citation label
        """
        year_str = str(year) if year else "n.d."
        # Truncate title if too long
        truncated_title = title[:50] + "..." if len(title) > 50 else title
        return f"{source_org} ({year_str}). {truncated_title}"

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(Exception),
    )
    async def _store_document_batch(
        self,
        documents: List[Dict[str, Any]],
        table_name: str = "kw_documents",
    ) -> int:
        """Store batch of documents in ZeroDB with retry logic.

        Args:
            documents: List of document metadata dictionaries
            table_name: Target table name

        Returns:
            Number of documents successfully stored

        Raises:
            IngestionError: If storage fails after retries
        """
        try:
            logger.info(f"Storing batch of {len(documents)} documents to {table_name}")

            # Use ZeroDB MCP insert_rows for batch insert
            result = await self.zerodb_client.insert_rows(
                table_id=table_name,
                rows=documents,
                return_ids=True,
            )

            stored_count = len(result.get("inserted_ids", []))
            logger.info(f"Successfully stored {stored_count} documents")
            return stored_count

        except Exception as e:
            logger.error(f"Failed to store document batch: {e}")
            raise IngestionError(f"Storage failed: {e}") from e

    async def _ensure_tables_exist(self) -> None:
        """Ensure required ZeroDB tables exist with proper schemas.

        Raises:
            IngestionError: If table creation fails
        """
        try:
            # Check if kw_sources table exists
            sources_table = await self.zerodb_client.get_table(table_id="kw_sources")
            if not sources_table:
                logger.info("Creating kw_sources table")
                await self._create_sources_table()
            else:
                logger.info("kw_sources table already exists")

            # Check if kw_documents table exists
            docs_table = await self.zerodb_client.get_table(table_id="kw_documents")
            if not docs_table:
                logger.info("Creating kw_documents table")
                await self._create_documents_table()
            else:
                logger.info("kw_documents table already exists")

        except Exception as e:
            logger.warning(f"Table check/creation skipped: {e}")
            # Don't fail if tables already exist or can't be checked

    async def _create_sources_table(self) -> None:
        """Create kw_sources table for tracking ingestion sources."""
        schema = {
            "fields": {
                "source_id": {"type": "string", "required": True},
                "source_name": {"type": "string", "required": True},
                "source_type": {"type": "string", "required": True},
                "source_org": {"type": "string", "required": True},
                "base_url": {"type": "string", "required": True},
                "access_method": {"type": "string", "required": True},
                "license": {"type": "string", "required": True},
                "priority": {"type": "string", "required": True},
                "default_namespace": {"type": "string", "required": True},
                "tags": {"type": "array", "items": {"type": "string"}},
                "job_id": {"type": "string", "required": True},
                "schedule": {"type": "string"},
                "last_ingestion_run": {"type": "string"},
                "total_documents_ingested": {"type": "integer", "default": 0},
                "created_at": {"type": "string"},
                "updated_at": {"type": "string"},
            },
            "indexes": [
                {"fields": ["source_id"], "unique": True},
                {"fields": ["source_type"]},
                {"fields": ["priority"]},
            ],
        }

        await self.zerodb_client.create_table(
            table_name="kw_sources",
            schema=schema,
            description="Kwanzaa ingestion sources from First Fruits manifest",
        )
        logger.info("Created kw_sources table")

    async def _create_documents_table(self) -> None:
        """Create kw_documents table for document metadata storage."""
        schema = {
            "fields": {
                "doc_id": {"type": "string", "required": True},
                "title": {"type": "string", "required": True},
                "source_org": {"type": "string", "required": True},
                "collection": {"type": "string", "required": True},
                "canonical_url": {"type": "string", "required": True},
                "license": {"type": "string", "required": True},
                "year": {"type": "integer"},
                "content_type": {"type": "string", "required": True},
                "authors": {"type": "array", "items": {"type": "string"}},
                "retrieved_at": {"type": "string", "required": True},
                "access_method": {"type": "string", "required": True},
                "priority": {"type": "string", "required": True},
                "tags": {"type": "array", "items": {"type": "string"}},
                "snippet": {"type": "string"},
                "subtitle": {"type": "string"},
                "publisher": {"type": "string"},
                "place": {"type": "string"},
                "language": {"type": "string", "default": "en"},
                "abstract": {"type": "string"},
                "rights_url": {"type": "string"},
                "source_query": {"type": "string"},
                "source_id": {"type": "string"},
                "checksum": {"type": "string"},
                "namespace": {"type": "string"},
                "citation_label": {"type": "string"},
                "provenance": {"type": "object"},
                "ingestion_run_id": {"type": "string"},
                "created_at": {"type": "string"},
                "updated_at": {"type": "string"},
            },
            "indexes": [
                {"fields": ["doc_id"], "unique": True},
                {"fields": ["source_org"]},
                {"fields": ["content_type"]},
                {"fields": ["year"]},
                {"fields": ["namespace"]},
                {"fields": ["checksum"]},
            ],
        }

        await self.zerodb_client.create_table(
            table_name="kw_documents",
            schema=schema,
            description="Kwanzaa document metadata for First Fruits corpus",
        )
        logger.info("Created kw_documents table")

    async def process_source(self, source: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process a single source and extract document metadata.

        This is a placeholder that should be extended with actual API/bulk
        data fetching logic for each source type.

        Args:
            source: Source configuration from manifest

        Returns:
            List of document metadata dictionaries
        """
        source_id = source["source_id"]
        logger.info(f"Processing source: {source_id}")

        # For MVP, this creates example documents
        # In production, this would call actual APIs or read bulk data
        documents = []

        # Handle different manifest schema formats
        base_url = source.get("base_url") or source.get("canonical_url", "https://example.com")
        license_info = source.get("license") or source.get("license_info", "Unknown")

        # Map priority to P0/P1/P2 format if numeric
        priority = source.get("priority", "P0")
        if isinstance(priority, int):
            priority = f"P{priority}"

        # Determine default namespace based on source type
        default_namespace = source.get("default_namespace")
        if not default_namespace:
            source_type = source.get("source_type", "")
            if "primary_source" in source_type or source_type == "speech":
                default_namespace = "kwanzaa_primary_sources"
            elif "black_press" in source_type:
                default_namespace = "kwanzaa_black_press"
            else:
                default_namespace = "kwanzaa_primary_sources"

        # Map content type to valid ContentType enum
        content_type_raw = source.get("content_type", "dev_doc")
        content_type_map = {
            "manuscripts_letters_speeches": ContentType.LETTER.value,
            "speeches_transcripts": ContentType.SPEECH.value,
            "newspaper_articles": ContentType.NEWSPAPER_ARTICLE.value,
        }
        content_type = content_type_map.get(content_type_raw, ContentType.DEV_DOC.value)

        # Map source_type to valid SourceType enum
        source_type_raw = source.get("source_type", "archive")
        source_type_map = {
            "primary_source": SourceType.ARCHIVE.value,
            "speech": SourceType.ARCHIVE.value,
            "black_press": SourceType.PRESS.value,
            "government": SourceType.GOVERNMENT.value,
            "university": SourceType.UNIVERSITY.value,
            "library": SourceType.LIBRARY.value,
            "museum": SourceType.MUSEUM.value,
            "archive": SourceType.ARCHIVE.value,
            "nonprofit": SourceType.NONPROFIT.value,
            "publisher": SourceType.PUBLISHER.value,
        }
        mapped_source_type = source_type_map.get(source_type_raw, SourceType.ARCHIVE.value)

        # Example document creation (replace with real data fetching)
        example_doc = {
            "doc_id": self._generate_doc_id(source_id, "example_001"),
            "title": f"Example Document from {source['source_name']}",
            "source_org": source["source_org"],
            "collection": source["source_name"],
            "canonical_url": f"{base_url}/example_001",
            "license": license_info,
            "year": source.get("year") or 2020,
            "content_type": content_type,
            "authors": ["Unknown"],
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
            "access_method": source["access_method"],
            "priority": priority,
            "tags": source.get("tags", []),
            "snippet": f"Snippet from {source['source_name']}: {source.get('metadata', {}).get('description', 'No description available.')}",
            "language": "en",
            "namespace": default_namespace,
            "citation_label": self._generate_citation_label(
                source["source_org"], source.get("year") or 2020, f"Example from {source['source_name']}"
            ),
            "provenance": {
                "source_type": mapped_source_type,
                "access_method": source["access_method"],
                "source_id": source_id,
                "source_url": base_url,
                "retrieved_at": datetime.now(timezone.utc).isoformat(),
                "license": license_info,
                "hash": self._compute_hash(f"example content from {source_id}"),
            },
            "source_id": source_id,
            "checksum": self._compute_hash(f"example content from {source_id}"),
            "ingestion_run_id": self.run_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

        # Validate before adding
        try:
            self.validator.validate_document_metadata(example_doc)
            self.validator.validate_provenance(example_doc["provenance"])
            documents.append(example_doc)
        except ValidationError as e:
            logger.error(f"Validation failed for document: {e}")
            self.stats.add_error(source_id, "validation_error", str(e))

        logger.info(f"Extracted {len(documents)} documents from {source_id}")
        return documents

    async def run(self) -> IngestionStats:
        """Run the complete metadata ingestion pipeline.

        Returns:
            IngestionStats with ingestion results

        Raises:
            IngestionError: If pipeline execution fails
        """
        try:
            logger.info(f"Starting metadata ingestion run: {self.run_id}")

            # Load manifest
            manifest = self.load_manifest()

            # Ensure tables exist
            await self._ensure_tables_exist()

            # Process each source
            all_documents = []
            for source in manifest["sources"]:
                source_id = source["source_id"]

                try:
                    logger.info(f"Processing source: {source_id}")
                    documents = await self.process_source(source)

                    # Filter out already processed documents (idempotency)
                    new_documents = [
                        doc for doc in documents
                        if doc["doc_id"] not in self.processed_doc_ids
                    ]

                    if new_documents:
                        all_documents.extend(new_documents)
                        self.processed_doc_ids.update(doc["doc_id"] for doc in new_documents)
                        self.stats.total_documents += len(new_documents)

                    self.stats.sources_processed += 1
                    logger.info(
                        f"Source {source_id} processed: {len(new_documents)} new documents"
                    )

                except Exception as e:
                    logger.error(f"Failed to process source {source_id}: {e}")
                    self.stats.sources_failed += 1
                    self.stats.add_error(source_id, "processing_error", str(e))
                    continue

            # Store documents in batches
            if all_documents:
                logger.info(f"Storing {len(all_documents)} documents in batches")

                for i in range(0, len(all_documents), self.batch_size):
                    batch = all_documents[i : i + self.batch_size]

                    try:
                        stored_count = await self._store_document_batch(batch)
                        self.stats.documents_inserted += stored_count
                    except Exception as e:
                        logger.error(f"Failed to store batch: {e}")
                        self.stats.documents_failed += len(batch)
                        self.stats.add_error(
                            "batch_storage", "storage_error", str(e)
                        )

            # Finalize stats
            self.stats.completed_at = datetime.now(timezone.utc).isoformat()

            logger.info(f"Ingestion run completed: {self.run_id}")
            logger.info(f"Sources processed: {self.stats.sources_processed}/{self.stats.total_sources}")
            logger.info(f"Documents inserted: {self.stats.documents_inserted}")
            logger.info(f"Documents failed: {self.stats.documents_failed}")
            logger.info(f"Errors: {len(self.stats.errors)}")

            return self.stats

        except Exception as e:
            logger.error(f"Ingestion pipeline failed: {e}")
            self.stats.completed_at = datetime.now(timezone.utc).isoformat()
            raise IngestionError(f"Pipeline execution failed: {e}") from e

    def export_stats(self, output_path: Path) -> None:
        """Export ingestion statistics to JSON file.

        Args:
            output_path: Path to output JSON file
        """
        stats_dict = {
            "run_id": self.stats.run_id,
            "started_at": self.stats.started_at,
            "completed_at": self.stats.completed_at,
            "total_sources": self.stats.total_sources,
            "sources_processed": self.stats.sources_processed,
            "sources_failed": self.stats.sources_failed,
            "total_documents": self.stats.total_documents,
            "documents_inserted": self.stats.documents_inserted,
            "documents_updated": self.stats.documents_updated,
            "documents_failed": self.stats.documents_failed,
            "errors": self.stats.errors,
        }

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(stats_dict, f, indent=2)

        logger.info(f"Stats exported to: {output_path}")
