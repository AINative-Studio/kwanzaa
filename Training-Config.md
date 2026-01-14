### 1) Starter Hugging Face Training Config (Safe Defaults)

This is a **starter configuration** for **adapter-based fine-tuning (QLoRA by default)** that emphasizes:

* **Citation-following**
* **Refusal/uncertainty behavior**
* **Strict JSON output (“answer_json”)**
* **Budget safety** ($500–$5k) with small/medium base models

It’s written as a **repo-friendly spec** your team can implement with whatever runner you choose (HF AutoTrain, HF Trainer, TRL, custom scripts). No tool lock-in.

---

## A. Recommended Default Path (QLoRA)

**Why QLoRA:** cheapest + fastest path to get meaningful behavior changes without full GPU burn.

### Base Model (Default)

* **Preferred:** an **Allen Institute (AI2)** instruction model in the ~7B class (or nearest available that supports your license + usage needs)
* **Optional alternatives:** LLaMA-instruct, DeepSeek-instruct

> Put the chosen base model string in config as `base_model_id` so you can swap later.

---

## B. Training Objective

You are not training “culture.”
You are training **behavior and format compliance**:

1. Use retrieved context
2. Cite sources when required
3. Refuse when evidence is missing
4. Always output valid `answer_json`

---

## C. Dataset Assumptions

Dataset is in JSONL, one record per line.

Each record should provide messages in this shape:

* `messages[0]`: system
* `messages[1]`: user
* `messages[2]`: assistant (target)

You can embed retrieval snippets inside the user message like:

* `### Retrieved Context:` …chunks…
* `### Instruction:` …question…

This keeps training aligned to RAG behavior.

---

## D. Starter Config File (YAML)

Create: `configs/train.adapter.qlora.yaml`

```yaml
run:
  name: "kwanzaa-adapter-v0"
  output_dir: "outputs/kwanzaa-adapter-v0"
  seed: 42
  mixed_precision: "bf16"  # fallback to "fp16" if needed
  logging_steps: 10
  save_steps: 200
  eval_steps: 200
  save_total_limit: 3

model:
  base_model_id: "AI2/CHOSEN-INSTRUCT-MODEL"   # <-- swap AI2 / LLaMA / DeepSeek here
  trust_remote_code: true
  use_flash_attention: true   # only if supported in your environment

adapter:
  method: "qlora"             # qlora | lora
  r: 16
  alpha: 32
  dropout: 0.05
  target_modules:
    - "q_proj"
    - "k_proj"
    - "v_proj"
    - "o_proj"
    - "gate_proj"
    - "up_proj"
    - "down_proj"
  quantization:
    load_in_4bit: true
    bnb_4bit_compute_dtype: "bf16"
    bnb_4bit_use_double_quant: true
    bnb_4bit_quant_type: "nf4"

data:
  train_file: "data/training/kwanzaa_train.jsonl"
  eval_file: "data/training/kwanzaa_eval.jsonl"
  format: "chat_jsonl"        # internal label for your loader
  max_seq_length: 2048
  packing: true               # pack multiple short samples into sequences

training:
  epochs: 2
  learning_rate: 0.0002       # 2e-4 typical for QLoRA
  lr_scheduler: "cosine"
  warmup_ratio: 0.03
  weight_decay: 0.0
  per_device_train_batch_size: 1
  per_device_eval_batch_size: 1
  gradient_accumulation_steps: 16
  max_grad_norm: 1.0
  optim: "paged_adamw_8bit"
  gradient_checkpointing: true

evaluation:
  metrics:
    - "json_valid_rate"
    - "citation_coverage_rate"
    - "refusal_correctness_rate"
    - "retrieval_groundedness_rate"
  generation_defaults:
    temperature: 0.2
    top_p: 0.9
    max_new_tokens: 800

publishing:
  hf_repo: "ainative/kwanzaa-adapter-v0"
  include:
    - "adapter_config.json"
    - "adapter_model.safetensors"
    - "training_config.yaml"
    - "README.md"
  metadata:
    base_model_id: "AI2/CHOSEN-INSTRUCT-MODEL"
    dataset_version: "v0"
    task: "citation_grounded_chat"
```

---

## E. “Safe Default” Hyperparameter Rationale

* **max_seq_length: 2048** — enough room for citations + retrieval snippets without exploding cost
* **batch=1 + grad_accum=16** — stable on modest GPUs
* **epochs=2** — reduces overfitting and “format collapse”
* **lr=2e-4** — QLoRA standard; move down to 1e-4 if outputs get unstable

---

## F. Minimal Evaluation Set (Required)

Create: `data/training/kwanzaa_eval.jsonl` with **at least**:

* 10 citation-required Qs (educator/research)
* 10 “not in corpus” refusals
* 10 answer_json strict formatting tests
* 5 red-team prompts (stereotype / performative tone)

Your eval harness should compute:

* **JSON validity rate**
* **Citation coverage rate** (when required)
* **Refusal correctness** (when corpus lacks support)

---

## G. Definition of Done for “Training Config” (What your team must deliver)

* ✅ Config file checked in (`configs/train.adapter.qlora.yaml`)
* ✅ Base model is configurable via `base_model_id`
* ✅ Adapter settings defined + target_modules set
* ✅ Dataset paths defined
* ✅ Eval metrics listed
* ✅ Publishing block defined

---
