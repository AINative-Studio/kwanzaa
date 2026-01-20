---
library_name: peft
license: llama3.2
base_model: meta-llama/Llama-3.2-1B-Instruct
tags:
- base_model:adapter:meta-llama/Llama-3.2-1B-Instruct
- lora
- transformers
pipeline_tag: text-generation
model-index:
- name: kwanzaa-adapter-v1
  results: []
---

<!-- This model card has been generated automatically according to the information the Trainer had access to. You
should probably proofread and complete it, then remove this comment. -->

# kwanzaa-adapter-v1

This model is a fine-tuned version of [meta-llama/Llama-3.2-1B-Instruct](https://huggingface.co/meta-llama/Llama-3.2-1B-Instruct) on an unknown dataset.

## Model description

More information needed

## Intended uses & limitations

More information needed

## Training and evaluation data

More information needed

## Training procedure

### Training hyperparameters

The following hyperparameters were used during training:
- learning_rate: 0.0002
- train_batch_size: 2
- eval_batch_size: 2
- seed: 42
- gradient_accumulation_steps: 4
- total_train_batch_size: 8
- optimizer: Use paged_adamw_8bit with betas=(0.9,0.999) and epsilon=1e-08 and optimizer_args=No additional optimizer arguments
- lr_scheduler_type: cosine
- lr_scheduler_warmup_steps: 10
- num_epochs: 3

### Training results



### Framework versions

- PEFT 0.18.1
- Transformers 5.0.0.dev0
- Pytorch 2.9.0+cu126
- Datasets 4.3.0
- Tokenizers 0.22.1