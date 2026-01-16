"""Training metrics tracking and computation utilities."""

import json
import math
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import torch


@dataclass
class TrainingMetrics:
    """Container for training metrics."""

    epoch: int = 0
    step: int = 0
    loss: float = 0.0
    eval_loss: Optional[float] = None
    perplexity: Optional[float] = None
    learning_rate: float = 0.0

    # Custom metrics
    json_valid_rate: Optional[float] = None
    citation_coverage_rate: Optional[float] = None
    refusal_correctness_rate: Optional[float] = None
    retrieval_groundedness_rate: Optional[float] = None

    # Timing
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    epoch_time: Optional[float] = None
    total_time: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        return {
            "epoch": self.epoch,
            "step": self.step,
            "loss": self.loss,
            "eval_loss": self.eval_loss,
            "perplexity": self.perplexity,
            "learning_rate": self.learning_rate,
            "json_valid_rate": self.json_valid_rate,
            "citation_coverage_rate": self.citation_coverage_rate,
            "refusal_correctness_rate": self.refusal_correctness_rate,
            "retrieval_groundedness_rate": self.retrieval_groundedness_rate,
            "timestamp": self.timestamp,
            "epoch_time": self.epoch_time,
            "total_time": self.total_time,
        }


class MetricsTracker:
    """Track and log training metrics."""

    def __init__(self, output_dir: str):
        """
        Initialize metrics tracker.

        Args:
            output_dir: Directory to save metrics logs
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.metrics_history: List[TrainingMetrics] = []
        self.best_eval_loss: float = float("inf")
        self.best_checkpoint: Optional[str] = None

        self.metrics_file = self.output_dir / "metrics_history.jsonl"
        self.summary_file = self.output_dir / "training_summary.json"

    def log_metrics(self, metrics: TrainingMetrics) -> None:
        """
        Log metrics for current step.

        Args:
            metrics: TrainingMetrics object
        """
        self.metrics_history.append(metrics)

        # Update best eval loss
        if metrics.eval_loss is not None and metrics.eval_loss < self.best_eval_loss:
            self.best_eval_loss = metrics.eval_loss
            self.best_checkpoint = f"checkpoint-{metrics.step}"

        # Append to JSONL file
        with open(self.metrics_file, "a") as f:
            f.write(json.dumps(metrics.to_dict()) + "\n")

    def get_latest_metrics(self) -> Optional[TrainingMetrics]:
        """Get most recent metrics."""
        return self.metrics_history[-1] if self.metrics_history else None

    def get_metrics_summary(self) -> Dict[str, Any]:
        """
        Get summary of all metrics.

        Returns:
            Dictionary with summary statistics
        """
        if not self.metrics_history:
            return {}

        losses = [m.loss for m in self.metrics_history if m.loss > 0]
        eval_losses = [
            m.eval_loss for m in self.metrics_history if m.eval_loss is not None
        ]
        perplexities = [
            m.perplexity for m in self.metrics_history if m.perplexity is not None
        ]

        summary = {
            "total_steps": len(self.metrics_history),
            "final_loss": losses[-1] if losses else None,
            "final_eval_loss": eval_losses[-1] if eval_losses else None,
            "final_perplexity": perplexities[-1] if perplexities else None,
            "best_eval_loss": self.best_eval_loss if eval_losses else None,
            "best_checkpoint": self.best_checkpoint,
            "avg_loss": np.mean(losses) if losses else None,
            "min_loss": np.min(losses) if losses else None,
            "max_loss": np.max(losses) if losses else None,
        }

        # Add custom metrics if available
        latest = self.get_latest_metrics()
        if latest:
            if latest.json_valid_rate is not None:
                summary["json_valid_rate"] = latest.json_valid_rate
            if latest.citation_coverage_rate is not None:
                summary["citation_coverage_rate"] = latest.citation_coverage_rate
            if latest.refusal_correctness_rate is not None:
                summary["refusal_correctness_rate"] = latest.refusal_correctness_rate
            if latest.retrieval_groundedness_rate is not None:
                summary["retrieval_groundedness_rate"] = (
                    latest.retrieval_groundedness_rate
                )

        return summary

    def save_summary(self) -> None:
        """Save training summary to file."""
        summary = self.get_metrics_summary()
        with open(self.summary_file, "w") as f:
            json.dump(summary, f, indent=2)

    def load_metrics_history(self) -> None:
        """Load metrics history from file."""
        if not self.metrics_file.exists():
            return

        self.metrics_history = []
        with open(self.metrics_file, "r") as f:
            for line in f:
                metrics_dict = json.loads(line)
                metrics = TrainingMetrics(**metrics_dict)
                self.metrics_history.append(metrics)


def compute_perplexity(loss: float) -> float:
    """
    Compute perplexity from loss.

    Args:
        loss: Cross-entropy loss

    Returns:
        Perplexity value
    """
    try:
        return math.exp(loss)
    except OverflowError:
        return float("inf")


def compute_citation_rate(
    generated_texts: List[str], expected_citations: bool = True
) -> float:
    """
    Compute citation coverage rate.

    Args:
        generated_texts: List of generated text samples
        expected_citations: Whether citations were expected

    Returns:
        Proportion of texts with proper citations
    """
    if not generated_texts:
        return 0.0

    # Citation patterns: [1], [2], [source], etc.
    citation_pattern = r"\[(?:\d+|[A-Za-z0-9_-]+)\]"

    texts_with_citations = 0
    for text in generated_texts:
        if re.search(citation_pattern, text):
            texts_with_citations += 1

    return texts_with_citations / len(generated_texts)


def compute_json_validity_rate(generated_texts: List[str]) -> float:
    """
    Compute rate of valid JSON outputs.

    Args:
        generated_texts: List of generated text samples

    Returns:
        Proportion of valid JSON outputs
    """
    if not generated_texts:
        return 0.0

    valid_json_count = 0
    for text in generated_texts:
        try:
            # Try to extract JSON from text
            json_match = re.search(r"\{.*\}", text, re.DOTALL)
            if json_match:
                json.loads(json_match.group())
                valid_json_count += 1
        except (json.JSONDecodeError, AttributeError):
            continue

    return valid_json_count / len(generated_texts)


def compute_refusal_correctness_rate(
    generated_texts: List[str], expected_refusals: List[bool]
) -> float:
    """
    Compute rate of correct refusal behavior.

    Args:
        generated_texts: List of generated text samples
        expected_refusals: List indicating whether refusal was expected

    Returns:
        Proportion of correct refusal/non-refusal responses
    """
    if not generated_texts or len(generated_texts) != len(expected_refusals):
        return 0.0

    # Refusal indicators
    refusal_patterns = [
        r"I don't have",
        r"I cannot",
        r"I'm not able to",
        r"insufficient information",
        r"not found in",
        r"no information",
    ]
    refusal_regex = re.compile("|".join(refusal_patterns), re.IGNORECASE)

    correct_count = 0
    for text, expected_refusal in zip(generated_texts, expected_refusals):
        has_refusal = bool(refusal_regex.search(text))
        if has_refusal == expected_refusal:
            correct_count += 1

    return correct_count / len(generated_texts)


def compute_retrieval_groundedness_rate(
    generated_texts: List[str], context_texts: List[str]
) -> float:
    """
    Compute rate of responses grounded in provided context.

    Simple implementation based on token overlap.

    Args:
        generated_texts: List of generated text samples
        context_texts: List of context/retrieved text

    Returns:
        Average groundedness score
    """
    if not generated_texts or len(generated_texts) != len(context_texts):
        return 0.0

    groundedness_scores = []
    for generated, context in zip(generated_texts, context_texts):
        # Simple token overlap metric
        gen_tokens = set(generated.lower().split())
        ctx_tokens = set(context.lower().split())

        if not gen_tokens:
            groundedness_scores.append(0.0)
            continue

        overlap = len(gen_tokens & ctx_tokens)
        score = overlap / len(gen_tokens)
        groundedness_scores.append(score)

    return np.mean(groundedness_scores)


def log_training_progress(
    step: int,
    total_steps: int,
    metrics: TrainingMetrics,
    log_interval: int = 10,
) -> None:
    """
    Log training progress to console.

    Args:
        step: Current training step
        total_steps: Total number of steps
        metrics: Current metrics
        log_interval: Log every N steps
    """
    if step % log_interval != 0:
        return

    progress = 100 * step / total_steps
    log_msg = (
        f"Step {step}/{total_steps} ({progress:.1f}%) | "
        f"Loss: {metrics.loss:.4f}"
    )

    if metrics.eval_loss is not None:
        log_msg += f" | Eval Loss: {metrics.eval_loss:.4f}"

    if metrics.perplexity is not None:
        log_msg += f" | PPL: {metrics.perplexity:.2f}"

    if metrics.learning_rate > 0:
        log_msg += f" | LR: {metrics.learning_rate:.2e}"

    print(log_msg)


def compute_gradient_norm(model: torch.nn.Module) -> float:
    """
    Compute total gradient norm across all parameters.

    Args:
        model: Model to compute gradient norm for

    Returns:
        Total gradient norm
    """
    total_norm = 0.0
    for p in model.parameters():
        if p.grad is not None:
            param_norm = p.grad.data.norm(2)
            total_norm += param_norm.item() ** 2
    total_norm = total_norm**0.5
    return total_norm
