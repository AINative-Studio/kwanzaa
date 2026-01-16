"""Ingestion tracking models and schemas."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class IngestionStatus(str, Enum):
    """Status of an ingestion run."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"


class IngestionPhase(str, Enum):
    """Phases of the ingestion pipeline."""

    DISCOVER = "discover"
    NORMALIZE = "normalize"
    STORE_METADATA = "store_metadata"
    EXPAND_FULLTEXT = "expand_fulltext"
    COMPLETE = "complete"


class IngestionRunMetadata(BaseModel):
    """Metadata for tracking ingestion runs."""

    run_id: str = Field(..., description="Unique identifier for this run")
    environment: str = Field(..., description="Environment: dev, staging, prod")
    triggered_by: str = Field(..., description="How the job was triggered: scheduled, manual, webhook")

    started_at: datetime = Field(..., description="When the run started")
    completed_at: Optional[datetime] = Field(None, description="When the run completed")

    status: IngestionStatus = Field(..., description="Current status of the run")
    current_phase: IngestionPhase = Field(..., description="Current phase of pipeline")

    manifest_version: str = Field(..., description="Version/hash of manifest used")
    manifest_sources: List[str] = Field(default_factory=list, description="Source names from manifest")

    # Statistics
    documents_discovered: int = Field(default=0, description="Total documents discovered")
    documents_processed: int = Field(default=0, description="Documents successfully processed")
    documents_failed: int = Field(default=0, description="Documents that failed processing")
    documents_skipped: int = Field(default=0, description="Documents skipped (duplicates/unchanged)")

    chunks_created: int = Field(default=0, description="Total chunks created")
    vectors_upserted: int = Field(default=0, description="Total vectors stored")

    # Errors and warnings
    errors: List[Dict[str, Any]] = Field(default_factory=list, description="List of errors encountered")
    warnings: List[str] = Field(default_factory=list, description="List of warnings")

    # Source-level tracking
    source_status: Dict[str, Dict[str, Any]] = Field(
        default_factory=dict,
        description="Status per source: {source_name: {status, count, errors}}"
    )

    # Configuration
    config_snapshot: Dict[str, Any] = Field(default_factory=dict, description="Snapshot of config used")

    # Resource usage
    duration_seconds: Optional[float] = Field(None, description="Total run duration in seconds")
    peak_memory_mb: Optional[float] = Field(None, description="Peak memory usage in MB")

    # Notifications
    notifications_sent: List[str] = Field(default_factory=list, description="Notification channels used")

    class Config:
        """Pydantic config."""

        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }


class IngestionSourceMetadata(BaseModel):
    """Metadata for a source in the manifest."""

    source_name: str = Field(..., description="Unique source identifier")
    source_type: str = Field(..., description="Type of source: archive, press, academic, etc.")
    base_url: str = Field(..., description="Base URL for the source")
    access_method: str = Field(..., description="How to access: api, bulk, allowed_scrape")
    license: str = Field(..., description="License for the content")
    priority: str = Field(..., description="P0, P1, or P2")
    default_namespace: str = Field(..., description="Target ZeroDB namespace")
    tags: List[str] = Field(default_factory=list, description="Categorization tags")

    # Processing configuration
    enabled: bool = Field(default=True, description="Whether this source is enabled")
    schedule: str = Field(default="daily", description="Processing schedule")
    rate_limit_per_second: Optional[float] = Field(None, description="Rate limit for this source")

    # State tracking
    last_processed_at: Optional[datetime] = Field(None, description="Last successful processing")
    last_run_id: Optional[str] = Field(None, description="Last run ID")
    last_record_id: Optional[str] = Field(None, description="Last record ID processed")
    checksum: Optional[str] = Field(None, description="Checksum for change detection")

    # Query templates
    query_templates: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Query templates for discovery"
    )

    # Metadata mapping
    fields_mapping: Optional[Dict[str, str]] = Field(
        None,
        description="Source field to canonical field mapping"
    )


class IngestionManifest(BaseModel):
    """Complete ingestion manifest."""

    version: str = Field(..., description="Manifest version")
    created_at: datetime = Field(..., description="When manifest was created")
    updated_at: datetime = Field(..., description="Last update timestamp")

    sources: List[IngestionSourceMetadata] = Field(..., description="List of sources to ingest")

    # Global settings
    global_config: Dict[str, Any] = Field(
        default_factory=dict,
        description="Global configuration options"
    )

    # Namespace definitions
    namespaces: Dict[str, Dict[str, Any]] = Field(
        default_factory=dict,
        description="Namespace configurations"
    )


class NotificationConfig(BaseModel):
    """Configuration for job notifications."""

    enabled: bool = Field(default=True, description="Whether notifications are enabled")

    # Channels
    email_enabled: bool = Field(default=False, description="Send email notifications")
    email_recipients: List[str] = Field(default_factory=list, description="Email addresses")

    webhook_enabled: bool = Field(default=False, description="Send webhook notifications")
    webhook_url: Optional[str] = Field(None, description="Webhook endpoint URL")

    slack_enabled: bool = Field(default=False, description="Send Slack notifications")
    slack_webhook_url: Optional[str] = Field(None, description="Slack webhook URL")

    # Notification rules
    notify_on_success: bool = Field(default=True, description="Notify on successful runs")
    notify_on_failure: bool = Field(default=True, description="Notify on failures")
    notify_on_partial: bool = Field(default=True, description="Notify on partial success")

    # Thresholds
    error_threshold: int = Field(default=10, description="Max errors before notification")
    warning_threshold: int = Field(default=50, description="Max warnings before notification")


class JobConfiguration(BaseModel):
    """Configuration for the ingestion job."""

    environment: str = Field(..., description="Environment: dev, staging, prod")

    # Scheduling
    schedule_cron: str = Field(default="0 2 * * *", description="Cron schedule (default: 2 AM UTC daily)")
    enabled: bool = Field(default=True, description="Whether scheduled runs are enabled")

    # Processing options
    incremental: bool = Field(default=True, description="Use incremental processing")
    full_refresh: bool = Field(default=False, description="Force full refresh (ignore checkpoints)")
    parallel_sources: int = Field(default=1, description="Number of sources to process in parallel")

    # Resource limits
    max_duration_minutes: int = Field(default=120, description="Maximum run duration")
    max_memory_mb: int = Field(default=4096, description="Maximum memory usage")

    # Retry configuration
    max_retries: int = Field(default=3, description="Max retries per source")
    retry_delay_seconds: int = Field(default=60, description="Delay between retries")

    # Notification settings
    notifications: NotificationConfig = Field(default_factory=NotificationConfig)

    # Monitoring
    healthcheck_url: Optional[str] = Field(None, description="URL to ping for health checks")
    metrics_enabled: bool = Field(default=True, description="Enable metrics collection")
