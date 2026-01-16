"""Abstract base class for model implementations.

Provides a unified interface for all language models used in Kwanzaa,
including support for adapters, prompt formatting, and generation parameters.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel as PydanticBaseModel
from pydantic import Field, field_validator


class ModelType(str, Enum):
    """Supported model types."""

    AI2 = "ai2"
    LLAMA = "llama"
    DEEPSEEK = "deepseek"


class AdapterType(str, Enum):
    """Supported adapter types."""

    LORA = "lora"
    QLORA = "qlora"
    NONE = "none"


@dataclass
class PromptTemplate:
    """Template for model-specific prompt formatting.

    Attributes:
        system_prefix: Prefix for system messages
        system_suffix: Suffix for system messages
        user_prefix: Prefix for user messages
        user_suffix: Suffix for user messages
        assistant_prefix: Prefix for assistant messages
        assistant_suffix: Suffix for assistant messages
        bos_token: Beginning of sequence token
        eos_token: End of sequence token
        sep_token: Separator token between messages
    """

    system_prefix: str = ""
    system_suffix: str = "\n\n"
    user_prefix: str = "User: "
    user_suffix: str = "\n"
    assistant_prefix: str = "Assistant: "
    assistant_suffix: str = "\n"
    bos_token: str = ""
    eos_token: str = ""
    sep_token: str = ""

    def format_system(self, content: str) -> str:
        """Format a system message."""
        return f"{self.system_prefix}{content}{self.system_suffix}"

    def format_user(self, content: str) -> str:
        """Format a user message."""
        return f"{self.user_prefix}{content}{self.user_suffix}"

    def format_assistant(self, content: str) -> str:
        """Format an assistant message."""
        return f"{self.assistant_prefix}{content}{self.assistant_suffix}"

    def format_messages(
        self,
        messages: List[Dict[str, str]],
        include_generation_prompt: bool = True,
    ) -> str:
        """Format a list of messages into a single prompt string.

        Args:
            messages: List of message dicts with 'role' and 'content' keys
            include_generation_prompt: Whether to include assistant prefix for generation

        Returns:
            Formatted prompt string
        """
        formatted_parts = []

        if self.bos_token:
            formatted_parts.append(self.bos_token)

        for message in messages:
            role = message.get("role", "user")
            content = message.get("content", "")

            if role == "system":
                formatted_parts.append(self.format_system(content))
            elif role == "user":
                formatted_parts.append(self.format_user(content))
            elif role == "assistant":
                formatted_parts.append(self.format_assistant(content))

            if self.sep_token:
                formatted_parts.append(self.sep_token)

        # Add assistant prefix for generation
        if include_generation_prompt:
            formatted_parts.append(self.assistant_prefix)

        return "".join(formatted_parts)


class ModelConfig(PydanticBaseModel):
    """Configuration for model initialization.

    This class defines all parameters needed to initialize and configure
    a language model, including base model settings, adapter settings,
    and generation parameters.
    """

    # Model identification
    model_type: ModelType = Field(
        description="Type of model (ai2, llama, deepseek)"
    )
    model_name: str = Field(
        description="HuggingFace model identifier or path"
    )
    model_revision: Optional[str] = Field(
        default=None,
        description="Model revision/version to use",
    )

    # Adapter configuration
    adapter_type: AdapterType = Field(
        default=AdapterType.NONE,
        description="Type of adapter to load",
    )
    adapter_path: Optional[str] = Field(
        default=None,
        description="Path to adapter weights",
    )
    adapter_revision: Optional[str] = Field(
        default=None,
        description="Adapter revision/version",
    )

    # Model loading parameters
    load_in_8bit: bool = Field(
        default=False,
        description="Load model in 8-bit precision",
    )
    load_in_4bit: bool = Field(
        default=False,
        description="Load model in 4-bit precision",
    )
    device_map: Union[str, Dict[str, Any]] = Field(
        default="auto",
        description="Device mapping for model layers",
    )
    torch_dtype: str = Field(
        default="auto",
        description="PyTorch dtype (auto, float16, bfloat16, float32)",
    )
    trust_remote_code: bool = Field(
        default=False,
        description="Whether to trust remote code in model",
    )

    # Generation parameters
    max_new_tokens: int = Field(
        default=2048,
        ge=1,
        le=8192,
        description="Maximum number of tokens to generate",
    )
    temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="Sampling temperature",
    )
    top_p: float = Field(
        default=0.95,
        ge=0.0,
        le=1.0,
        description="Nucleus sampling threshold",
    )
    top_k: int = Field(
        default=50,
        ge=0,
        description="Top-k sampling parameter (0 = disabled)",
    )
    repetition_penalty: float = Field(
        default=1.1,
        ge=1.0,
        le=2.0,
        description="Penalty for token repetition",
    )
    do_sample: bool = Field(
        default=True,
        description="Whether to use sampling (vs greedy decoding)",
    )

    # Context and constraints
    context_length: int = Field(
        default=4096,
        ge=512,
        le=32768,
        description="Maximum context length",
    )
    pad_token_id: Optional[int] = Field(
        default=None,
        description="Padding token ID",
    )
    eos_token_id: Optional[Union[int, List[int]]] = Field(
        default=None,
        description="End of sequence token ID(s)",
    )

    # Performance settings
    use_cache: bool = Field(
        default=True,
        description="Use key-value cache during generation",
    )
    batch_size: int = Field(
        default=1,
        ge=1,
        le=32,
        description="Batch size for inference",
    )

    # Additional model-specific settings
    extra_params: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional model-specific parameters",
    )

    @field_validator("torch_dtype")
    @classmethod
    def validate_dtype(cls, v: str) -> str:
        """Validate PyTorch dtype."""
        valid_dtypes = ["auto", "float16", "bfloat16", "float32"]
        if v not in valid_dtypes:
            raise ValueError(
                f"Invalid torch_dtype: {v}. Valid options: {valid_dtypes}"
            )
        return v

    @field_validator("load_in_8bit", "load_in_4bit")
    @classmethod
    def validate_quantization(cls, v: bool, info) -> bool:
        """Ensure only one quantization mode is enabled."""
        if info.data.get("load_in_8bit") and info.data.get("load_in_4bit"):
            raise ValueError("Cannot use both 8-bit and 4-bit quantization")
        return v

    class Config:
        """Pydantic config."""

        use_enum_values = True


class BaseModel(ABC):
    """Abstract base class for all language models.

    This class defines the interface that all model implementations must follow,
    ensuring consistent behavior across different model types.
    """

    def __init__(self, config: ModelConfig):
        """Initialize the model with configuration.

        Args:
            config: Model configuration
        """
        self.config = config
        self._model = None
        self._tokenizer = None
        self._adapter_loaded = False

    @abstractmethod
    def load_model(self) -> None:
        """Load the base model and tokenizer.

        This method should initialize self._model and self._tokenizer
        according to the configuration.

        Raises:
            RuntimeError: If model loading fails
        """
        pass

    @abstractmethod
    def load_adapter(self, adapter_path: Optional[str] = None) -> None:
        """Load an adapter on top of the base model.

        Args:
            adapter_path: Path to adapter weights (uses config if None)

        Raises:
            RuntimeError: If adapter loading fails
            ValueError: If no adapter path is provided
        """
        pass

    @abstractmethod
    def get_prompt_template(self) -> PromptTemplate:
        """Get the model-specific prompt template.

        Returns:
            PromptTemplate configured for this model
        """
        pass

    @abstractmethod
    def generate(
        self,
        prompt: str,
        **generation_kwargs: Any,
    ) -> str:
        """Generate text from a prompt.

        Args:
            prompt: Input prompt string
            **generation_kwargs: Additional generation parameters

        Returns:
            Generated text

        Raises:
            RuntimeError: If generation fails
        """
        pass

    @abstractmethod
    def generate_batch(
        self,
        prompts: List[str],
        **generation_kwargs: Any,
    ) -> List[str]:
        """Generate text for a batch of prompts.

        Args:
            prompts: List of input prompt strings
            **generation_kwargs: Additional generation parameters

        Returns:
            List of generated texts

        Raises:
            RuntimeError: If generation fails
        """
        pass

    def format_messages(
        self,
        messages: List[Dict[str, str]],
        include_generation_prompt: bool = True,
    ) -> str:
        """Format messages using the model's prompt template.

        Args:
            messages: List of message dicts with 'role' and 'content' keys
            include_generation_prompt: Whether to include assistant prefix

        Returns:
            Formatted prompt string
        """
        template = self.get_prompt_template()
        return template.format_messages(messages, include_generation_prompt)

    def is_loaded(self) -> bool:
        """Check if model is loaded.

        Returns:
            True if model and tokenizer are loaded
        """
        return self._model is not None and self._tokenizer is not None

    def has_adapter(self) -> bool:
        """Check if an adapter is loaded.

        Returns:
            True if adapter is loaded
        """
        return self._adapter_loaded

    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model.

        Returns:
            Dictionary with model information
        """
        return {
            "model_type": self.config.model_type,
            "model_name": self.config.model_name,
            "model_revision": self.config.model_revision,
            "adapter_type": self.config.adapter_type,
            "adapter_path": self.config.adapter_path,
            "adapter_loaded": self._adapter_loaded,
            "is_loaded": self.is_loaded(),
            "context_length": self.config.context_length,
            "quantization": "8bit" if self.config.load_in_8bit else "4bit" if self.config.load_in_4bit else "none",
        }

    def unload(self) -> None:
        """Unload the model from memory.

        This method should be overridden by subclasses to implement
        proper cleanup of model resources.
        """
        self._model = None
        self._tokenizer = None
        self._adapter_loaded = False

    def __repr__(self) -> str:
        """String representation of the model."""
        return (
            f"{self.__class__.__name__}("
            f"model_name={self.config.model_name}, "
            f"adapter_loaded={self._adapter_loaded}, "
            f"is_loaded={self.is_loaded()})"
        )
