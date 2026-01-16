# Adapter Training Pipeline Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    Adapter Training Pipeline                     │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────┐
│   User Interface    │
│  (CLI/Commands)     │
└──────────┬──────────┘
           │
           v
┌─────────────────────────────────────────────────────────────────┐
│                     train_adapter.py                             │
│  - Configuration loading                                         │
│  - Training orchestration                                        │
│  - Verification workflow                                         │
└───────┬──────────────────────────────────┬──────────────────────┘
        │                                  │
        v                                  v
┌───────────────────┐           ┌──────────────────────┐
│  Configuration    │           │   Utility Modules    │
│                   │           │                      │
│  training.yaml    │           │  - artifacts.py      │
│  qlora.yaml       │           │  - verification.py   │
│  ai2.yaml         │           │  - metrics.py        │
└───────────────────┘           └──────────────────────┘
```

## Training Workflow

```
┌─────────────┐
│   START     │
└──────┬──────┘
       │
       v
┌─────────────────────────┐
│ 1. Load Configuration   │
│    - training.yaml      │
│    - Validate params    │
└──────┬──────────────────┘
       │
       v
┌─────────────────────────┐
│ 2. Initialize Model     │
│    - Load base model    │
│    - Apply 4-bit quant  │
│    - Add LoRA adapters  │
└──────┬──────────────────┘
       │
       v
┌─────────────────────────┐
│ 3. Save Baseline        │
│    - Compute checksums  │
│    - Save to JSON       │
└──────┬──────────────────┘
       │
       v
┌─────────────────────────┐
│ 4. Load Datasets        │
│    - train.jsonl        │
│    - eval.jsonl         │
│    - Tokenize & prep    │
└──────┬──────────────────┘
       │
       v
┌─────────────────────────┐
│ 5. Training Loop        │
│    - Forward pass       │
│    - Compute loss       │
│    - Backward pass      │
│    - Update adapters    │
│    - Log metrics        │
└──────┬──────────────────┘
       │
       v
┌─────────────────────────┐
│ 6. Verify Weights       │
│    - Recompute checksums│
│    - Compare baseline   │
│    - Report differences │
└──────┬──────────────────┘
       │
       v
┌─────────────────────────┐
│ 7. Create Artifact      │
│    - Save adapter       │
│    - Generate metadata  │
│    - Compute checksums  │
│    - Create README      │
└──────┬──────────────────┘
       │
       v
┌─────────────────────────┐
│ 8. Validate Artifact    │
│    - Check completeness │
│    - Verify integrity   │
└──────┬──────────────────┘
       │
       v
┌─────────────┐
│     END     │
│  (Success)  │
└─────────────┘
```

## Component Architecture

### Core Components

```
┌─────────────────────────────────────────────────────────────────┐
│                     train_adapter.py                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  main()                                                          │
│    └─> train_adapter()                                          │
│         ├─> load_training_config()                              │
│         ├─> setup_model_and_tokenizer()                         │
│         │    ├─> Load base model with quantization             │
│         │    ├─> Apply LoRA config                             │
│         │    └─> Verify trainable params                       │
│         ├─> save_base_model_checksums()                         │
│         ├─> load_and_prepare_dataset()                          │
│         ├─> create_training_arguments()                         │
│         ├─> Trainer.train()                                     │
│         ├─> verify_base_weights_unchanged()                     │
│         ├─> save_adapter_artifact()                             │
│         └─> verify_artifact()                                   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Utility Modules

