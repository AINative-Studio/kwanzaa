"""Service layer for business logic."""

# Lazy imports to avoid circular dependencies and missing dependencies
__all__ = ["SearchService", "EmbeddingService", "MetadataIngestionPipeline"]


def __getattr__(name):
    """Lazy load services to avoid import errors."""
    if name == "EmbeddingService":
        from app.services.embedding import EmbeddingService
        return EmbeddingService
    elif name == "SearchService":
        from app.services.search import SearchService
        return SearchService
    elif name == "MetadataIngestionPipeline":
        from app.services.metadata_ingestion import MetadataIngestionPipeline
        return MetadataIngestionPipeline
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
