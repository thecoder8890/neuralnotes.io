# Creating a Hugging Face Model with neuralnotes.io

This document provides a step-by-step plan for creating, training, validating, and publishing a Hugging Face model that leverages the DocuGen AI codebase from this repository.

---

## Table of Contents

1. [Objective](#objective)
2. [Repository Assessment](#1-repository-assessment)
3. [Model Type and Scope](#2-model-type-and-scope)
4. [Data Preparation](#3-data-preparation)
5. [Code Integration](#4-code-integration)
6. [Training Pipeline](#5-training-pipeline)
7. [Testing and Validation](#6-testing-and-validation)
8. [Exporting and Saving the Model](#7-exporting-and-saving-the-model)
9. [Publishing to Hugging Face Hub](#8-publishing-to-hugging-face-hub)

---

## Objective

Build a Hugging Face-compatible model that replicates and enhances DocuGen AI's core capability: generating complete, runnable project scaffolds from documentation context and natural language prompts. The model will be fine-tuned to accept a documentation chunk and a user prompt, then output structured code files, project layouts, and setup instructions.

---

## 1. Repository Assessment

### Current Architecture

DocuGen AI uses a **RAG (Retrieval-Augmented Generation)** pipeline:

```
Documentation (URL/file)
   → Text Extraction (BeautifulSoup, PyPDF2, Markdown)
   → Chunking (LangChain RecursiveCharacterTextSplitter, chunk_size=1000, overlap=200)
   → Embedding (OpenAI Embeddings)
   → Vector Storage (ChromaDB)
   → Retrieval (top-k semantic search)
   → Code Generation (OpenAI GPT-4/3.5-turbo)
   → Structured Output (JSON → files, structure, instructions)
```

### Key Components to Leverage

| Component | File | Purpose |
|-----------|------|---------|
| Document Processor | `backend/core/document_processor.py` | Text extraction, chunking, embedding, vector storage |
| Code Generator | `backend/core/code_generator.py` | Prompt construction, OpenAI API calls, output parsing |
| Data Schemas | `backend/models/schemas.py` | Pydantic models defining input/output formats |
| API Layer | `main.py` | FastAPI endpoints tying the pipeline together |

### Supported Technologies

The existing generator supports: **Spring Boot**, **Django**, **React**, **Express.js**, **Flask**, and **Next.js**.

---

## 2. Model Type and Scope

### Use Case

**Conditional Code Generation** — given documentation context and a natural language instruction, the model generates a structured project (multiple files with content, directory layout, and setup instructions).

### Model Architecture

Fine-tune a **causal language model** (e.g., `codellama/CodeLlama-7b-hf`, `bigcode/starcoder2-3b`, or `Salesforce/codegen2-1B`) using supervised fine-tuning (SFT) on prompt → code completion pairs extracted from DocuGen AI's generation pipeline.

### Input/Output Format

**Input** (prompt to the model):
```
<|system|>You are a project scaffolding assistant. Generate a complete project structure as JSON.
Technology: {technology}
<|context|>{documentation_chunks}
<|user|>{natural_language_prompt}
<|assistant|>
```

**Output** (model completion):
```json
{
  "files": [
    {"name": "src/App.tsx", "content": "...", "type": "text"},
    {"name": "package.json", "content": "...", "type": "text"}
  ],
  "structure": {"src": {"App.tsx": null}, "package.json": null},
  "instructions": "Run npm install && npm start"
}
```

### Tokenizer

Use the base model's tokenizer (e.g., CodeLlama's `LlamaTokenizer`). Add special tokens:
- `<|system|>`, `<|context|>`, `<|user|>`, `<|assistant|>` — to delineate prompt sections
- `<|file_start|>`, `<|file_end|>` — optional, for multi-file output boundaries

---

## 3. Data Preparation

### 3.1 Collect Training Data

Generate training examples by running the existing pipeline against diverse documentation sources.

**Data collection script** — `scripts/collect_training_data.py`:

```python
"""
Collect training data by running DocuGen AI against various documentation
sources and capturing the input-output pairs for fine-tuning.
"""

import asyncio
import json
import os
import sys
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.core.document_processor import DocumentProcessor
from backend.core.code_generator import CodeGenerator
from backend.models.schemas import Technology

# Documentation sources to process
DOC_SOURCES = [
    "https://docs.spring.io/spring-boot/docs/current/reference/html/",
    "https://react.dev/learn",
    "https://docs.djangoproject.com/en/5.0/intro/tutorial01/",
    "https://flask.palletsprojects.com/en/3.0.x/quickstart/",
    "https://expressjs.com/en/starter/hello-world.html",
    "https://nextjs.org/docs/getting-started",
]

# Example prompts per technology
PROMPTS = {
    Technology.SPRING_BOOT: [
        "Create a REST API with CRUD operations for a user management system",
        "Build a Spring Boot app with JWT authentication",
        "Create a microservice with health checks and metrics",
    ],
    Technology.REACT: [
        "Build a todo list app with state management",
        "Create a dashboard with charts and data tables",
        "Build a form with validation and file upload",
    ],
    Technology.DJANGO: [
        "Create a blog application with user authentication",
        "Build a REST API with Django REST Framework",
        "Create an e-commerce product catalog",
    ],
    Technology.FLASK: [
        "Build a REST API with SQLAlchemy ORM",
        "Create a file upload service with validation",
        "Build a URL shortener service",
    ],
    Technology.EXPRESS: [
        "Create a REST API with MongoDB integration",
        "Build a real-time chat server with WebSockets",
        "Create an authentication service with JWT",
    ],
    Technology.NEXTJS: [
        "Build a blog with server-side rendering",
        "Create a full-stack app with API routes",
        "Build a dashboard with dynamic routing",
    ],
}


async def collect_data(output_dir: str = "data/training"):
    os.makedirs(output_dir, exist_ok=True)

    processor = DocumentProcessor()
    generator = CodeGenerator()

    training_examples = []

    for url in DOC_SOURCES:
        try:
            doc_id = await processor.process_url(url)
            print(f"Processed: {url} -> {doc_id}")

            for tech, prompts in PROMPTS.items():
                for prompt in prompts:
                    # Query relevant docs
                    relevant_chunks = await processor.query_documents(
                        doc_id, prompt, n_results=5
                    )
                    context = "\n\n".join(relevant_chunks[:5])

                    # Generate project
                    result = await generator.generate_project(
                        doc_id=doc_id, prompt=prompt, technology=tech
                    )

                    # Create training example
                    example = {
                        "input": {
                            "system": (
                                "You are a project scaffolding assistant. "
                                "Generate a complete project structure as JSON."
                            ),
                            "technology": tech.value,
                            "context": context,
                            "prompt": prompt,
                        },
                        "output": {
                            "files": [
                                {"name": f.name, "content": f.content, "type": f.type}
                                for f in result.files
                            ],
                            "structure": result.structure,
                            "instructions": result.instructions,
                        },
                        "metadata": {
                            "doc_url": url,
                            "doc_id": doc_id,
                            "timestamp": datetime.now().isoformat(),
                        },
                    }
                    training_examples.append(example)
                    print(f"  Collected: {tech.value} - {prompt[:50]}...")

        except Exception as e:
            print(f"Error processing {url}: {e}")
            continue

    # Save training data
    output_file = os.path.join(output_dir, "training_data.jsonl")
    with open(output_file, "w") as f:
        for example in training_examples:
            f.write(json.dumps(example) + "\n")

    print(f"\nCollected {len(training_examples)} training examples -> {output_file}")
    return training_examples


if __name__ == "__main__":
    asyncio.run(collect_data())
```

### 3.2 Preprocess Data

Transform collected examples into the tokenized format required for fine-tuning.

**Preprocessing script** — `scripts/preprocess_data.py`:

```python
"""
Preprocess collected training data into tokenized format for fine-tuning.
"""

import json
import os
from datasets import Dataset
from transformers import AutoTokenizer

BASE_MODEL = "bigcode/starcoder2-3b"  # Or your chosen base model
MAX_SEQ_LENGTH = 4096

SPECIAL_TOKENS = {
    "additional_special_tokens": [
        "<|system|>",
        "<|context|>",
        "<|user|>",
        "<|assistant|>",
    ]
}


def format_example(example: dict) -> str:
    """Convert a training example to the prompt format."""
    inp = example["input"]
    out = example["output"]

    prompt = (
        f"<|system|>{inp['system']}\nTechnology: {inp['technology']}\n"
        f"<|context|>{inp['context'][:2000]}\n"
        f"<|user|>{inp['prompt']}\n"
        f"<|assistant|>{json.dumps(out, indent=2)}"
    )
    return prompt


def preprocess(
    input_file: str = "data/training/training_data.jsonl",
    output_dir: str = "data/processed",
):
    os.makedirs(output_dir, exist_ok=True)

    # Load tokenizer and add special tokens
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
    tokenizer.add_special_tokens(SPECIAL_TOKENS)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    # Load and format examples
    formatted_texts = []
    with open(input_file, "r") as f:
        for line in f:
            example = json.loads(line.strip())
            formatted_texts.append(format_example(example))

    # Create dataset
    dataset = Dataset.from_dict({"text": formatted_texts})

    # Tokenize
    def tokenize_fn(examples):
        return tokenizer(
            examples["text"],
            truncation=True,
            max_length=MAX_SEQ_LENGTH,
            padding="max_length",
        )

    tokenized_dataset = dataset.map(tokenize_fn, batched=True, remove_columns=["text"])

    # Split into train/validation
    split = tokenized_dataset.train_test_split(test_size=0.1, seed=42)

    # Save
    split["train"].save_to_disk(os.path.join(output_dir, "train"))
    split["test"].save_to_disk(os.path.join(output_dir, "validation"))
    tokenizer.save_pretrained(os.path.join(output_dir, "tokenizer"))

    print(f"Train examples: {len(split['train'])}")
    print(f"Validation examples: {len(split['test'])}")
    print(f"Saved to: {output_dir}")


if __name__ == "__main__":
    preprocess()
```

### 3.3 Recommended Dataset Size

| Quality Level | Examples | Estimated Collection Time |
|--------------|----------|--------------------------|
| Minimum viable | 100–500 | 2–4 hours |
| Good quality | 1,000–5,000 | 1–2 days |
| Production grade | 10,000+ | 1–2 weeks |

---

## 4. Code Integration

### 4.1 Install Dependencies

```bash
pip install transformers datasets accelerate peft bitsandbytes trl huggingface_hub
```

### 4.2 Model Wrapper

Create a Hugging Face-compatible model class that wraps the generation logic — `scripts/model_wrapper.py`:

```python
"""
Hugging Face-compatible model wrapper for DocuGen AI code generation.
"""

import json
from typing import Optional
from transformers import AutoModelForCausalLM, AutoTokenizer


class DocuGenModel:
    """Wrapper for using the fine-tuned model for code generation."""

    def __init__(self, model_name_or_path: str):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name_or_path)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name_or_path,
            device_map="auto",
            torch_dtype="auto",
        )

    def generate_project(
        self,
        prompt: str,
        technology: str,
        context: str = "",
        max_new_tokens: int = 4096,
        temperature: float = 0.2,
        top_p: float = 0.95,
    ) -> dict:
        """Generate a project structure from a prompt."""
        input_text = (
            "<|system|>You are a project scaffolding assistant. "
            "Generate a complete project structure as JSON.\n"
            f"Technology: {technology}\n"
            f"<|context|>{context[:2000]}\n"
            f"<|user|>{prompt}\n"
            "<|assistant|>"
        )

        inputs = self.tokenizer(input_text, return_tensors="pt").to(self.model.device)

        outputs = self.model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            top_p=top_p,
            do_sample=True,
            pad_token_id=self.tokenizer.eos_token_id,
        )

        generated_text = self.tokenizer.decode(
            outputs[0][inputs["input_ids"].shape[1]:],
            skip_special_tokens=False,
        )

        # Parse the JSON output
        try:
            # Find the JSON block in the output
            json_start = generated_text.find("{")
            json_end = generated_text.rfind("}") + 1
            if json_start != -1 and json_end > json_start:
                return json.loads(generated_text[json_start:json_end])
        except json.JSONDecodeError:
            pass

        return {"raw_output": generated_text}
```

### 4.3 Integrate with Existing Backend

Replace the OpenAI API call in `backend/core/code_generator.py` with the Hugging Face model:

```python
# In code_generator.py, add an alternative initialization path:

from scripts.model_wrapper import DocuGenModel

class CodeGenerator:
    def __init__(self):
        self.document_processor = DocumentProcessor()
        self.hf_model = None
        self.openai_client = None
        self.generated_projects = {}
        self._initialize_model()

    def _initialize_model(self):
        """Initialize the model — prefer local HF model, fall back to OpenAI."""
        hf_model_path = os.getenv("HF_MODEL_PATH")
        if hf_model_path and os.path.exists(hf_model_path):
            self.hf_model = DocuGenModel(hf_model_path)
        else:
            self._initialize_openai()
```

---

## 5. Training Pipeline

### 5.1 Training Script

**Fine-tuning script using QLoRA** — `scripts/train_model.py`:

```python
"""
Fine-tune a code generation model using QLoRA for DocuGen AI.
"""

import os
import torch
from datasets import load_from_disk
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    BitsAndBytesConfig,
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from trl import SFTTrainer

# ── Configuration ──────────────────────────────────────────────────────

BASE_MODEL = "bigcode/starcoder2-3b"
OUTPUT_DIR = "models/docugen-codegen"
DATA_DIR = "data/processed"
MAX_SEQ_LENGTH = 4096

# QLoRA configuration
QLORA_CONFIG = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16,
    bnb_4bit_use_double_quant=True,
)

LORA_CONFIG = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM",
)

TRAINING_ARGS = TrainingArguments(
    output_dir=OUTPUT_DIR,
    num_train_epochs=3,
    per_device_train_batch_size=2,
    per_device_eval_batch_size=2,
    gradient_accumulation_steps=4,
    learning_rate=2e-4,
    weight_decay=0.01,
    warmup_ratio=0.03,
    lr_scheduler_type="cosine",
    logging_steps=10,
    eval_strategy="steps",
    eval_steps=100,
    save_strategy="steps",
    save_steps=100,
    save_total_limit=3,
    fp16=True,
    report_to="none",
    gradient_checkpointing=True,
    optim="paged_adamw_8bit",
)


def train():
    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(
        os.path.join(DATA_DIR, "tokenizer")
    )

    # Load model with QLoRA
    model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL,
        quantization_config=QLORA_CONFIG,
        device_map="auto",
    )
    model.resize_token_embeddings(len(tokenizer))
    model = prepare_model_for_kbit_training(model)
    model = get_peft_model(model, LORA_CONFIG)

    model.print_trainable_parameters()

    # Load datasets
    train_dataset = load_from_disk(os.path.join(DATA_DIR, "train"))
    eval_dataset = load_from_disk(os.path.join(DATA_DIR, "validation"))

    # Initialize trainer
    trainer = SFTTrainer(
        model=model,
        args=TRAINING_ARGS,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        processing_class=tokenizer,
        max_seq_length=MAX_SEQ_LENGTH,
    )

    # Train
    print("Starting training...")
    trainer.train()

    # Save final model
    trainer.save_model(os.path.join(OUTPUT_DIR, "final"))
    tokenizer.save_pretrained(os.path.join(OUTPUT_DIR, "final"))
    print(f"Model saved to {OUTPUT_DIR}/final")


if __name__ == "__main__":
    train()
```

### 5.2 Hyperparameter Reference

| Parameter | Value | Notes |
|-----------|-------|-------|
| Base model | `bigcode/starcoder2-3b` | Good balance of size and performance for code |
| LoRA rank (r) | 16 | Higher = more capacity, more VRAM |
| LoRA alpha | 32 | Typically 2× rank |
| Learning rate | 2e-4 | Standard for QLoRA fine-tuning |
| Batch size | 2 (× 4 grad accum = effective 8) | Adjust based on GPU memory |
| Epochs | 3 | Monitor eval loss for early stopping |
| Max sequence length | 4096 | Covers most project generation outputs |
| Quantization | 4-bit NF4 (QLoRA) | Reduces VRAM to ~8 GB for a 3B model |

### 5.3 Hardware Requirements

| Setup | GPU VRAM | Training Time (1K examples) |
|-------|----------|----------------------------|
| Single GPU (QLoRA) | 8–16 GB | 2–4 hours |
| Single GPU (full fine-tune) | 24–48 GB | 4–8 hours |
| Multi-GPU (2× A100) | 80 GB each | 1–2 hours |
| Google Colab (T4, free) | 16 GB | 4–6 hours (QLoRA only) |

### 5.4 Launch Training

```bash
# Collect training data (requires OpenAI API key in .env)
python scripts/collect_training_data.py

# Preprocess data
python scripts/preprocess_data.py

# Train the model
python scripts/train_model.py
```

---

## 6. Testing and Validation

### 6.1 Evaluation Metrics

```python
"""
Evaluate the fine-tuned model on held-out validation data.
"""

import json
from typing import List
from rouge_score import rouge_scorer
from codebleu import calc_codebleu


def evaluate_generation(predictions: List[str], references: List[str]) -> dict:
    """Compute evaluation metrics for generated code."""
    # ROUGE scores for textual similarity
    scorer = rouge_scorer.RougeScorer(
        ["rouge1", "rouge2", "rougeL"], use_stemmer=True
    )
    rouge_scores = {"rouge1": [], "rouge2": [], "rougeL": []}
    for pred, ref in zip(predictions, references):
        scores = scorer.score(ref, pred)
        for key in rouge_scores:
            rouge_scores[key].append(scores[key].fmeasure)

    # CodeBLEU for code-specific evaluation
    codebleu_scores = calc_codebleu(
        references=[[r] for r in references],
        predictions=predictions,
        lang="python",
    )

    # Structural validation — check if output is valid JSON
    valid_json_count = 0
    valid_structure_count = 0
    for pred in predictions:
        try:
            parsed = json.loads(pred)
            valid_json_count += 1
            if "files" in parsed and "structure" in parsed:
                valid_structure_count += 1
        except json.JSONDecodeError:
            pass

    return {
        "rouge1": sum(rouge_scores["rouge1"]) / len(rouge_scores["rouge1"]),
        "rouge2": sum(rouge_scores["rouge2"]) / len(rouge_scores["rouge2"]),
        "rougeL": sum(rouge_scores["rougeL"]) / len(rouge_scores["rougeL"]),
        "codebleu": codebleu_scores["codebleu"],
        "valid_json_rate": valid_json_count / len(predictions),
        "valid_structure_rate": valid_structure_count / len(predictions),
    }
```

### 6.2 Run Validation

```bash
# Install evaluation dependencies
pip install rouge-score codebleu

# Run evaluation script
python scripts/evaluate_model.py \
    --model_path models/docugen-codegen/final \
    --test_data data/processed/validation
```

### 6.3 Quality Checklist

- [ ] **Valid JSON rate ≥ 95%** — Model outputs parseable JSON
- [ ] **Valid structure rate ≥ 90%** — Output contains `files`, `structure`, and `instructions` keys
- [ ] **ROUGE-L ≥ 0.3** — Reasonable textual overlap with reference outputs
- [ ] **CodeBLEU ≥ 0.2** — Code quality is acceptable
- [ ] **Manual review** — Spot-check 20+ generated projects across all 6 supported technologies
- [ ] **End-to-end test** — Integrate model into backend and verify API responses

---

## 7. Exporting and Saving the Model

### 7.1 Merge LoRA Weights and Export

```python
"""
Merge LoRA adapter weights into the base model and export for distribution.
"""

from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

BASE_MODEL = "bigcode/starcoder2-3b"
ADAPTER_PATH = "models/docugen-codegen/final"
MERGED_OUTPUT = "models/docugen-codegen-merged"


def merge_and_export():
    print("Loading base model...")
    base_model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL,
        torch_dtype="auto",
        device_map="auto",
    )

    print("Loading LoRA adapter...")
    model = PeftModel.from_pretrained(base_model, ADAPTER_PATH)

    print("Merging weights...")
    merged_model = model.merge_and_unload()

    print(f"Saving merged model to {MERGED_OUTPUT}...")
    merged_model.save_pretrained(MERGED_OUTPUT)

    tokenizer = AutoTokenizer.from_pretrained(ADAPTER_PATH)
    tokenizer.save_pretrained(MERGED_OUTPUT)

    print("Export complete.")


if __name__ == "__main__":
    merge_and_export()
```

### 7.2 Verify the Exported Model

```bash
python -c "
from transformers import AutoModelForCausalLM, AutoTokenizer
model = AutoModelForCausalLM.from_pretrained('models/docugen-codegen-merged')
tokenizer = AutoTokenizer.from_pretrained('models/docugen-codegen-merged')
print(f'Model parameters: {model.num_parameters():,}')
print(f'Vocabulary size: {len(tokenizer)}')
print('Export verified successfully.')
"
```

### 7.3 Model Card

Create a `README.md` inside the model directory (`models/docugen-codegen-merged/README.md`):

```markdown
---
license: apache-2.0
language:
  - en
tags:
  - code-generation
  - project-scaffolding
  - docugen
datasets:
  - custom
pipeline_tag: text-generation
library_name: transformers
---

# DocuGen CodeGen

A fine-tuned code generation model for documentation-aware project scaffolding.

## Model Description

This model generates complete project structures (files, directory layouts,
and setup instructions) given documentation context and a natural language
prompt. It was fine-tuned from `bigcode/starcoder2-3b` on project generation
data produced by the DocuGen AI pipeline.

## Supported Technologies

- Spring Boot (Java/Maven)
- React (TypeScript)
- Django (Python)
- Flask (Python)
- Express.js (Node.js)
- Next.js (React SSR)

## Usage

```python
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained("your-username/docugen-codegen")
tokenizer = AutoTokenizer.from_pretrained("your-username/docugen-codegen")

prompt = (
    "<|system|>You are a project scaffolding assistant. "
    "Generate a complete project structure as JSON.\n"
    "Technology: react\n"
    "<|context|>React documentation about components and hooks...\n"
    "<|user|>Create a todo list app with state management\n"
    "<|assistant|>"
)

inputs = tokenizer(prompt, return_tensors="pt")
outputs = model.generate(**inputs, max_new_tokens=4096, temperature=0.2)
print(tokenizer.decode(outputs[0], skip_special_tokens=False))
```

## Training Details

- **Base model**: bigcode/starcoder2-3b
- **Method**: QLoRA (4-bit quantization with LoRA adapters)
- **LoRA rank**: 16, alpha: 32
- **Training data**: Project scaffolding examples from DocuGen AI
- **Epochs**: 3
- **Sequence length**: 4096

## Limitations

- Output must be validated as JSON before use
- Large or complex project structures may be truncated at the sequence limit
- Quality depends on the relevance of the documentation context provided
```

---

## 8. Publishing to Hugging Face Hub

### 8.1 Authenticate

```bash
# Install the Hugging Face CLI
pip install huggingface_hub

# Log in (creates ~/.huggingface/token)
huggingface-cli login
```

### 8.2 Push to Hub

```python
"""
Upload the merged model to Hugging Face Hub.
"""

from huggingface_hub import HfApi

MODEL_DIR = "models/docugen-codegen-merged"
REPO_ID = "your-username/docugen-codegen"  # Change to your Hub username

api = HfApi()

# Create the repository on Hub (if it doesn't exist)
api.create_repo(repo_id=REPO_ID, repo_type="model", exist_ok=True)

# Upload the model directory
api.upload_folder(
    folder_path=MODEL_DIR,
    repo_id=REPO_ID,
    repo_type="model",
    commit_message="Upload DocuGen CodeGen model",
)

print(f"Model published to: https://huggingface.co/{REPO_ID}")
```

Or use the CLI:

```bash
huggingface-cli upload your-username/docugen-codegen models/docugen-codegen-merged .
```

### 8.3 Verify on Hub

```bash
# Test loading from Hub
python -c "
from transformers import pipeline
pipe = pipeline('text-generation', model='your-username/docugen-codegen')
result = pipe('<|system|>Generate a project.\n<|user|>Hello world app\n<|assistant|>', max_new_tokens=512)
print(result[0]['generated_text'])
"
```

---

## Summary

| Step | Action | Command / Script |
|------|--------|-----------------|
| 1 | Collect training data | `python scripts/collect_training_data.py` |
| 2 | Preprocess and tokenize | `python scripts/preprocess_data.py` |
| 3 | Fine-tune with QLoRA | `python scripts/train_model.py` |
| 4 | Evaluate model quality | `python scripts/evaluate_model.py` |
| 5 | Merge LoRA and export | `python scripts/merge_and_export.py` |
| 6 | Publish to Hugging Face | `huggingface-cli upload your-username/docugen-codegen ...` |

This plan provides a complete, end-to-end workflow for creating a Hugging Face model that captures DocuGen AI's code generation capabilities in a portable, shareable format.
