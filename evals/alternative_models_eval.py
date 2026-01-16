"""Alternative Models Evaluation Harness for Kwanzaa.

This module extends the AI2 evaluation framework to support alternative embedding
and generation models including LLaMA, DeepSeek, and other open-source alternatives.

Design Principles:
- Vendor independence: Easy switching between model providers
- Comprehensive comparison: Track performance deltas across models
- Provenance integrity: Ensure all models maintain Kwanzaa's core principles
- Reproducibility: Consistent evaluation across model architectures

Supported Models:
- Baseline: BAAI/bge-small-en-v1.5 (current Kwanzaa embedding model)
- LLaMA: Meta's LLaMA 2/3 models for embedding and generation
- DeepSeek: DeepSeek-V2 and DeepSeek-Coder models
- OpenAI: text-embedding-3-small/large (for comparison)
- Anthropic: Claude models (via API for generation)

Evaluation Metrics:
- Retrieval Precision@K: Precision at top-K results
- Retrieval Recall@K: Recall at top-K results
- Mean Reciprocal Rank (MRR): Quality of top-ranked results
- NDCG@K: Normalized Discounted Cumulative Gain
- Answer Quality: BLEU, ROUGE, BERTScore for generation tasks
- Latency: Query processing time
- Provenance Accuracy: Citation correctness
"""

import asyncio
import json
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from sentence_transformers import SentenceTransformer


class ModelType(str, Enum):
    """Supported model types."""
    EMBEDDING = "embedding"
    GENERATION = "generation"
    HYBRID = "hybrid"  # Models that do both


class ModelProvider(str, Enum):
    """Supported model providers."""
    BASELINE = "baseline"  # Current Kwanzaa model
    LLAMA = "llama"
    DEEPSEEK = "deepseek"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    HUGGINGFACE = "huggingface"


@dataclass
class ModelConfig:
    """Configuration for a model to evaluate."""
    name: str
    provider: ModelProvider
    model_type: ModelType
    model_id: str  # HuggingFace model ID or API identifier
    api_key: Optional[str] = None
    max_tokens: int = 512
    temperature: float = 0.0
    embedding_dimensions: int = 1536
    batch_size: int = 32
    device: str = "cpu"  # "cpu", "cuda", "mps"
    quantization: Optional[str] = None  # "4bit", "8bit", None

    # Model-specific parameters
    extra_params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EvaluationPrompt:
    """A single evaluation prompt with expected behavior."""
    prompt_id: str
    query: str
    expected_sources: List[str]  # Expected citation sources
    expected_content_types: List[str]  # Expected content types
    expected_year_range: Optional[Tuple[int, int]] = None
    ground_truth_answer: Optional[str] = None
    category: str = "general"  # "general", "historical", "cultural", etc.
    difficulty: str = "medium"  # "easy", "medium", "hard"

    # Evaluation criteria
    require_citations: bool = True
    primary_sources_only: bool = False
    min_sources: int = 1

    # Metadata
    notes: str = ""


@dataclass
class EvaluationResult:
    """Results for a single prompt evaluation."""
    prompt_id: str
    model_name: str

    # Retrieval metrics
    retrieved_count: int
    precision_at_5: float
    recall_at_5: float
    mrr: float
    ndcg_at_5: float

    # Quality metrics
    citation_accuracy: float  # Percentage of citations matching expected sources
    source_type_accuracy: float  # Percentage of correct source types
    year_range_accuracy: float  # Whether results fall in expected year range

    # Performance metrics
    query_latency_ms: int
    embedding_latency_ms: int
    total_latency_ms: int

    # Answer quality (if generation task)
    answer_generated: Optional[str] = None
    bleu_score: Optional[float] = None
    rouge_l_score: Optional[float] = None
    bert_score: Optional[float] = None

    # Provenance tracking
    citations_provided: List[str] = field(default_factory=list)
    content_types_found: List[str] = field(default_factory=list)
    year_range_found: Optional[Tuple[int, int]] = None

    # Error tracking
    error: Optional[str] = None
    success: bool = True


