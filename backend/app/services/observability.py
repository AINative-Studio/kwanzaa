"""
Observability Service

Tracks metrics for ingestion pipeline monitoring.
Required by Issue #38 - Observability
"""

from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import json


class ObservabilityService:
    """Track and report ingestion pipeline metrics."""

    def __init__(self):
        self.metrics = defaultdict(list)

    async def track_upload(
        self,
        document_id: str,
        file_size: int,
        file_type: str,
        filename: str,
    ):
        """Track file upload event."""
        self.metrics["uploads"].append({
            "timestamp": datetime.utcnow().isoformat(),
            "document_id": document_id,
            "file_size": file_size,
            "file_type": file_type,
            "filename": filename,
        })

    async def track_safety_scan(
        self,
        document_id: str,
        pii_matches: int,
        moderation_flags: int,
    ):
        """Track safety scan metrics."""
        self.metrics["safety_scans"].append({
            "timestamp": datetime.utcnow().isoformat(),
            "document_id": document_id,
            "pii_matches": pii_matches,
            "moderation_flags": moderation_flags,
        })

    async def track_chunk_generation(
        self,
        document_id: str,
        chunk_count: int,
        duration_ms: float,
    ):
        """Track chunking metrics."""
        self.metrics["chunk_generation"].append({
            "timestamp": datetime.utcnow().isoformat(),
            "document_id": document_id,
            "chunk_count": chunk_count,
            "duration_ms": duration_ms,
        })

    async def track_curator_action(
        self,
        action: str,
        document_id: str,
        **kwargs,
    ):
        """Track curator actions (publish, reject, edit)."""
        self.metrics["curator_actions"].append({
            "timestamp": datetime.utcnow().isoformat(),
            "action": action,
            "document_id": document_id,
            **kwargs,
        })

    async def get_pipeline_metrics(self) -> Dict[str, Any]:
        """Get aggregated pipeline metrics."""
        now = datetime.utcnow()
        last_24h = now - timedelta(hours=24)

        return {
            "total_uploads": len(self.metrics["uploads"]),
            "total_safety_scans": len(self.metrics["safety_scans"]),
            "total_chunks_generated": sum(
                m["chunk_count"] for m in self.metrics["chunk_generation"]
            ),
            "curator_actions": {
                "publish": len([a for a in self.metrics["curator_actions"] if a["action"] == "publish"]),
                "reject": len([a for a in self.metrics["curator_actions"] if a["action"] == "reject"]),
            },
            "avg_chunk_generation_time_ms": (
                sum(m["duration_ms"] for m in self.metrics["chunk_generation"]) /
                len(self.metrics["chunk_generation"])
                if self.metrics["chunk_generation"] else 0
            ),
            "pii_detection_rate": (
                sum(m["pii_matches"] > 0 for m in self.metrics["safety_scans"]) /
                len(self.metrics["safety_scans"])
                if self.metrics["safety_scans"] else 0
            ),
        }
