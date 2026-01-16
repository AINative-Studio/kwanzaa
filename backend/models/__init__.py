"""Model abstraction layer for Kwanzaa.

This package provides a unified interface for all base models (AI2, LLaMA, DeepSeek)
with support for adapter loading and model-specific prompt formatting.
"""

from backend.models.base import BaseModel, ModelConfig, PromptTemplate
from backend.models.factory import ModelFactory, get_model

__all__ = [
    "BaseModel",
    "ModelConfig",
    "PromptTemplate",
    "ModelFactory",
    "get_model",
]
