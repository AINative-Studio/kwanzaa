"""Application configuration.

This module provides the main Settings class which loads configuration from
environment variables. For model, adapter, and RAG configurations, use the
config_loader module which reads from YAML files in backend/config/
"""

from typing import Any, Dict, List, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # API Settings
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "Kwanzaa API"
    VERSION: str = "1.0.0"
    DEBUG: bool = False

    # CORS Settings
    BACKEND_CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"]
    )

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: str | List[str]) -> List[str] | str:
        """Parse CORS origins from string or list."""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # Database Settings
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://localhost/kwanzaa",
        description="PostgreSQL database URL",
    )

    # ZeroDB Settings
    ZERODB_PROJECT_ID: str = Field(
        default="",
        description="ZeroDB project ID",
    )
    ZERODB_API_KEY: str = Field(
        default="",
        description="ZeroDB API key",
    )
    ZERODB_API_URL: str = Field(
        default="https://api.zerodb.ainative.io",
        description="ZeroDB API base URL",
    )

    # Model Configuration
    BASE_MODEL: str = Field(
        default="ai2",
        description="Base model to use (ai2, llama, deepseek). Maps to config/models/{model}.yaml",
    )
    ADAPTER_TYPE: str = Field(
        default="qlora",
        description="Adapter type to use (qlora, lora, full_finetune). Maps to config/adapters/{adapter}.yaml",
    )
    MODEL_CACHE_DIR: str = Field(
        default=".cache/models",
        description="Directory for caching downloaded models",
    )

    # Embedding Settings
    EMBEDDING_MODEL: str = Field(
        default="BAAI/bge-small-en-v1.5",
        description="Default embedding model",
    )
    EMBEDDING_DIMENSIONS: int = Field(
        default=1536,
        description="Embedding vector dimensions",
    )
    EMBEDDING_BATCH_SIZE: int = Field(
        default=32,
        description="Batch size for embedding generation",
    )

    # Reranking Settings
    RERANK_MODEL: str = Field(
        default="cross-encoder/ms-marco-MiniLM-L-6-v2",
        description="Cross-encoder model for reranking",
    )

    # Search Settings
    DEFAULT_SEARCH_LIMIT: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Default number of search results",
    )
    MAX_SEARCH_LIMIT: int = Field(
        default=100,
        ge=1,
        le=1000,
        description="Maximum number of search results",
    )
    DEFAULT_SIMILARITY_THRESHOLD: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Default similarity threshold",
    )
    DEFAULT_NAMESPACE: str = Field(
        default="default",
        description="Default vector namespace",
    )

    # Persona Settings
    PERSONA_THRESHOLDS: Dict[str, float] = Field(
        default={
            "educator": 0.80,
            "researcher": 0.75,
            "creator": 0.65,
            "builder": 0.70,
        },
        description="Similarity thresholds by persona",
    )

    PERSONA_NAMESPACES: Dict[str, List[str]] = Field(
        default={
            "educator": ["kwanzaa_primary_sources"],
            "researcher": ["kwanzaa_primary_sources", "kwanzaa_black_press"],
            "creator": ["kwanzaa_primary_sources", "kwanzaa_speeches_letters", "kwanzaa_teaching_kits"],
            "builder": ["kwanzaa_dev_patterns"],
        },
        description="Default namespaces by persona",
    )

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = Field(
        default=60,
        description="API requests per minute",
    )
    RATE_LIMIT_BURST: int = Field(
        default=10,
        description="Burst limit per second",
    )

    # Security
    SECRET_KEY: str = Field(
        default="changeme",
        description="Secret key for JWT signing",
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=60,
        description="Access token expiration time in minutes",
    )
    ALGORITHM: str = Field(
        default="HS256",
        description="JWT algorithm",
    )

    # Logging
    LOG_LEVEL: str = Field(
        default="INFO",
        description="Logging level",
    )
    LOG_FORMAT: str = Field(
        default="json",
        description="Log format (json or text)",
    )

    # Performance
    QUERY_CACHE_TTL_SECONDS: int = Field(
        default=300,
        description="Query result cache TTL",
    )
    EMBEDDING_CACHE_TTL_SECONDS: int = Field(
        default=3600,
        description="Embedding cache TTL",
    )

    # Model Mode Settings
    DEFAULT_MODEL_MODE: str = Field(
        default="full",
        description="Default model mode (base, base_adapter, full)",
    )
    SESSION_TTL_MINUTES: int = Field(
        default=60,
        ge=1,
        le=1440,
        description="Session TTL in minutes (max 24 hours)",
    )

    # Feature Flags
    ENABLE_RERANKING: bool = Field(
        default=True,
        description="Enable result reranking for better relevance",
    )
    ENABLE_HYBRID_SEARCH: bool = Field(
        default=False,
        description="Enable hybrid semantic + keyword search",
    )
    ENABLE_QUERY_EXPANSION: bool = Field(
        default=False,
        description="Enable query expansion for better recall",
    )

    def get_persona_config(self, persona_key: str) -> Dict[str, Any]:
        """Get configuration for a specific persona.

        Args:
            persona_key: Persona identifier (educator, researcher, creator, builder)

        Returns:
            Dict containing threshold, namespaces, and RAG settings for the persona

        Raises:
            ValueError: If persona_key is invalid
        """
        if persona_key not in self.PERSONA_THRESHOLDS:
            raise ValueError(
                f"Invalid persona_key: {persona_key}. "
                f"Valid options: {list(self.PERSONA_THRESHOLDS.keys())}"
            )

        # Default RAG settings by persona
        rag_defaults = {
            "educator": {"max_results": 10, "min_results": 3, "rerank": True},
            "researcher": {"max_results": 20, "min_results": 5, "rerank": True},
            "creator": {"max_results": 15, "min_results": 2, "rerank": False},
            "builder": {"max_results": 10, "min_results": 1, "rerank": False},
        }

        return {
            "threshold": self.PERSONA_THRESHOLDS[persona_key],
            "namespaces": self.PERSONA_NAMESPACES.get(persona_key, [self.DEFAULT_NAMESPACE]),
            "rag": {
                "similarity_threshold": self.PERSONA_THRESHOLDS[persona_key],
                "max_results": rag_defaults[persona_key]["max_results"],
                "min_results": rag_defaults[persona_key]["min_results"],
                "rerank": rag_defaults[persona_key]["rerank"],
            },
        }


# Global settings instance
settings = Settings()
