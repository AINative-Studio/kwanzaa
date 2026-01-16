"""Manifest loader for First Fruits data sources.

This module handles loading and filtering of the FirstFruitsManifest,
which contains metadata about available data sources and their priorities.
"""

import json
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class SourceType(str, Enum):
    """Source type enumeration."""

    PRIMARY_SOURCE = "primary_source"
    BLACK_PRESS = "black_press"
    SPEECH = "speech"
    LETTER = "letter"
    TEACHING_KIT = "teaching_kit"
    ACADEMIC_PAPER = "academic_paper"
    BOOK = "book"
    WEBSITE = "website"
    API = "api"


class AccessMethod(str, Enum):
    """Access method for source data."""

    LOCAL_FILE = "local_file"
    HTTP_DOWNLOAD = "http_download"
    API = "api"
    SCRAPE = "scrape"
    MANUAL = "manual"


@dataclass
class SourceManifest:
    """Manifest entry for a single data source."""

    source_name: str
    source_id: str
    source_type: SourceType
    access_method: AccessMethod
    canonical_url: Optional[str]
    license_info: str
    priority: int
    source_org: Optional[str] = None
    year: Optional[int] = None
    content_type: Optional[str] = None
    tags: List[str] = None
    location: Optional[str] = None
    metadata: Dict[str, Any] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SourceManifest":
        """Create SourceManifest from dictionary.

        Args:
            data: Dictionary containing manifest data

        Returns:
            SourceManifest instance

        Raises:
            ValueError: If required fields are missing or invalid
        """
        try:
            return cls(
                source_name=data["source_name"],
                source_id=data["source_id"],
                source_type=SourceType(data["source_type"]),
                access_method=AccessMethod(data["access_method"]),
                canonical_url=data.get("canonical_url"),
                license_info=data["license_info"],
                priority=int(data["priority"]),
                source_org=data.get("source_org"),
                year=data.get("year"),
                content_type=data.get("content_type"),
                tags=data.get("tags", []),
                location=data.get("location"),
                metadata=data.get("metadata", {}),
            )
        except KeyError as e:
            raise ValueError(f"Missing required field in manifest: {e}") from e
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid manifest data: {e}") from e

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Dictionary representation
        """
        return {
            "source_name": self.source_name,
            "source_id": self.source_id,
            "source_type": self.source_type.value,
            "access_method": self.access_method.value,
            "canonical_url": self.canonical_url,
            "license_info": self.license_info,
            "priority": self.priority,
            "source_org": self.source_org,
            "year": self.year,
            "content_type": self.content_type,
            "tags": self.tags or [],
            "location": self.location,
            "metadata": self.metadata or {},
        }

    def is_p0(self) -> bool:
        """Check if this is a P0 (priority 0) source.

        Returns:
            True if priority is 0, False otherwise
        """
        return self.priority == 0


class ManifestLoader:
    """Loader for First Fruits manifest files.

    This class handles loading, parsing, and filtering of manifest files
    that define available data sources.
    """

    def __init__(self, manifest_path: Optional[Path] = None) -> None:
        """Initialize manifest loader.

        Args:
            manifest_path: Path to manifest file (optional)
        """
        self.manifest_path = manifest_path
        self._sources: List[SourceManifest] = []
        self._loaded = False

    def load_manifest(self, manifest_path: Optional[Path] = None) -> None:
        """Load manifest from JSON file.

        Args:
            manifest_path: Path to manifest file (overrides constructor path)

        Raises:
            FileNotFoundError: If manifest file not found
            ValueError: If manifest format is invalid
        """
        path = manifest_path or self.manifest_path

        if not path:
            raise ValueError("Manifest path not provided")

        if not path.exists():
            raise FileNotFoundError(f"Manifest file not found: {path}")

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Handle both list and dict formats
            if isinstance(data, dict) and "sources" in data:
                sources_data = data["sources"]
            elif isinstance(data, list):
                sources_data = data
            else:
                raise ValueError("Invalid manifest format: expected list or dict with 'sources' key")

            self._sources = [SourceManifest.from_dict(source) for source in sources_data]
            self._loaded = True

        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in manifest file: {e}") from e

    def load_from_dict(self, manifest_data: Dict[str, Any]) -> None:
        """Load manifest from dictionary.

        Args:
            manifest_data: Manifest data as dictionary

        Raises:
            ValueError: If manifest format is invalid
        """
        try:
            # Handle both list and dict formats
            if isinstance(manifest_data, dict) and "sources" in manifest_data:
                sources_data = manifest_data["sources"]
            elif isinstance(manifest_data, list):
                sources_data = manifest_data
            else:
                raise ValueError("Invalid manifest format: expected list or dict with 'sources' key")

            self._sources = [SourceManifest.from_dict(source) for source in sources_data]
            self._loaded = True

        except Exception as e:
            raise ValueError(f"Failed to load manifest from dict: {e}") from e

    def get_all_sources(self) -> List[SourceManifest]:
        """Get all sources from manifest.

        Returns:
            List of all source manifests

        Raises:
            RuntimeError: If manifest not loaded
        """
        if not self._loaded:
            raise RuntimeError("Manifest not loaded. Call load_manifest() first.")

        return self._sources.copy()

    def get_p0_sources(self) -> List[SourceManifest]:
        """Get only P0 (priority 0) sources from manifest.

        P0 sources are the highest priority sources that should be
        expanded to full text first.

        Returns:
            List of P0 source manifests

        Raises:
            RuntimeError: If manifest not loaded
        """
        if not self._loaded:
            raise RuntimeError("Manifest not loaded. Call load_manifest() first.")

        return [source for source in self._sources if source.is_p0()]

    def get_sources_by_priority(self, priority: int) -> List[SourceManifest]:
        """Get sources filtered by priority level.

        Args:
            priority: Priority level to filter (0 = highest)

        Returns:
            List of sources with specified priority

        Raises:
            RuntimeError: If manifest not loaded
        """
        if not self._loaded:
            raise RuntimeError("Manifest not loaded. Call load_manifest() first.")

        return [source for source in self._sources if source.priority == priority]

    def get_sources_by_type(self, source_type: SourceType) -> List[SourceManifest]:
        """Get sources filtered by type.

        Args:
            source_type: Source type to filter

        Returns:
            List of sources with specified type

        Raises:
            RuntimeError: If manifest not loaded
        """
        if not self._loaded:
            raise RuntimeError("Manifest not loaded. Call load_manifest() first.")

        return [source for source in self._sources if source.source_type == source_type]

    def get_sources_by_tags(self, tags: List[str], match_all: bool = False) -> List[SourceManifest]:
        """Get sources filtered by tags.

        Args:
            tags: Tags to filter by
            match_all: If True, source must have all tags; if False, any tag matches

        Returns:
            List of sources matching tag criteria

        Raises:
            RuntimeError: If manifest not loaded
        """
        if not self._loaded:
            raise RuntimeError("Manifest not loaded. Call load_manifest() first.")

        if match_all:
            return [
                source
                for source in self._sources
                if source.tags and all(tag in source.tags for tag in tags)
            ]
        else:
            return [
                source
                for source in self._sources
                if source.tags and any(tag in source.tags for tag in tags)
            ]

    def get_source_by_id(self, source_id: str) -> Optional[SourceManifest]:
        """Get a specific source by ID.

        Args:
            source_id: Source ID to find

        Returns:
            Source manifest if found, None otherwise

        Raises:
            RuntimeError: If manifest not loaded
        """
        if not self._loaded:
            raise RuntimeError("Manifest not loaded. Call load_manifest() first.")

        for source in self._sources:
            if source.source_id == source_id:
                return source

        return None

    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about loaded manifest.

        Returns:
            Dictionary containing manifest statistics

        Raises:
            RuntimeError: If manifest not loaded
        """
        if not self._loaded:
            raise RuntimeError("Manifest not loaded. Call load_manifest() first.")

        # Count by priority
        priority_counts = {}
        for source in self._sources:
            priority_counts[source.priority] = priority_counts.get(source.priority, 0) + 1

        # Count by type
        type_counts = {}
        for source in self._sources:
            type_name = source.source_type.value
            type_counts[type_name] = type_counts.get(type_name, 0) + 1

        # Count by access method
        access_counts = {}
        for source in self._sources:
            method_name = source.access_method.value
            access_counts[method_name] = access_counts.get(method_name, 0) + 1

        return {
            "total_sources": len(self._sources),
            "p0_sources": len(self.get_p0_sources()),
            "priority_distribution": priority_counts,
            "type_distribution": type_counts,
            "access_method_distribution": access_counts,
        }

    def validate_manifest(self) -> List[str]:
        """Validate loaded manifest and return list of issues.

        Returns:
            List of validation issues (empty if valid)

        Raises:
            RuntimeError: If manifest not loaded
        """
        if not self._loaded:
            raise RuntimeError("Manifest not loaded. Call load_manifest() first.")

        issues = []

        # Check for duplicate source IDs
        source_ids = [source.source_id for source in self._sources]
        duplicates = [sid for sid in set(source_ids) if source_ids.count(sid) > 1]
        if duplicates:
            issues.append(f"Duplicate source IDs found: {', '.join(duplicates)}")

        # Check for missing required fields
        for i, source in enumerate(self._sources):
            if not source.source_name:
                issues.append(f"Source at index {i} missing source_name")
            if not source.source_id:
                issues.append(f"Source at index {i} missing source_id")
            if not source.license_info:
                issues.append(f"Source '{source.source_id}' missing license_info")

        # Check for invalid priorities
        for source in self._sources:
            if source.priority < 0:
                issues.append(f"Source '{source.source_id}' has negative priority: {source.priority}")

        return issues