```
┌─────────────────────────────────────────────────────────────────┐
│                      artifacts.py                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────────────────────────────────┐        │
│  │ Checksum Generation                                 │        │
│  │  - generate_file_checksum()                         │        │
│  │  - generate_artifact_checksum()                     │        │
│  │  - verify_artifact_integrity()                      │        │
│  └─────────────────────────────────────────────────────┘        │
│                                                                  │
│  ┌─────────────────────────────────────────────────────┐        │
│  │ Metadata Management                                 │        │
│  │  - create_artifact_metadata()                       │        │
│  │  - generate_adapter_readme()                        │        │
│  └─────────────────────────────────────────────────────┘        │
│                                                                  │
│  ┌─────────────────────────────────────────────────────┐        │
│  │ Artifact Operations                                 │        │
│  │  - save_adapter_artifact()                          │        │
│  │  - load_artifact_metadata()                         │        │
│  │  - verify_artifact()                                │        │
│  └─────────────────────────────────────────────────────┘        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    verification.py                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────────────────────────────────┐        │
│  │ Weight Verification                                 │        │
│  │  - compute_model_state_checksum()                   │        │
│  │  - save_base_model_checksums()                      │        │
│  │  - compare_model_checksums()                        │        │
│  │  - verify_base_weights_unchanged()                  │        │
│  └─────────────────────────────────────────────────────┘        │
│                                                                  │
│  ┌─────────────────────────────────────────────────────┐        │
│  │ Parameter Analysis                                  │        │
│  │  - get_trainable_parameters_summary()               │        │
│  │  - verify_only_adapter_trainable()                  │        │
│  │  - save_adapter_only_params()                       │        │
│  └─────────────────────────────────────────────────────┘        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                       metrics.py                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────────────────────────────────┐        │
│  │ Metrics Data Structures                             │        │
│  │  - TrainingMetrics (dataclass)                      │        │
│  │  - MetricsTracker (class)                           │        │
│  └─────────────────────────────────────────────────────┘        │
│                                                                  │
│  ┌─────────────────────────────────────────────────────┐        │
│  │ Metric Computation                                  │        │
│  │  - compute_perplexity()                             │        │
│  │  - compute_citation_rate()                          │        │
│  │  - compute_json_validity_rate()                     │        │
│  │  - compute_refusal_correctness_rate()               │        │
│  │  - compute_retrieval_groundedness_rate()            │        │
│  └─────────────────────────────────────────────────────┘        │
│                                                                  │
│  ┌─────────────────────────────────────────────────────┐        │
│  │ Logging & Persistence                               │        │
│  │  - log_training_progress()                          │        │
│  │  - MetricsTracker.log_metrics()                     │        │
│  │  - MetricsTracker.save_summary()                    │        │
│  └─────────────────────────────────────────────────────┘        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow

```
┌──────────────┐
│ Config Files │
│  (YAML)      │
└──────┬───────┘
       │
       v
┌────────────────────────┐      ┌──────────────────┐
│  Training Script       │─────>│  Base Model      │
│  (train_adapter.py)    │      │  (HuggingFace)   │
└───────┬────────────────┘      └──────────────────┘
        │
        v
┌────────────────────────┐
│  Dataset Files         │
│  (train.jsonl/         │
│   eval.jsonl)          │
└───────┬────────────────┘
        │
        v
┌────────────────────────┐
│  Training Process      │
│  - Forward/Backward    │
│  - Gradient Updates    │
└───────┬────────────────┘
        │
        v
┌────────────────────────┐      ┌──────────────────┐
│  Adapter Weights       │─────>│  Artifacts       │
│  (LoRA params only)    │      │  (versioned)     │
└────────────────────────┘      └──────────────────┘
                                         │
                                         v
                                ┌──────────────────┐
                                │  Verification    │
                                │  - Checksums     │
                                │  - Metadata      │
                                └──────────────────┘
```

## Memory Layout (Training)

```
GPU Memory (~12GB total):

┌─────────────────────────────────────────────────────────┐
│  Base Model (4-bit quantized)                   ~4GB   │
├─────────────────────────────────────────────────────────┤
│  LoRA Adapter Parameters                        ~100MB │
├─────────────────────────────────────────────────────────┤
│  Gradients (adapter only)                       ~200MB │
├─────────────────────────────────────────────────────────┤
│  Optimizer State (paged AdamW)                   ~2GB   │
├─────────────────────────────────────────────────────────┤
│  Activations (with gradient checkpointing)       ~4GB   │
├─────────────────────────────────────────────────────────┤
│  CUDA Overhead                                   ~1GB   │
└─────────────────────────────────────────────────────────┘

System RAM (~16GB):

┌─────────────────────────────────────────────────────────┐
│  Dataset (tokenized)                             ~4GB   │
├─────────────────────────────────────────────────────────┤
│  DataLoader Buffers                              ~2GB   │
├─────────────────────────────────────────────────────────┤
│  Python Runtime & Dependencies                   ~8GB   │
├─────────────────────────────────────────────────────────┤
│  OS & Other Processes                            ~2GB   │
└─────────────────────────────────────────────────────────┘
```

## Artifact Structure

```
outputs/kwanzaa-adapter-v0/
│
├── final_artifact/                 # Deployable artifact
│   ├── adapter_config.json         # LoRA configuration
│   ├── adapter_model.safetensors   # Adapter weights (only)
│   ├── metadata.json               # Training provenance
│   ├── training_config.yaml        # Full config snapshot
│   ├── training_metrics.json       # Final metrics
│   ├── checksums.json              # File integrity
│   └── README.md                   # Usage instructions
│
├── adapter/                        # Raw adapter output
│   ├── adapter_config.json
│   └── adapter_model.safetensors
│
├── tensorboard/                    # Training logs
│   └── events.out.tfevents.*
│
├── checkpoint-200/                 # Training checkpoints
├── checkpoint-400/
├── checkpoint-600/
│
├── baseline_checksums.json         # Base model baseline
├── metrics_history.jsonl           # Step-by-step metrics
├── training_summary.json           # Summary statistics
└── training_results.json           # Complete results
```

## Integration Points

```
┌─────────────────────────────────────────────────────────────────┐
│                      Kwanzaa Backend                             │
└─────────────────────────────────────────────────────────────────┘
                              │
                              v
