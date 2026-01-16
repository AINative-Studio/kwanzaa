"""Model factory for config-driven model instantiation.

Provides a factory pattern for creating model instances from configuration
files or dictionaries, enabling easy model switching without code changes.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional, Type, Union

from backend.models.base import BaseModel, ModelConfig, ModelType
from backend.models.ai2 import AI2Model
from backend.models.llama import LLaMAModel
from backend.models.deepseek import DeepSeekModel

logger = logging.getLogger(__name__)


class ModelFactory:
    """Factory for creating model instances from configuration.

    The factory supports loading configuration from:
    - JSON files
    - YAML files
    - Python dictionaries
    - Environment variables

    Example usage:
        # From file
        model = ModelFactory.from_config_file("config/model_config.json")

        # From dict
        config_dict = {
            "model_type": "ai2",
            "model_name": "allenai/OLMo-7B",
            "adapter_path": "path/to/adapter"
        }
        model = ModelFactory.from_dict(config_dict)

        # Direct instantiation
        config = ModelConfig(model_type="ai2", model_name="allenai/OLMo-7B")
        model = ModelFactory.create(config)
    """

    # Registry mapping model types to implementation classes
    _MODEL_REGISTRY: Dict[ModelType, Type[BaseModel]] = {
        ModelType.AI2: AI2Model,
        ModelType.LLAMA: LLaMAModel,
        ModelType.DEEPSEEK: DeepSeekModel,
    }

    @classmethod
    def create(
        cls,
        config: ModelConfig,
        load_on_init: bool = False,
    ) -> BaseModel:
        """Create a model instance from a ModelConfig.

        Args:
            config: Model configuration
            load_on_init: Whether to load the model immediately

        Returns:
            Instantiated model

        Raises:
            ValueError: If model_type is not supported
        """
        model_class = cls._MODEL_REGISTRY.get(config.model_type)

        if model_class is None:
            supported_types = list(cls._MODEL_REGISTRY.keys())
            raise ValueError(
                f"Unsupported model_type: {config.model_type}. "
                f"Supported types: {supported_types}"
            )

        logger.info(
            f"Creating {config.model_type} model: {config.model_name}"
        )

        model = model_class(config)

        if load_on_init:
            logger.info("Loading model on initialization")
            model.load_model()

            # Load adapter if configured
            if config.adapter_path and config.adapter_type != "none":
                logger.info("Loading adapter on initialization")
                model.load_adapter()

        return model

    @classmethod
    def from_dict(
        cls,
        config_dict: Dict[str, Any],
        load_on_init: bool = False,
    ) -> BaseModel:
        """Create a model from a configuration dictionary.

        Args:
            config_dict: Dictionary with model configuration
            load_on_init: Whether to load the model immediately

        Returns:
            Instantiated model

        Raises:
            ValueError: If configuration is invalid
        """
        try:
            config = ModelConfig(**config_dict)
            return cls.create(config, load_on_init=load_on_init)
        except Exception as e:
            logger.error(f"Failed to create model from dict: {e}")
            raise ValueError(f"Invalid model configuration: {e}") from e

    @classmethod
    def from_config_file(
        cls,
        config_path: Union[str, Path],
        load_on_init: bool = False,
    ) -> BaseModel:
        """Create a model from a configuration file.

        Supports JSON and YAML formats. Format is detected by file extension.

        Args:
            config_path: Path to configuration file (.json or .yaml/.yml)
            load_on_init: Whether to load the model immediately

        Returns:
            Instantiated model

        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If file format is unsupported or config is invalid
        """
        config_path = Path(config_path)

        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")

        logger.info(f"Loading model config from: {config_path}")

        # Determine file format and load
        if config_path.suffix == ".json":
            with open(config_path, "r") as f:
                config_dict = json.load(f)
        elif config_path.suffix in [".yaml", ".yml"]:
            try:
                import yaml
            except ImportError as e:
                raise ImportError(
                    "PyYAML is required for YAML configs. "
                    "Install with: pip install pyyaml"
                ) from e

            with open(config_path, "r") as f:
                config_dict = yaml.safe_load(f)
        else:
            raise ValueError(
                f"Unsupported config file format: {config_path.suffix}. "
                f"Supported formats: .json, .yaml, .yml"
            )

        return cls.from_dict(config_dict, load_on_init=load_on_init)

    @classmethod
    def from_env(
        cls,
        prefix: str = "MODEL_",
        load_on_init: bool = False,
    ) -> BaseModel:
        """Create a model from environment variables.

        Environment variables should be prefixed (default: MODEL_) and
        match ModelConfig field names. For example:
        - MODEL_MODEL_TYPE=ai2
        - MODEL_MODEL_NAME=allenai/OLMo-7B
        - MODEL_ADAPTER_PATH=/path/to/adapter

        Args:
            prefix: Prefix for environment variables
            load_on_init: Whether to load the model immediately

        Returns:
            Instantiated model

        Raises:
            ValueError: If required environment variables are missing
        """
        import os

        config_dict = {}

        # Get all environment variables with the prefix
        for key, value in os.environ.items():
            if key.startswith(prefix):
                # Remove prefix and convert to lowercase
                config_key = key[len(prefix):].lower()

                # Convert string values to appropriate types
                if value.lower() in ["true", "false"]:
                    config_dict[config_key] = value.lower() == "true"
                elif value.isdigit():
                    config_dict[config_key] = int(value)
                elif value.replace(".", "", 1).isdigit():
                    config_dict[config_key] = float(value)
                else:
                    config_dict[config_key] = value

        if not config_dict:
            raise ValueError(
                f"No environment variables found with prefix: {prefix}"
            )

        logger.info(
            f"Creating model from environment variables (prefix: {prefix})"
        )
        return cls.from_dict(config_dict, load_on_init=load_on_init)

    @classmethod
    def register_model(
        cls,
        model_type: ModelType,
        model_class: Type[BaseModel],
    ) -> None:
        """Register a new model implementation.

        This allows extending the factory with custom model implementations.

        Args:
            model_type: Type identifier for the model
            model_class: Model class implementing BaseModel

        Raises:
            ValueError: If model_class doesn't inherit from BaseModel
        """
        if not issubclass(model_class, BaseModel):
            raise ValueError(
                f"Model class must inherit from BaseModel. "
                f"Got: {model_class}"
            )

        logger.info(f"Registering model type: {model_type}")
        cls._MODEL_REGISTRY[model_type] = model_class

    @classmethod
    def list_supported_models(cls) -> Dict[str, str]:
        """Get a list of supported model types.

        Returns:
            Dictionary mapping model types to implementation class names
        """
        return {
            model_type.value: model_class.__name__
            for model_type, model_class in cls._MODEL_REGISTRY.items()
        }

    @classmethod
    def get_default_config(cls, model_type: ModelType) -> Dict[str, Any]:
        """Get default configuration for a model type.

        Args:
            model_type: Type of model

        Returns:
            Dictionary with default configuration

        Raises:
            ValueError: If model_type is not supported
        """
        if model_type not in cls._MODEL_REGISTRY:
            raise ValueError(f"Unsupported model_type: {model_type}")

        # Base defaults
        defaults = {
            "model_type": model_type.value,
            "adapter_type": "none",
            "load_in_8bit": False,
            "load_in_4bit": False,
            "device_map": "auto",
            "torch_dtype": "auto",
            "trust_remote_code": False,
            "max_new_tokens": 2048,
            "temperature": 0.7,
            "top_p": 0.95,
            "top_k": 50,
            "repetition_penalty": 1.1,
            "do_sample": True,
            "use_cache": True,
            "batch_size": 1,
        }

        # Model-specific defaults
        if model_type == ModelType.AI2:
            defaults.update({
                "model_name": "allenai/OLMo-7B-Instruct",
                "context_length": 4096,
            })
        elif model_type == ModelType.LLAMA:
            defaults.update({
                "model_name": "meta-llama/Llama-2-7b-chat-hf",
                "context_length": 4096,
            })
        elif model_type == ModelType.DEEPSEEK:
            defaults.update({
                "model_name": "deepseek-ai/deepseek-coder-6.7b-instruct",
                "context_length": 16384,
            })

        return defaults


# Convenience function for quick model instantiation
def get_model(
    model_type: str,
    model_name: str,
    adapter_path: Optional[str] = None,
    load_on_init: bool = False,
    **kwargs: Any,
) -> BaseModel:
    """Convenience function to quickly create a model.

    Args:
        model_type: Type of model ("ai2", "llama", "deepseek")
        model_name: HuggingFace model identifier
        adapter_path: Optional path to adapter weights
        load_on_init: Whether to load the model immediately
        **kwargs: Additional configuration parameters

    Returns:
        Instantiated model

    Example:
        model = get_model(
            model_type="ai2",
            model_name="allenai/OLMo-7B",
            adapter_path="path/to/adapter",
            load_on_init=True,
            temperature=0.8,
        )
    """
    config_dict = {
        "model_type": model_type,
        "model_name": model_name,
        **kwargs,
    }

    if adapter_path:
        config_dict["adapter_path"] = adapter_path
        config_dict["adapter_type"] = kwargs.get("adapter_type", "lora")

    return ModelFactory.from_dict(config_dict, load_on_init=load_on_init)


# Convenience function to save configuration
def save_config(
    config: Union[ModelConfig, Dict[str, Any]],
    output_path: Union[str, Path],
) -> None:
    """Save model configuration to a file.

    Args:
        config: Model configuration (ModelConfig or dict)
        output_path: Path to save the configuration (.json or .yaml/.yml)

    Raises:
        ValueError: If file format is unsupported
    """
    output_path = Path(output_path)

    # Convert ModelConfig to dict if needed
    if isinstance(config, ModelConfig):
        config_dict = config.model_dump()
    else:
        config_dict = config

    # Save based on file extension
    if output_path.suffix == ".json":
        with open(output_path, "w") as f:
            json.dump(config_dict, f, indent=2)
    elif output_path.suffix in [".yaml", ".yml"]:
        try:
            import yaml
        except ImportError as e:
            raise ImportError(
                "PyYAML is required for YAML configs. "
                "Install with: pip install pyyaml"
            ) from e

        with open(output_path, "w") as f:
            yaml.dump(config_dict, f, default_flow_style=False)
    else:
        raise ValueError(
            f"Unsupported config file format: {output_path.suffix}. "
            f"Supported formats: .json, .yaml, .yml"
        )

    logger.info(f"Configuration saved to: {output_path}")
