"""Tests for trained adapter integration.

This module tests the integration of the trained Kwanzaa adapter
into the backend inference pipeline.

Following TDD approach: Write tests first (RED), then implement (GREEN).
"""

import pytest
from pathlib import Path
from app.core.config_loader import config_loader


class TestAdapterConfiguration:
    """Test adapter configuration loading."""

    def test_qlora_config_loads_successfully(self):
        """Test that QLoRA adapter config loads without errors."""
        # Given: QLoRA adapter config exists
        # When: Loading the adapter configuration
        config = config_loader.load_adapter_config("qlora")

        # Then: Config should be loaded successfully
        assert config is not None
        assert "adapter" in config
        assert config["adapter"]["name"] == "qlora"

    def test_qlora_config_has_adapter_path(self):
        """Test that QLoRA config includes adapter_path for trained model."""
        # Given: QLoRA adapter config
        config = config_loader.load_adapter_config("qlora")

        # When: Checking for adapter_path
        adapter_section = config.get("adapter", {})

        # Then: Should have adapter_path pointing to trained model
        assert "adapter_path" in adapter_section
        assert "kwanzaa-adapter-v1" in adapter_section["adapter_path"]

    def test_adapter_path_exists(self):
        """Test that the adapter path points to existing files."""
        # Given: QLoRA config with adapter_path
        config = config_loader.load_adapter_config("qlora")
        adapter_path = config["adapter"]["adapter_path"]

        # When: Resolving the path
        backend_dir = Path(__file__).parent.parent
        full_path = backend_dir / adapter_path

        # Then: Path should exist and contain adapter files
        assert full_path.exists(), f"Adapter path does not exist: {full_path}"
        assert full_path.is_dir(), f"Adapter path is not a directory: {full_path}"

        # Check for required adapter files
        required_files = [
            "adapter_config.json",
            "adapter_model.safetensors"
        ]
        for filename in required_files:
            file_path = full_path / filename
            assert file_path.exists(), f"Required file missing: {filename}"


class TestModelConfiguration:
    """Test model configuration for Llama-3.2-1B."""

    def test_llama_config_uses_correct_model(self):
        """Test that Llama config uses Llama-3.2-1B-Instruct."""
        # Given: Llama model config
        config = config_loader.load_model_config("llama")

        # When: Checking model_id
        model_id = config.get("model", {}).get("model_id")

        # Then: Should use Llama-3.2-1B-Instruct (the model we trained on)
        assert "Llama-3.2-1B-Instruct" in model_id


class TestAdapterLoading:
    """Test actual adapter loading with transformers/PEFT."""

    @pytest.mark.integration
    def test_adapter_can_be_loaded_with_peft(self):
        """Test that adapter can be loaded using PEFT library."""
        # Given: Adapter path from config
        config = config_loader.load_adapter_config("qlora")
        adapter_path = config["adapter"]["adapter_path"]
        backend_dir = Path(__file__).parent.parent
        full_path = backend_dir / adapter_path

        # When: Attempting to load adapter config
        from peft import PeftConfig
        peft_config = PeftConfig.from_pretrained(str(full_path))

        # Then: Config should load successfully
        assert peft_config is not None
        assert peft_config.peft_type == "LORA"
        assert peft_config.base_model_name_or_path == "meta-llama/Llama-3.2-1B-Instruct"

    @pytest.mark.integration
    def test_adapter_config_matches_training(self):
        """Test that adapter config matches training parameters."""
        # Given: Adapter path from config
        config = config_loader.load_adapter_config("qlora")
        adapter_path = config["adapter"]["adapter_path"]
        backend_dir = Path(__file__).parent.parent
        full_path = backend_dir / adapter_path

        # When: Loading adapter config
        from peft import PeftConfig
        peft_config = PeftConfig.from_pretrained(str(full_path))

        # Then: Parameters should match training config
        assert peft_config.r == 16  # LoRA rank
        assert peft_config.lora_alpha == 32
        assert peft_config.lora_dropout == 0.05

        # Check target modules
        expected_modules = ["q_proj", "k_proj", "v_proj", "o_proj",
                            "gate_proj", "up_proj", "down_proj"]
        for module in expected_modules:
            assert module in peft_config.target_modules


class TestEndToEndInference:
    """Test end-to-end inference with trained adapter."""

    @pytest.mark.slow
    @pytest.mark.integration
    def test_adapter_inference_produces_valid_response(self):
        """Test that adapter can perform inference and produce valid responses."""
        # Given: Loaded model with adapter
        config = config_loader.load_adapter_config("qlora")
        adapter_path = config["adapter"]["adapter_path"]
        backend_dir = Path(__file__).parent.parent
        full_path = backend_dir / adapter_path

        from transformers import AutoTokenizer
        from peft import AutoPeftModelForCausalLM

        # When: Loading model and generating response
        model = AutoPeftModelForCausalLM.from_pretrained(
            str(full_path),
            device_map="auto",
        )
        tokenizer = AutoTokenizer.from_pretrained(str(full_path))

        test_messages = [
            {"role": "system", "content": "You are a Kwanzaa expert."},
            {"role": "user", "content": "What are the seven principles of Kwanzaa?"}
        ]

        text = tokenizer.apply_chat_template(test_messages, tokenize=False, add_generation_prompt=True)
        inputs = tokenizer(text, return_tensors="pt").to(model.device)
        outputs = model.generate(**inputs, max_new_tokens=50, temperature=0.7)
        response = tokenizer.decode(outputs[0][inputs['input_ids'].shape[1]:], skip_special_tokens=True)

        # Then: Response should be non-empty and relevant
        assert len(response) > 0
        assert len(response.split()) > 5  # At least a few words


# Test markers for running subsets
pytestmark = [
    pytest.mark.adapter,
    pytest.mark.config,
]