┌─────────────────────────────────────────────────────────────────┐
│                     Model Factory                                │
│  (backend/models/factory.py)                                     │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     v
┌─────────────────────────────────────────────────────────────────┐
│                     AI2 Model                                    │
│  (backend/models/ai2.py)                                         │
│                                                                  │
│  ┌────────────────────────────────────────────────────┐         │
│  │  Load Base Model: allenai/OLMo-7B-Instruct        │         │
│  └────────────────────────────────────────────────────┘         │
│                     │                                            │
│                     v                                            │
│  ┌────────────────────────────────────────────────────┐         │
│  │  Load Adapter (optional):                         │         │
│  │    outputs/kwanzaa-adapter-v0/final_artifact      │         │
│  └────────────────────────────────────────────────────┘         │
│                     │                                            │
│                     v                                            │
│  ┌────────────────────────────────────────────────────┐         │
│  │  Generate Response with Adapter                    │         │
│  └────────────────────────────────────────────────────┘         │
└─────────────────────────────────────────────────────────────────┘
```

## Monitoring & Observability

```
┌─────────────────────────────────────────────────────────────────┐
│                    Training Monitoring                           │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────┐      ┌──────────────────┐      ┌──────────────────┐
│   TensorBoard    │      │  Weights & Biases│      │     MLflow       │
│   (Local)        │      │   (Cloud)        │      │  (Model Registry)│
└────────┬─────────┘      └────────┬─────────┘      └────────┬─────────┘
         │                         │                         │
         └─────────────────────────┴─────────────────────────┘
                                   │
                                   v
         ┌─────────────────────────────────────────────────────┐
         │            Metrics Collection                       │
         │  - Training/Eval Loss                               │
         │  - Perplexity                                       │
         │  - Learning Rate                                    │
         │  - Gradient Norm                                    │
         │  - Custom Metrics (citation rate, JSON validity)    │
         └─────────────────────────────────────────────────────┘
```

## Security & Safety

```
┌─────────────────────────────────────────────────────────────────┐
│                    Safety Mechanisms                             │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│  1. Base Weight Protection                                   │
│     - Save checksums before training                         │
│     - Verify checksums after training                        │
│     - Alert on any modifications                             │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│  2. Artifact Integrity                                       │
│     - SHA256 checksums for all files                         │
│     - Automatic verification on load                         │
│     - Tamper detection                                       │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│  3. Parameter Freeze Verification                            │
│     - Check only adapter params trainable                    │
│     - Verify base model params frozen                        │
│     - Log parameter statistics                               │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│  4. Reproducibility                                          │
│     - Fixed random seeds                                     │
│     - Deterministic training                                 │
│     - Complete config versioning                             │
└──────────────────────────────────────────────────────────────┘
```

## Scalability Considerations

### Current Implementation
- Single GPU training
- Gradient accumulation for effective batch size
- Gradient checkpointing for memory efficiency

### Future Enhancements
```
┌────────────────────────────────────────────────────────────┐
│  Multi-GPU Training (Planned)                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │   GPU 0      │  │   GPU 1      │  │   GPU 2      │    │
│  │  (Replica)   │  │  (Replica)   │  │  (Replica)   │    │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘    │
│         └─────────────────┴─────────────────┘             │
│                    Gradient Sync                           │
└────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────┐
│  Distributed Training via DeepSpeed                        │
│  - ZeRO Stage 2/3 for memory optimization                  │
│  - Pipeline parallelism for large models                   │
│  - Tensor parallelism for attention layers                 │
└────────────────────────────────────────────────────────────┘
```

## Summary

The adapter training pipeline provides:

- **Modular Architecture**: Separate concerns (artifacts, verification, metrics)
- **Safety First**: Multiple layers of verification and validation
- **Production Ready**: Complete monitoring, logging, and error handling
- **Extensible**: Easy to add new metrics, adapters, or base models
- **Well Documented**: Comprehensive guides and inline documentation
- **Tested**: Unit tests for all utility functions

This architecture ensures reliable, reproducible training of QLoRA adapters while maintaining the integrity of base model weights.
