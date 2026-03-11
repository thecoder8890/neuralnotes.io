# Kaggle Model Workflow

This folder contains a Kaggle-oriented workflow for turning the current DocuGen AI codebase into a trainable code-generation dataset and LoRA fine-tuning pipeline.

The main application stays untouched. Everything for Kaggle lives here.

## What This Adds

- `export_training_data.py`
  - Uses the existing document processor and code generator to create JSONL training examples.
- `train_lora.py`
  - Fine-tunes a causal language model on Kaggle using QLoRA/LoRA.
- `inference.py`
  - Runs inference with the trained adapter or a merged model.
- `prompt_utils.py`
  - Shared prompt formatting utilities.
- `sources.example.json`
  - Example input format for documentation sources.
- `requirements.txt`
  - Kaggle-specific training dependencies.

## Recommended Kaggle Workflow

1. Upload this repository to Kaggle as a dataset or clone it into a notebook.
2. Enable internet if you want to fetch documentation URLs or push to Hugging Face.
3. Install Kaggle-specific dependencies:

```bash
pip install -r kaggle-model/requirements.txt
```

4. Export training data:

```bash
python kaggle-model/export_training_data.py \
  --sources-file kaggle-model/sources.example.json \
  --output /kaggle/working/docugen_training.jsonl
```

5. Train a LoRA adapter:

```bash
python kaggle-model/train_lora.py \
  --dataset-path /kaggle/working/docugen_training.jsonl \
  --model-name bigcode/starcoder2-3b \
  --output-dir /kaggle/working/docugen-kaggle-lora
```

6. Run inference:

```bash
python kaggle-model/inference.py \
  --base-model bigcode/starcoder2-3b \
  --adapter-path /kaggle/working/docugen-kaggle-lora \
  --technology react \
  --prompt "Build a React dashboard with auth and charts"
```

## Notes

- `export_training_data.py` will try the full document/code pipeline first and fall back to the simplified pipeline if the heavy dependencies are unavailable.
- For higher-quality training data, set `OPENAI_API_KEY` so the existing generator can create richer examples.
- Kaggle often works best with 3B to 7B models and QLoRA rather than full fine-tuning.
- If you only want a hosted demo, Hugging Face Spaces is a better deployment target. This folder is specifically for Kaggle training and experimentation.

## Input Source Format

The `sources.example.json` file uses this shape:

```json
[
  {
    "type": "url",
    "value": "https://react.dev/learn"
  },
  {
    "type": "file",
    "value": "path/to/local/documentation.md"
  }
]
```

`type` can be `url` or `file`.
