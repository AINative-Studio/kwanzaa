"""Configuration loader for YAML-based config files.

This module provides utilities for loading and validating configuration
from YAML files, supporting model, adapter, and RAG configurations.
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from pydantic import BaseModel, Field, field_validator


class ConfigLoader:
    """Load and validate YAML configuration files."""

    def __init__(self, config_dir: Optional[Path] = None):
        """Initialize config loader.

        Args:
            config_dir: Root directory for config files. Defaults to backend/config/
        """
        if config_dir is None:
            # Default to backend/config relative to this file
            backend_dir = Path(__file__).parent.parent.parent
            config_dir = backend_dir / "config"

        self.config_dir = Path(config_dir)
        self._cache: Dict[str, Dict[str, Any]] = {}

    def load_yaml(self, filepath: Path) -> Dict[str, Any]:
        """Load YAML file and return parsed content.

        Args:
            filepath: Path to YAML file

        Returns:
            Parsed YAML content as dictionary

        Raises:
            FileNotFoundError: If file doesn't exist
            yaml.YAMLError: If YAML is malformed
        """
        if not filepath.exists():
            raise FileNotFoundError(f"Config file not found: {filepath}")

        with open(filepath, "r") as f:
            return yaml.safe_load(f)

    def load_model_config(self, model_name: str) -> Dict[str, Any]:
        """Load model configuration by name.

        Args:
            model_name: Model identifier (ai2, llama, deepseek)

        Returns:
            Model configuration dictionary

        Raises:
            FileNotFoundError: If model config doesn't exist
        """
        cache_key = f"model:{model_name}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        config_path = self.config_dir / "models" / f"{model_name}.yaml"
        config = self.load_yaml(config_path)
        self._cache[cache_key] = config
        return config

    def load_adapter_config(self, adapter_name: str) -> Dict[str, Any]:
        """Load adapter configuration by name.

        Args:
            adapter_name: Adapter identifier (qlora, lora, full_finetune)

        Returns:
            Adapter configuration dictionary

        Raises:
            FileNotFoundError: If adapter config doesn't exist
        """
        cache_key = f"adapter:{adapter_name}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        config_path = self.config_dir / "adapters" / f"{adapter_name}.yaml"
        config = self.load_yaml(config_path)
        self._cache[cache_key] = config
        return config

    def load_rag_config(self, config_type: str) -> Dict[str, Any]:
        """Load RAG configuration by type.

        Args:
            config_type: Config type (namespaces, personas, retrieval)

        Returns:
            RAG configuration dictionary

        Raises:
            FileNotFoundError: If RAG config doesn't exist
        """
        cache_key = f"rag:{config_type}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        config_path = self.config_dir / "rag" / f"{config_type}.yaml"
        config = self.load_yaml(config_path)
        self._cache[cache_key] = config
        return config

    def get_persona_config(self, persona_key: str) -> Dict[str, Any]:
        """Get configuration for a specific persona.

        Args:
            persona_key: Persona identifier (educator, researcher, creator, builder)

        Returns:
            Persona configuration including RAG settings

        Raises:
            ValueError: If persona doesn't exist
        """
        personas_config = self.load_rag_config("personas")
        personas = personas_config.get("personas", {})

        if persona_key not in personas:
            raise ValueError(
                f"Invalid persona: {persona_key}. "
                f"Valid options: {list(personas.keys())}"
            )

        return personas[persona_key]

    def get_namespace_config(self, namespace: str) -> Dict[str, Any]:
        """Get configuration for a specific namespace.

        Args:
            namespace: Namespace identifier

        Returns:
            Namespace configuration

        Raises:
            ValueError: If namespace doesn't exist
        """
        namespaces_config = self.load_rag_config("namespaces")
        namespaces = namespaces_config.get("namespaces", {})

        if namespace not in namespaces:
            raise ValueError(
                f"Invalid namespace: {namespace}. "
                f"Valid options: {list(namespaces.keys())}"
            )

        return namespaces[namespace]

    def list_available_models(self) -> list[str]:
        """List all available model configurations.

        Returns:
            List of model identifiers
        """
        models_dir = self.config_dir / "models"
        if not models_dir.exists():
            return []

        return [
            f.stem for f in models_dir.glob("*.yaml")
            if f.is_file()
        ]

    def list_available_adapters(self) -> list[str]:
        """List all available adapter configurations.

        Returns:
            List of adapter identifiers
        """
        adapters_dir = self.config_dir / "adapters"
        if not adapters_dir.exists():
            return []

        return [
            f.stem for f in adapters_dir.glob("*.yaml")
            if f.is_file()
        ]

    def list_available_personas(self) -> list[str]:
        """List all available personas.

        Returns:
            List of persona identifiers
        """
        try:
            personas_config = self.load_rag_config("personas")
            return list(personas_config.get("personas", {}).keys())
        except FileNotFoundError:
            return []

    def list_available_namespaces(self) -> list[str]:
        """List all available namespaces.

        Returns:
            List of namespace identifiers
        """
        try:
            namespaces_config = self.load_rag_config("namespaces")
            return list(namespaces_config.get("namespaces", {}).keys())
        except FileNotFoundError:
            return []

    def clear_cache(self) -> None:
        """Clear the configuration cache."""
        self._cache.clear()


class ModelConfig(BaseModel):
    """Validated model configuration."""

    provider: str
    model_id: str
    model_type: str
    capabilities: Dict[str, Any]
    loading: Dict[str, Any]
    generation: Dict[str, Any] = Field(default_factory=dict)


class AdapterConfig(BaseModel):
    """Validated adapter configuration."""

    name: str
    method: str
    lora: Optional[Dict[str, Any]] = None
    quantization: Optional[Dict[str, Any]] = None
    training: Optional[Dict[str, Any]] = None


class PersonaConfig(BaseModel):
    """Validated persona configuration."""

    display_name: str
    description: str
    rag: Dict[str, Any]
    modes: Dict[str, bool]
    response: Dict[str, Any]
    system_prompt_additions: list[str] = Field(default_factory=list)


# Global config loader instance
config_loader = ConfigLoader()
