"""Tests for training utilities."""

import json
import tempfile
from pathlib import Path

import pytest

from backend.training.utils.artifacts import (
    generate_file_checksum,
    generate_artifact_checksum,
    verify_artifact_integrity,
    create_artifact_metadata,
    generate_adapter_readme,
)
from backend.training.utils.metrics import (
    TrainingMetrics,
    MetricsTracker,
    compute_perplexity,
    compute_citation_rate,
    compute_json_validity_rate,
)


class TestArtifacts:
    """Test artifact management utilities."""

    def test_generate_file_checksum(self, tmp_path):
        """Test file checksum generation."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Hello, World!")

        checksum = generate_file_checksum(str(test_file))
        assert len(checksum) == 64  # SHA256 produces 64 hex characters
        assert isinstance(checksum, str)

        # Same content should produce same checksum
        checksum2 = generate_file_checksum(str(test_file))
        assert checksum == checksum2

    def test_generate_artifact_checksum(self, tmp_path):
        """Test artifact directory checksum generation."""
        # Create test files
        (tmp_path / "file1.txt").write_text("Content 1")
        (tmp_path / "file2.txt").write_text("Content 2")
        (tmp_path / "subdir").mkdir()
        (tmp_path / "subdir" / "file3.txt").write_text("Content 3")

        checksums = generate_artifact_checksum(str(tmp_path))

        assert "file1.txt" in checksums
        assert "file2.txt" in checksums
        assert str(Path("subdir") / "file3.txt") in checksums
        assert len(checksums) == 3

    def test_verify_artifact_integrity_success(self, tmp_path):
        """Test artifact integrity verification - success case."""
        # Create test files
        test_file = tmp_path / "test.txt"
        test_file.write_text("Test content")

        # Generate checksums
        checksums = generate_artifact_checksum(str(tmp_path))

        # Verify integrity
        is_valid, errors = verify_artifact_integrity(str(tmp_path), checksums)

        assert is_valid
        assert len(errors) == 0

    def test_verify_artifact_integrity_failure(self, tmp_path):
        """Test artifact integrity verification - failure case."""
        # Create test file and generate checksum
        test_file = tmp_path / "test.txt"
        test_file.write_text("Original content")
        checksums = generate_artifact_checksum(str(tmp_path))

        # Modify file
        test_file.write_text("Modified content")

        # Verify integrity
        is_valid, errors = verify_artifact_integrity(str(tmp_path), checksums)

        assert not is_valid
        assert len(errors) > 0
        assert "Checksum mismatch" in errors[0]

    def test_verify_artifact_integrity_missing_file(self, tmp_path):
        """Test artifact integrity verification - missing file."""
        checksums = {"missing_file.txt": "abc123"}

        is_valid, errors = verify_artifact_integrity(str(tmp_path), checksums)

        assert not is_valid
        assert len(errors) > 0
        assert "Missing file" in errors[0]

    def test_create_artifact_metadata(self):
        """Test artifact metadata creation."""
        metadata = create_artifact_metadata(
            base_model_id="allenai/OLMo-7B-Instruct",
            adapter_config={
                "method": "qlora",
                "lora": {"r": 16, "alpha": 32, "dropout": 0.05, "target_modules": []},
            },
            training_config={
                "training": {
                    "num_train_epochs": 2,
                    "learning_rate": 0.0002,
                    "per_device_train_batch_size": 1,
                    "gradient_accumulation_steps": 16,
                },
                "data": {"max_seq_length": 2048},
                "artifacts": {"metadata": {"task": "test_task", "dataset_version": "v1"}},
            },
            training_metrics={"final_loss": 1.234, "final_perplexity": 3.44},
            version="v1.0.0",
        )

        assert metadata["version"] == "v1.0.0"
        assert metadata["base_model"]["model_id"] == "allenai/OLMo-7B-Instruct"
        assert metadata["adapter"]["method"] == "qlora"
        assert metadata["adapter"]["lora_r"] == 16
        assert metadata["training"]["num_epochs"] == 2
        assert metadata["metrics"]["final_loss"] == 1.234

    def test_generate_adapter_readme(self):
        """Test README generation."""
        metadata = {
            "version": "v1.0.0",
            "created_at": "2024-01-01T00:00:00",
            "adapter": {
                "method": "qlora",
                "lora_r": 16,
                "lora_alpha": 32,
                "lora_dropout": 0.05,
                "target_modules": ["q_proj", "v_proj"],
            },
            "training": {
                "num_epochs": 2,
                "learning_rate": 0.0002,
                "batch_size": 1,
                "gradient_accumulation_steps": 16,
                "max_seq_length": 2048,
            },
            "metrics": {"final_loss": 1.234, "final_perplexity": 3.44},
            "task": "citation-grounded-chat",
        }

        readme = generate_adapter_readme(metadata, "allenai/OLMo-7B-Instruct")

        assert "v1.0.0" in readme
        assert "allenai/OLMo-7B-Instruct" in readme
        assert "qlora" in readme
        assert "1.234" in readme
        assert "3.44" in readme
        assert "python" in readme.lower()  # Usage example


class TestMetrics:
    """Test metrics tracking utilities."""

    def test_training_metrics_creation(self):
        """Test TrainingMetrics dataclass."""
        metrics = TrainingMetrics(
            epoch=1,
            step=100,
            loss=1.234,
            eval_loss=1.5,
            perplexity=3.44,
            learning_rate=0.0002,
        )

        assert metrics.epoch == 1
        assert metrics.step == 100
        assert metrics.loss == 1.234
        assert metrics.timestamp is not None

    def test_training_metrics_to_dict(self):
        """Test TrainingMetrics serialization."""
        metrics = TrainingMetrics(epoch=1, step=100, loss=1.234)
        metrics_dict = metrics.to_dict()

        assert isinstance(metrics_dict, dict)
        assert metrics_dict["epoch"] == 1
        assert metrics_dict["step"] == 100
        assert metrics_dict["loss"] == 1.234

    def test_metrics_tracker_initialization(self, tmp_path):
        """Test MetricsTracker initialization."""
        tracker = MetricsTracker(str(tmp_path))

        assert tracker.output_dir == tmp_path
        assert tracker.best_eval_loss == float("inf")
        assert len(tracker.metrics_history) == 0

    def test_metrics_tracker_log_metrics(self, tmp_path):
        """Test logging metrics."""
        tracker = MetricsTracker(str(tmp_path))

        metrics = TrainingMetrics(epoch=1, step=100, loss=1.234, eval_loss=1.5)
        tracker.log_metrics(metrics)

        assert len(tracker.metrics_history) == 1
        assert tracker.best_eval_loss == 1.5

        # Log better metrics
        better_metrics = TrainingMetrics(epoch=2, step=200, loss=1.0, eval_loss=1.2)
        tracker.log_metrics(better_metrics)

        assert len(tracker.metrics_history) == 2
        assert tracker.best_eval_loss == 1.2
        assert "checkpoint-200" in tracker.best_checkpoint

    def test_metrics_tracker_get_summary(self, tmp_path):
        """Test metrics summary generation."""
        tracker = MetricsTracker(str(tmp_path))

        # Log multiple metrics
        for i in range(5):
            metrics = TrainingMetrics(
                epoch=1, step=i * 100, loss=2.0 - i * 0.2, eval_loss=2.0 - i * 0.2
            )
            tracker.log_metrics(metrics)

        summary = tracker.get_metrics_summary()

        assert summary["total_steps"] == 5
        assert summary["final_loss"] == 1.2  # 2.0 - 4*0.2
        assert summary["best_eval_loss"] == 1.2
        assert summary["avg_loss"] is not None

    def test_compute_perplexity(self):
        """Test perplexity computation."""
        assert compute_perplexity(0.0) == 1.0
        assert compute_perplexity(1.0) == pytest.approx(2.718, rel=0.01)
        assert compute_perplexity(2.0) == pytest.approx(7.389, rel=0.01)

    def test_compute_citation_rate(self):
        """Test citation rate computation."""
        texts_with_citations = [
            "Based on [1], we can conclude...",
            "According to [source], the answer is...",
            "The result [2] shows...",
        ]
        texts_without_citations = [
            "I think the answer is...",
            "Based on my knowledge...",
        ]

        rate_with = compute_citation_rate(texts_with_citations)
        assert rate_with == 1.0  # All have citations

        rate_without = compute_citation_rate(texts_without_citations)
        assert rate_without == 0.0  # None have citations

        mixed = texts_with_citations + texts_without_citations
        rate_mixed = compute_citation_rate(mixed)
        assert rate_mixed == 0.6  # 3 out of 5

    def test_compute_json_validity_rate(self):
        """Test JSON validity rate computation."""
        valid_jsons = [
            '{"answer": "test", "confidence": 0.9}',
            'Some text {"key": "value"} more text',
            '{"nested": {"key": "value"}}',
        ]
        invalid_jsons = [
            "Not JSON at all",
            "{invalid json}",
        ]

        rate_valid = compute_json_validity_rate(valid_jsons)
        assert rate_valid == 1.0

        rate_invalid = compute_json_validity_rate(invalid_jsons)
        assert rate_invalid == 0.0

        mixed = valid_jsons + invalid_jsons
        rate_mixed = compute_json_validity_rate(mixed)
        assert rate_mixed == 0.6  # 3 out of 5


class TestMetricsTrackerPersistence:
    """Test metrics tracker file persistence."""

    def test_save_and_load_metrics(self, tmp_path):
        """Test saving and loading metrics history."""
        tracker = MetricsTracker(str(tmp_path))

        # Log some metrics
        for i in range(3):
            metrics = TrainingMetrics(epoch=1, step=i * 100, loss=2.0 - i * 0.5)
            tracker.log_metrics(metrics)

        # Check files were created
        assert (tmp_path / "metrics_history.jsonl").exists()

        # Create new tracker and load history
        new_tracker = MetricsTracker(str(tmp_path))
        new_tracker.load_metrics_history()

        assert len(new_tracker.metrics_history) == 3
        assert new_tracker.metrics_history[0].step == 0
        assert new_tracker.metrics_history[2].step == 200

    def test_save_summary(self, tmp_path):
        """Test saving summary to file."""
        tracker = MetricsTracker(str(tmp_path))

        metrics = TrainingMetrics(epoch=1, step=100, loss=1.234, eval_loss=1.5)
        tracker.log_metrics(metrics)

        tracker.save_summary()

        assert (tmp_path / "training_summary.json").exists()

        # Load and verify
        with open(tmp_path / "training_summary.json") as f:
            summary = json.load(f)

        assert summary["total_steps"] == 1
        assert summary["final_loss"] == 1.234
        assert summary["best_eval_loss"] == 1.5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
