"""DeepSeek model implementation.

Supports DeepSeek models with proper prompt formatting and adapter loading.
"""

import logging
from typing import Any, List, Optional

from backend.models.base import BaseModel, ModelConfig, PromptTemplate

logger = logging.getLogger(__name__)


class DeepSeekPromptTemplate(PromptTemplate):
    """Prompt template for DeepSeek models.

    DeepSeek uses a ChatML-style format similar to OpenAI models.
    """

    def __init__(self):
        super().__init__(
            system_prefix="<|im_start|>system\n",
            system_suffix="<|im_end|>\n",
            user_prefix="<|im_start|>user\n",
            user_suffix="<|im_end|>\n",
            assistant_prefix="<|im_start|>assistant\n",
            assistant_suffix="<|im_end|>\n",
            bos_token="<|begin▁of▁sentence|>",
            eos_token="<|im_end|>",
            sep_token="",
        )


class DeepSeekModel(BaseModel):
    """DeepSeek model implementation.

    Supports DeepSeek models including:
    - DeepSeek Coder (various sizes)
    - DeepSeek Chat variants
    - DeepSeek Math models

    Example models:
    - deepseek-ai/deepseek-coder-6.7b-base
    - deepseek-ai/deepseek-coder-6.7b-instruct
    - deepseek-ai/deepseek-llm-7b-chat
    - deepseek-ai/deepseek-math-7b-instruct
    """

    def __init__(self, config: ModelConfig):
        """Initialize DeepSeek model.

        Args:
            config: Model configuration
        """
        super().__init__(config)
        self._validate_config()

    def _validate_config(self) -> None:
        """Validate DeepSeek-specific configuration."""
        # DeepSeek models support various context lengths
        # Coder models typically support up to 16K tokens
        if "coder" in self.config.model_name.lower() and self.config.context_length > 16384:
            logger.warning(
                f"DeepSeek Coder models typically support up to 16384 tokens. "
                f"Requested: {self.config.context_length}"
            )

    def load_model(self) -> None:
        """Load the DeepSeek base model and tokenizer.

        Raises:
            RuntimeError: If model loading fails
            ImportError: If required libraries are not installed
        """
        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer
            import torch
        except ImportError as e:
            raise ImportError(
                "transformers and torch are required for DeepSeek models. "
                "Install with: pip install transformers torch"
            ) from e

        logger.info(f"Loading DeepSeek model: {self.config.model_name}")

        try:
            # Prepare dtype
            dtype_map = {
                "auto": "auto",
                "float16": torch.float16,
                "bfloat16": torch.bfloat16,
                "float32": torch.float32,
            }
            torch_dtype = dtype_map.get(self.config.torch_dtype, "auto")

            # Load tokenizer
            self._tokenizer = AutoTokenizer.from_pretrained(
                self.config.model_name,
                revision=self.config.model_revision,
                trust_remote_code=self.config.trust_remote_code,
            )

            # Ensure pad token is set
            if self._tokenizer.pad_token is None:
                self._tokenizer.pad_token = self._tokenizer.eos_token
                if self.config.pad_token_id is None:
                    self.config.pad_token_id = self._tokenizer.eos_token_id

            # Load model with appropriate settings
            model_kwargs = {
                "pretrained_model_name_or_path": self.config.model_name,
                "revision": self.config.model_revision,
                "torch_dtype": torch_dtype,
                "device_map": self.config.device_map,
                "trust_remote_code": self.config.trust_remote_code,
            }

            # Add quantization settings
            if self.config.load_in_8bit:
                model_kwargs["load_in_8bit"] = True
            elif self.config.load_in_4bit:
                model_kwargs["load_in_4bit"] = True

            self._model = AutoModelForCausalLM.from_pretrained(**model_kwargs)

            logger.info(
                f"Successfully loaded DeepSeek model: {self.config.model_name}"
            )

        except Exception as e:
            logger.error(f"Failed to load DeepSeek model: {e}")
            raise RuntimeError(f"Failed to load DeepSeek model: {e}") from e

    def load_adapter(self, adapter_path: Optional[str] = None) -> None:
        """Load a LoRA/QLoRA adapter on top of the base model.

        Args:
            adapter_path: Path to adapter weights (uses config if None)

        Raises:
            RuntimeError: If adapter loading fails
            ValueError: If no adapter path is provided or model not loaded
            ImportError: If PEFT is not installed
        """
        if not self.is_loaded():
            raise ValueError("Base model must be loaded before loading adapter")

        adapter_path = adapter_path or self.config.adapter_path
        if not adapter_path:
            raise ValueError("No adapter path provided")

        try:
            from peft import PeftModel
        except ImportError as e:
            raise ImportError(
                "peft is required for adapter loading. "
                "Install with: pip install peft"
            ) from e

        logger.info(f"Loading adapter from: {adapter_path}")

        try:
            self._model = PeftModel.from_pretrained(
                self._model,
                adapter_path,
                revision=self.config.adapter_revision,
            )
            self._adapter_loaded = True
            logger.info(f"Successfully loaded adapter from: {adapter_path}")

        except Exception as e:
            logger.error(f"Failed to load adapter: {e}")
            raise RuntimeError(f"Failed to load adapter: {e}") from e

    def get_prompt_template(self) -> PromptTemplate:
        """Get the DeepSeek-specific prompt template.

        Returns:
            DeepSeekPromptTemplate configured for ChatML format
        """
        return DeepSeekPromptTemplate()

    def generate(
        self,
        prompt: str,
        **generation_kwargs: Any,
    ) -> str:
        """Generate text from a prompt using the DeepSeek model.

        Args:
            prompt: Input prompt string
            **generation_kwargs: Additional generation parameters

        Returns:
            Generated text

        Raises:
            RuntimeError: If generation fails
            ValueError: If model is not loaded
        """
        if not self.is_loaded():
            raise ValueError("Model must be loaded before generation")

        try:
            import torch

            # Tokenize input
            inputs = self._tokenizer(
                prompt,
                return_tensors="pt",
                truncation=True,
                max_length=self.config.context_length,
            )

            # Move to same device as model
            device = next(self._model.parameters()).device
            inputs = {k: v.to(device) for k, v in inputs.items()}

            # Prepare generation parameters
            gen_params = {
                "max_new_tokens": self.config.max_new_tokens,
                "temperature": self.config.temperature,
                "top_p": self.config.top_p,
                "top_k": self.config.top_k,
                "repetition_penalty": self.config.repetition_penalty,
                "do_sample": self.config.do_sample,
                "use_cache": self.config.use_cache,
                "pad_token_id": self.config.pad_token_id or self._tokenizer.pad_token_id,
            }

            # Override with user-provided kwargs
            gen_params.update(generation_kwargs)

            # Generate
            with torch.no_grad():
                outputs = self._model.generate(
                    **inputs,
                    **gen_params,
                )

            # Decode output, removing input prompt
            generated_text = self._tokenizer.decode(
                outputs[0][inputs["input_ids"].shape[1]:],
                skip_special_tokens=True,
            )

            return generated_text.strip()

        except Exception as e:
            logger.error(f"Generation failed: {e}")
            raise RuntimeError(f"Generation failed: {e}") from e

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
            ValueError: If model is not loaded
        """
        if not self.is_loaded():
            raise ValueError("Model must be loaded before generation")

        try:
            import torch

            # Tokenize inputs
            inputs = self._tokenizer(
                prompts,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=self.config.context_length,
            )

            # Move to same device as model
            device = next(self._model.parameters()).device
            inputs = {k: v.to(device) for k, v in inputs.items()}

            # Prepare generation parameters
            gen_params = {
                "max_new_tokens": self.config.max_new_tokens,
                "temperature": self.config.temperature,
                "top_p": self.config.top_p,
                "top_k": self.config.top_k,
                "repetition_penalty": self.config.repetition_penalty,
                "do_sample": self.config.do_sample,
                "use_cache": self.config.use_cache,
                "pad_token_id": self.config.pad_token_id or self._tokenizer.pad_token_id,
            }

            # Override with user-provided kwargs
            gen_params.update(generation_kwargs)

            # Generate
            with torch.no_grad():
                outputs = self._model.generate(
                    **inputs,
                    **gen_params,
                )

            # Decode outputs
            generated_texts = []
            input_lengths = inputs["attention_mask"].sum(dim=1)

            for i, output in enumerate(outputs):
                # Skip input tokens
                generated_tokens = output[input_lengths[i]:]
                generated_text = self._tokenizer.decode(
                    generated_tokens,
                    skip_special_tokens=True,
                )
                generated_texts.append(generated_text.strip())

            return generated_texts

        except Exception as e:
            logger.error(f"Batch generation failed: {e}")
            raise RuntimeError(f"Batch generation failed: {e}") from e

    def unload(self) -> None:
        """Unload the model from memory and free GPU resources."""
        if self._model is not None:
            import torch
            import gc

            del self._model
            del self._tokenizer
            self._model = None
            self._tokenizer = None
            self._adapter_loaded = False

            # Clear GPU cache if available
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            gc.collect()

            logger.info("DeepSeek model unloaded successfully")