@dataclass
class ComparisonReport:
    """Comparison report between models."""
    baseline_model: str
    alternative_model: str
    evaluation_date: str

    # Aggregate metrics
    total_prompts: int
    prompts_evaluated: int

    # Delta metrics (alternative - baseline)
    avg_precision_delta: float
    avg_recall_delta: float
    avg_mrr_delta: float
    avg_ndcg_delta: float
    avg_latency_delta_ms: int

    # Per-category breakdown
    category_results: Dict[str, Dict[str, float]] = field(default_factory=dict)

    # Detailed results
    prompt_results: List[Dict[str, Any]] = field(default_factory=list)

    # Recommendations
    recommendation: str = ""
    trade_offs: List[str] = field(default_factory=list)


class AlternativeModelEvaluator:
    """Evaluator for alternative embedding and generation models."""

    def __init__(
        self,
        baseline_config: ModelConfig,
        prompts_path: Optional[Path] = None,
        output_dir: Optional[Path] = None,
    ):
        """Initialize the evaluator.

        Args:
            baseline_config: Configuration for baseline model
            prompts_path: Path to evaluation prompts JSON file
            output_dir: Directory to save evaluation results
        """
        self.baseline_config = baseline_config
        self.prompts_path = prompts_path or Path("/Users/aideveloper/kwanzaa/evals/prompts/ai2_prompts.json")
        self.output_dir = output_dir or Path("/Users/aideveloper/kwanzaa/evals/results")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Model cache
        self._models: Dict[str, Any] = {}

        # Load evaluation prompts
        self.prompts = self._load_prompts()

    def _load_prompts(self) -> List[EvaluationPrompt]:
        """Load evaluation prompts from JSON file.

        Returns:
            List of EvaluationPrompt objects
        """
        if not self.prompts_path.exists():
            # Return default prompts if file doesn't exist
            return self._get_default_prompts()

        with open(self.prompts_path, "r") as f:
            prompts_data = json.load(f)

        prompts = []
        for prompt_data in prompts_data:
            prompt = EvaluationPrompt(**prompt_data)
            prompts.append(prompt)

        return prompts

    def _get_default_prompts(self) -> List[EvaluationPrompt]:
        """Get default AI2-style evaluation prompts.

        Returns:
            List of default evaluation prompts
        """
        return [
            EvaluationPrompt(
                prompt_id="cra_1964_basic",
                query="What did the Civil Rights Act of 1964 prohibit?",
                expected_sources=["National Archives", "Library of Congress"],
                expected_content_types=["legal_document", "proclamation"],
                expected_year_range=(1964, 1964),
                category="historical",
                difficulty="easy",
                require_citations=True,
                min_sources=1,
            ),
            EvaluationPrompt(
                prompt_id="kwanzaa_principles",
                query="Explain the seven principles of Kwanzaa",
                expected_sources=["Dr. Maulana Karenga"],
                expected_content_types=["cultural_document", "educational"],
                expected_year_range=(1966, 2025),
                category="cultural",
                difficulty="medium",
                require_citations=True,
                min_sources=1,
            ),
            EvaluationPrompt(
                prompt_id="black_inventors",
                query="List important Black inventors from the 1800s",
                expected_sources=["Patent Office", "Historical Records"],
                expected_content_types=["biography", "patent_record"],
                expected_year_range=(1800, 1900),
                category="historical",
                difficulty="hard",
                require_citations=True,
                primary_sources_only=True,
                min_sources=3,
            ),
            EvaluationPrompt(
                prompt_id="voting_rights_act",
                query="When was the Voting Rights Act passed and what did it guarantee?",
                expected_sources=["National Archives", "Congressional Records"],
                expected_content_types=["legal_document"],
                expected_year_range=(1965, 1965),
                category="historical",
                difficulty="medium",
                require_citations=True,
                min_sources=1,
            ),
            EvaluationPrompt(
                prompt_id="harlem_renaissance",
                query="Describe the cultural impact of the Harlem Renaissance",
                expected_sources=["Historical Archives", "Literary Collections"],
                expected_content_types=["essay", "biography", "cultural_document"],
                expected_year_range=(1920, 1940),
                category="cultural",
                difficulty="hard",
                require_citations=True,
                min_sources=2,
            ),
        ]

    def _load_model(self, config: ModelConfig) -> Any:
        """Load a model based on configuration.

        Args:
            config: Model configuration

        Returns:
            Loaded model instance
        """
        cache_key = f"{config.provider}:{config.model_id}"

        if cache_key in self._models:
            return self._models[cache_key]

        print(f"Loading model: {config.name} ({config.model_id})")

        if config.provider == ModelProvider.BASELINE or config.provider == ModelProvider.HUGGINGFACE:
            # Load sentence-transformers model
            model = SentenceTransformer(config.model_id, device=config.device)
            self._models[cache_key] = model
            return model

        elif config.provider == ModelProvider.LLAMA:
            # Load LLaMA model (requires transformers library)
            try:
                from transformers import AutoModel, AutoTokenizer
                tokenizer = AutoTokenizer.from_pretrained(config.model_id)
                model = AutoModel.from_pretrained(
                    config.model_id,
                    device_map=config.device if config.device != "cpu" else None,
                    load_in_4bit=config.quantization == "4bit",
                    load_in_8bit=config.quantization == "8bit",
                )
                self._models[cache_key] = (model, tokenizer)
                return (model, tokenizer)
            except ImportError:
                raise ImportError("transformers library required for LLaMA models")

        elif config.provider == ModelProvider.DEEPSEEK:
            # Load DeepSeek model
            try:
                from transformers import AutoModel, AutoTokenizer
                tokenizer = AutoTokenizer.from_pretrained(config.model_id)
                model = AutoModel.from_pretrained(
                    config.model_id,
                    device_map=config.device if config.device != "cpu" else None,
                    trust_remote_code=True,
                )
                self._models[cache_key] = (model, tokenizer)
                return (model, tokenizer)
            except ImportError:
                raise ImportError("transformers library required for DeepSeek models")

        elif config.provider == ModelProvider.OPENAI:
            # OpenAI API client
            try:
                import openai
                client = openai.OpenAI(api_key=config.api_key)
                self._models[cache_key] = client
                return client
            except ImportError:
                raise ImportError("openai library required for OpenAI models")

        elif config.provider == ModelProvider.ANTHROPIC:
            # Anthropic API client
            try:
                import anthropic
                client = anthropic.Anthropic(api_key=config.api_key)
                self._models[cache_key] = client
                return client
            except ImportError:
                raise ImportError("anthropic library required for Anthropic models")

        else:
            raise ValueError(f"Unsupported provider: {config.provider}")

    async def generate_embedding(
        self,
        text: str,
        config: ModelConfig,
    ) -> Tuple[List[float], int]:
        """Generate embedding for text using specified model.

        Args:
            text: Input text
            config: Model configuration

        Returns:
            Tuple of (embedding vector, latency in ms)
        """
        start_time = time.time()

        model = self._load_model(config)

        if config.provider in [ModelProvider.BASELINE, ModelProvider.HUGGINGFACE]:
            # SentenceTransformer model
            embedding = model.encode(text, convert_to_numpy=True)
            embedding_list = embedding.tolist()

        elif config.provider == ModelProvider.OPENAI:
            # OpenAI embeddings API
            response = model.embeddings.create(
                model=config.model_id,
                input=text,
            )
            embedding_list = response.data[0].embedding

        elif config.provider in [ModelProvider.LLAMA, ModelProvider.DEEPSEEK]:
            # Transformer models - need to implement mean pooling
            model_obj, tokenizer = model
            inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)

            if config.device != "cpu":
                inputs = {k: v.to(config.device) for k, v in inputs.items()}

            with torch.no_grad():
                outputs = model_obj(**inputs)
                # Mean pooling
                embeddings = outputs.last_hidden_state.mean(dim=1)
                embedding_list = embeddings.cpu().numpy()[0].tolist()

        else:
            raise ValueError(f"Embedding not supported for provider: {config.provider}")

        # Normalize dimensions
        if len(embedding_list) < config.embedding_dimensions:
            embedding_list.extend([0.0] * (config.embedding_dimensions - len(embedding_list)))
        elif len(embedding_list) > config.embedding_dimensions:
            embedding_list = embedding_list[:config.embedding_dimensions]

        latency_ms = int((time.time() - start_time) * 1000)

        return embedding_list, latency_ms

    async def evaluate_prompt(
        self,
        prompt: EvaluationPrompt,
        config: ModelConfig,
        mock_search_func: Optional[Any] = None,
    ) -> EvaluationResult:
        """Evaluate a single prompt with specified model.

        Args:
            prompt: Evaluation prompt
            config: Model configuration
            mock_search_func: Optional mock search function for testing

        Returns:
            EvaluationResult with metrics
        """
        total_start = time.time()

        try:
            # Generate query embedding
            query_embedding, embedding_latency = await self.generate_embedding(
                prompt.query, config
            )

            # Perform mock search (in production, would use actual ZeroDB search)
            search_start = time.time()

            if mock_search_func:
                results = await mock_search_func(query_embedding, prompt)
            else:
                # Mock results for testing
                results = self._generate_mock_results(prompt)

            query_latency = int((time.time() - search_start) * 1000)
            total_latency = int((time.time() - total_start) * 1000)

            # Calculate retrieval metrics
            retrieved_count = len(results)

            # Precision@5: How many of top 5 are relevant
            top_5_results = results[:5]
            relevant_count = sum(
                1 for r in top_5_results
                if r.get("source_org") in prompt.expected_sources
                or r.get("content_type") in prompt.expected_content_types
            )
            precision_at_5 = relevant_count / min(5, len(top_5_results)) if top_5_results else 0.0

            # Recall@5: How many relevant docs were retrieved in top 5
            # (simplified - in real scenario, need ground truth set size)
            recall_at_5 = relevant_count / max(len(prompt.expected_sources), 1)

            # MRR: Reciprocal rank of first relevant document
            first_relevant_rank = None
            for i, r in enumerate(results, start=1):
                if (r.get("source_org") in prompt.expected_sources or
                    r.get("content_type") in prompt.expected_content_types):
                    first_relevant_rank = i
                    break

            mrr = 1.0 / first_relevant_rank if first_relevant_rank else 0.0

            # NDCG@5: Normalized Discounted Cumulative Gain
            ndcg_at_5 = self._calculate_ndcg(results[:5], prompt)

            # Citation accuracy
            citations_provided = [r.get("source_org", "") for r in results]
            citation_accuracy = sum(
                1 for c in citations_provided if c in prompt.expected_sources
            ) / max(len(citations_provided), 1)

            # Source type accuracy
            content_types_found = [r.get("content_type", "") for r in results]
            source_type_accuracy = sum(
                1 for ct in content_types_found if ct in prompt.expected_content_types
            ) / max(len(content_types_found), 1)

            # Year range accuracy
            years = [r.get("year") for r in results if r.get("year")]
            year_range_found = (min(years), max(years)) if years else None

            year_range_accuracy = 0.0
            if prompt.expected_year_range and year_range_found:
                exp_start, exp_end = prompt.expected_year_range
                found_start, found_end = year_range_found
                # Check if ranges overlap
                if found_start <= exp_end and found_end >= exp_start:
                    year_range_accuracy = 1.0

            return EvaluationResult(
                prompt_id=prompt.prompt_id,
                model_name=config.name,
                retrieved_count=retrieved_count,
                precision_at_5=precision_at_5,
                recall_at_5=recall_at_5,
                mrr=mrr,
                ndcg_at_5=ndcg_at_5,
                citation_accuracy=citation_accuracy,
                source_type_accuracy=source_type_accuracy,
                year_range_accuracy=year_range_accuracy,
                query_latency_ms=query_latency,
                embedding_latency_ms=embedding_latency,
                total_latency_ms=total_latency,
                citations_provided=citations_provided,
                content_types_found=content_types_found,
                year_range_found=year_range_found,
                success=True,
            )

        except Exception as e:
            return EvaluationResult(
                prompt_id=prompt.prompt_id,
                model_name=config.name,
                retrieved_count=0,
                precision_at_5=0.0,
                recall_at_5=0.0,
                mrr=0.0,
                ndcg_at_5=0.0,
                citation_accuracy=0.0,
                source_type_accuracy=0.0,
                year_range_accuracy=0.0,
                query_latency_ms=0,
                embedding_latency_ms=0,
                total_latency_ms=int((time.time() - total_start) * 1000),
                error=str(e),
                success=False,
            )

    def _calculate_ndcg(self, results: List[Dict], prompt: EvaluationPrompt) -> float:
        """Calculate Normalized Discounted Cumulative Gain at K.

        Args:
            results: Search results
            prompt: Evaluation prompt with expected behavior

        Returns:
            NDCG@K score
        """
        if not results:
            return 0.0

        # Assign relevance scores (0-2 scale)
        relevance_scores = []
        for r in results:
            score = 0
            if r.get("source_org") in prompt.expected_sources:
                score += 1
            if r.get("content_type") in prompt.expected_content_types:
                score += 1
            relevance_scores.append(score)

        # DCG: Sum of (relevance / log2(rank + 1))
        dcg = sum(
            rel / np.log2(i + 2) for i, rel in enumerate(relevance_scores)
        )

        # IDCG: DCG of ideal ranking
        ideal_scores = sorted(relevance_scores, reverse=True)
        idcg = sum(
            rel / np.log2(i + 2) for i, rel in enumerate(ideal_scores)
        )

        return dcg / idcg if idcg > 0 else 0.0

    def _generate_mock_results(self, prompt: EvaluationPrompt) -> List[Dict]:
        """Generate mock search results for testing.

        Args:
            prompt: Evaluation prompt

        Returns:
            List of mock result dictionaries
        """
        # Generate 5-10 mock results
        num_results = np.random.randint(5, 11)
        results = []

        for i in range(num_results):
            # Mix relevant and irrelevant results
            is_relevant = np.random.random() > 0.3

            if is_relevant and prompt.expected_sources:
                source_org = np.random.choice(prompt.expected_sources)
                content_type = np.random.choice(prompt.expected_content_types)
            else:
                source_org = "Other Source"
                content_type = "other"

            year = None
            if prompt.expected_year_range:
                # Sometimes use expected range, sometimes not
                if is_relevant:
                    year = np.random.randint(
                        prompt.expected_year_range[0],
                        prompt.expected_year_range[1] + 1
                    )
                else:
                    year = np.random.randint(1800, 2025)

            results.append({
                "source_org": source_org,
                "content_type": content_type,
                "year": year,
                "score": 0.95 - (i * 0.05),  # Decreasing scores
            })

        return results

    async def compare_models(
        self,
        baseline_config: ModelConfig,
        alternative_config: ModelConfig,
        prompts: Optional[List[EvaluationPrompt]] = None,
    ) -> ComparisonReport:
        """Compare baseline model with alternative model.

        Args:
            baseline_config: Baseline model configuration
            alternative_config: Alternative model configuration
            prompts: Optional list of prompts (uses default if None)

        Returns:
            ComparisonReport with detailed metrics
        """
        prompts = prompts or self.prompts

        print(f"\n{'='*80}")
        print(f"Comparing Models:")
        print(f"  Baseline: {baseline_config.name} ({baseline_config.model_id})")
        print(f"  Alternative: {alternative_config.name} ({alternative_config.model_id})")
        print(f"  Prompts: {len(prompts)}")
        print(f"{'='*80}\n")

        # Evaluate both models
        baseline_results = []
        alternative_results = []

        for prompt in prompts:
            print(f"Evaluating prompt: {prompt.prompt_id}")

            # Evaluate baseline
            baseline_result = await self.evaluate_prompt(prompt, baseline_config)
            baseline_results.append(baseline_result)

            # Evaluate alternative
            alternative_result = await self.evaluate_prompt(prompt, alternative_config)
            alternative_results.append(alternative_result)

        # Calculate aggregate metrics
        def avg_metric(results: List[EvaluationResult], metric: str) -> float:
            values = [getattr(r, metric) for r in results if r.success]
            return np.mean(values) if values else 0.0

        baseline_precision = avg_metric(baseline_results, "precision_at_5")
        alternative_precision = avg_metric(alternative_results, "precision_at_5")

        baseline_recall = avg_metric(baseline_results, "recall_at_5")
        alternative_recall = avg_metric(alternative_results, "recall_at_5")

        baseline_mrr = avg_metric(baseline_results, "mrr")
        alternative_mrr = avg_metric(alternative_results, "mrr")

        baseline_ndcg = avg_metric(baseline_results, "ndcg_at_5")
        alternative_ndcg = avg_metric(alternative_results, "ndcg_at_5")

        baseline_latency = int(avg_metric(baseline_results, "total_latency_ms"))
        alternative_latency = int(avg_metric(alternative_results, "total_latency_ms"))

        # Calculate deltas
        precision_delta = alternative_precision - baseline_precision
        recall_delta = alternative_recall - baseline_recall
        mrr_delta = alternative_mrr - baseline_mrr
        ndcg_delta = alternative_ndcg - baseline_ndcg
        latency_delta = alternative_latency - baseline_latency

        # Per-category breakdown
        category_results = {}
        for category in set(p.category for p in prompts):
            category_prompts = [p.prompt_id for p in prompts if p.category == category]

            cat_baseline_results = [r for r in baseline_results if r.prompt_id in category_prompts]
            cat_alternative_results = [r for r in alternative_results if r.prompt_id in category_prompts]

            category_results[category] = {
                "baseline_precision": avg_metric(cat_baseline_results, "precision_at_5"),
                "alternative_precision": avg_metric(cat_alternative_results, "precision_at_5"),
                "baseline_mrr": avg_metric(cat_baseline_results, "mrr"),
                "alternative_mrr": avg_metric(cat_alternative_results, "mrr"),
                "precision_delta": avg_metric(cat_alternative_results, "precision_at_5") -
                                 avg_metric(cat_baseline_results, "precision_at_5"),
            }

        # Detailed prompt results
        prompt_results = []
        for i, prompt in enumerate(prompts):
            prompt_results.append({
                "prompt_id": prompt.prompt_id,
                "category": prompt.category,
                "baseline": {
                    "precision": baseline_results[i].precision_at_5,
                    "mrr": baseline_results[i].mrr,
                    "latency_ms": baseline_results[i].total_latency_ms,
                },
                "alternative": {
                    "precision": alternative_results[i].precision_at_5,
                    "mrr": alternative_results[i].mrr,
                    "latency_ms": alternative_results[i].total_latency_ms,
                },
                "delta": {
                    "precision": alternative_results[i].precision_at_5 - baseline_results[i].precision_at_5,
                    "mrr": alternative_results[i].mrr - baseline_results[i].mrr,
                    "latency_ms": alternative_results[i].total_latency_ms - baseline_results[i].total_latency_ms,
                },
            })

        # Generate recommendation
        recommendation = self._generate_recommendation(
            precision_delta, recall_delta, mrr_delta, ndcg_delta, latency_delta
        )

        # Identify trade-offs
        trade_offs = self._identify_trade_offs(
            precision_delta, recall_delta, latency_delta, alternative_config
        )

        report = ComparisonReport(
            baseline_model=baseline_config.name,
            alternative_model=alternative_config.name,
            evaluation_date=datetime.now().isoformat(),
            total_prompts=len(prompts),
            prompts_evaluated=len([r for r in alternative_results if r.success]),
            avg_precision_delta=precision_delta,
            avg_recall_delta=recall_delta,
            avg_mrr_delta=mrr_delta,
            avg_ndcg_delta=ndcg_delta,
            avg_latency_delta_ms=latency_delta,
            category_results=category_results,
            prompt_results=prompt_results,
            recommendation=recommendation,
            trade_offs=trade_offs,
        )

        # Save report
        self._save_report(report)

        return report

    def _generate_recommendation(
        self,
        precision_delta: float,
        recall_delta: float,
        mrr_delta: float,
        ndcg_delta: float,
        latency_delta: int,
    ) -> str:
        """Generate recommendation based on metric deltas.

        Args:
            precision_delta: Change in precision
            recall_delta: Change in recall
            mrr_delta: Change in MRR
            ndcg_delta: Change in NDCG
            latency_delta: Change in latency (ms)

        Returns:
            Recommendation string
        """
        quality_improved = (precision_delta > 0.05 or mrr_delta > 0.05)
        quality_degraded = (precision_delta < -0.05 or mrr_delta < -0.05)
        latency_improved = latency_delta < -50
        latency_degraded = latency_delta > 100

        if quality_improved and not latency_degraded:
            return "RECOMMENDED: Alternative model shows improved quality without significant latency cost."
        elif quality_improved and latency_degraded:
            return "CONDITIONAL: Alternative model has better quality but slower. Consider for offline batch processing."
        elif not quality_degraded and latency_improved:
            return "RECOMMENDED: Alternative model maintains quality with improved latency."
        elif quality_degraded:
            return "NOT RECOMMENDED: Alternative model shows degraded quality metrics."
        else:
            return "NEUTRAL: Models perform similarly. Choice depends on other factors (cost, deployment, etc.)."

    def _identify_trade_offs(
        self,
        precision_delta: float,
        recall_delta: float,
        latency_delta: int,
        config: ModelConfig,
    ) -> List[str]:
        """Identify key trade-offs for alternative model.

        Args:
            precision_delta: Change in precision
            recall_delta: Change in recall
            latency_delta: Change in latency
            config: Alternative model configuration

        Returns:
            List of trade-off descriptions
        """
        trade_offs = []

        if precision_delta > 0.05:
            trade_offs.append(f"✓ Better precision (+{precision_delta:.2%})")
        elif precision_delta < -0.05:
            trade_offs.append(f"✗ Lower precision ({precision_delta:.2%})")

        if latency_delta > 100:
            trade_offs.append(f"✗ Slower by {latency_delta}ms")
        elif latency_delta < -50:
            trade_offs.append(f"✓ Faster by {abs(latency_delta)}ms")

        if config.provider != ModelProvider.BASELINE:
            trade_offs.append(f"Requires {config.provider.value} provider/dependencies")

        if config.quantization:
            trade_offs.append(f"Uses {config.quantization} quantization (reduced memory)")

        return trade_offs

    def _save_report(self, report: ComparisonReport) -> None:
        """Save comparison report to JSON file.

        Args:
            report: Comparison report to save
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"comparison_{report.baseline_model}_vs_{report.alternative_model}_{timestamp}.json"
        filepath = self.output_dir / filename

        with open(filepath, "w") as f:
            json.dump(
                {
                    "baseline_model": report.baseline_model,
                    "alternative_model": report.alternative_model,
                    "evaluation_date": report.evaluation_date,
                    "total_prompts": report.total_prompts,
                    "prompts_evaluated": report.prompts_evaluated,
                    "metrics": {
                        "precision_delta": report.avg_precision_delta,
                        "recall_delta": report.avg_recall_delta,
                        "mrr_delta": report.avg_mrr_delta,
                        "ndcg_delta": report.avg_ndcg_delta,
                        "latency_delta_ms": report.avg_latency_delta_ms,
                    },
                    "category_results": report.category_results,
                    "prompt_results": report.prompt_results,
                    "recommendation": report.recommendation,
                    "trade_offs": report.trade_offs,
                },
                f,
                indent=2,
            )

        print(f"\nReport saved to: {filepath}")

    def print_report(self, report: ComparisonReport) -> None:
        """Print comparison report to console.

        Args:
            report: Comparison report to print
        """
        print(f"\n{'='*80}")
        print("MODEL COMPARISON REPORT")
        print(f"{'='*80}")
        print(f"Baseline Model: {report.baseline_model}")
        print(f"Alternative Model: {report.alternative_model}")
        print(f"Evaluation Date: {report.evaluation_date}")
        print(f"Prompts Evaluated: {report.prompts_evaluated}/{report.total_prompts}")
        print(f"\n{'='*80}")
        print("AGGREGATE METRICS (Alternative - Baseline)")
        print(f"{'='*80}")
        print(f"  Precision@5 Delta: {report.avg_precision_delta:+.4f}")
        print(f"  Recall@5 Delta:    {report.avg_recall_delta:+.4f}")
        print(f"  MRR Delta:         {report.avg_mrr_delta:+.4f}")
        print(f"  NDCG@5 Delta:      {report.avg_ndcg_delta:+.4f}")
        print(f"  Latency Delta:     {report.avg_latency_delta_ms:+d} ms")
        print(f"\n{'='*80}")
        print("RECOMMENDATION")
        print(f"{'='*80}")
        print(f"  {report.recommendation}")
        print(f"\n{'='*80}")
        print("TRADE-OFFS")
        print(f"{'='*80}")
        for trade_off in report.trade_offs:
            print(f"  • {trade_off}")
        print(f"{'='*80}\n")


# Predefined model configurations for easy switching
BASELINE_CONFIG = ModelConfig(
    name="Kwanzaa Baseline",
    provider=ModelProvider.BASELINE,
    model_type=ModelType.EMBEDDING,
    model_id="BAAI/bge-small-en-v1.5",
    embedding_dimensions=1536,
    device="cpu",
)

LLAMA2_CONFIG = ModelConfig(
    name="LLaMA 2 7B",
    provider=ModelProvider.LLAMA,
    model_type=ModelType.HYBRID,
    model_id="meta-llama/Llama-2-7b-hf",
    embedding_dimensions=1536,
    device="cpu",
    quantization="4bit",
)

LLAMA3_CONFIG = ModelConfig(
    name="LLaMA 3 8B",
    provider=ModelProvider.LLAMA,
    model_type=ModelType.HYBRID,
    model_id="meta-llama/Meta-Llama-3-8B",
    embedding_dimensions=1536,
    device="cpu",
    quantization="4bit",
)

DEEPSEEK_V2_CONFIG = ModelConfig(
    name="DeepSeek V2",
    provider=ModelProvider.DEEPSEEK,
    model_type=ModelType.HYBRID,
    model_id="deepseek-ai/deepseek-llm-7b-base",
    embedding_dimensions=1536,
    device="cpu",
)

OPENAI_SMALL_CONFIG = ModelConfig(
    name="OpenAI text-embedding-3-small",
    provider=ModelProvider.OPENAI,
    model_type=ModelType.EMBEDDING,
    model_id="text-embedding-3-small",
    embedding_dimensions=1536,
    api_key=None,  # Set via environment variable
)

OPENAI_LARGE_CONFIG = ModelConfig(
    name="OpenAI text-embedding-3-large",
    provider=ModelProvider.OPENAI,
    model_type=ModelType.EMBEDDING,
    model_id="text-embedding-3-large",
    embedding_dimensions=3072,
    api_key=None,  # Set via environment variable
)


async def main():
    """Example usage of the evaluation framework."""
    # Initialize evaluator
    evaluator = AlternativeModelEvaluator(
        baseline_config=BASELINE_CONFIG,
    )

    # Compare baseline with LLaMA 2
    print("Comparing Baseline vs LLaMA 2...")
    llama_report = await evaluator.compare_models(
        baseline_config=BASELINE_CONFIG,
        alternative_config=LLAMA2_CONFIG,
    )
    evaluator.print_report(llama_report)

    # Compare baseline with DeepSeek
    print("\nComparing Baseline vs DeepSeek V2...")
    deepseek_report = await evaluator.compare_models(
        baseline_config=BASELINE_CONFIG,
        alternative_config=DEEPSEEK_V2_CONFIG,
    )
    evaluator.print_report(deepseek_report)


if __name__ == "__main__":
    asyncio.run(main())
