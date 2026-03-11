import argparse
import os
from pathlib import Path
from typing import List


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train a Kaggle-specific DocuGen LoRA adapter.")
    parser.add_argument("--dataset-path", type=Path, required=True, help="Path to exported JSONL data.")
    parser.add_argument("--model-name", type=str, default="bigcode/starcoder2-3b")
    parser.add_argument("--output-dir", type=Path, default=Path("/kaggle/working/docugen-kaggle-lora"))
    parser.add_argument("--max-seq-length", type=int, default=2048)
    parser.add_argument("--batch-size", type=int, default=1)
    parser.add_argument("--gradient-accumulation-steps", type=int, default=8)
    parser.add_argument("--num-train-epochs", type=int, default=1)
    parser.add_argument("--learning-rate", type=float, default=2e-4)
    parser.add_argument("--logging-steps", type=int, default=10)
    parser.add_argument("--save-steps", type=int, default=100)
    parser.add_argument("--validation-split", type=float, default=0.05)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--target-modules",
        type=str,
        default="auto",
        help="Comma-separated LoRA target modules or 'auto'.",
    )
    parser.add_argument("--push-to-hub", action="store_true")
    parser.add_argument("--hub-model-id", type=str, default="")
    parser.add_argument("--trust-remote-code", action="store_true")
    return parser.parse_args()


def infer_target_modules(model_name: str) -> List[str]:
    lowered = model_name.lower()
    if "starcoder" in lowered or "gpt" in lowered:
        return ["c_proj", "c_attn", "c_fc"]
    if "phi" in lowered:
        return ["q_proj", "k_proj", "v_proj", "dense", "fc1", "fc2"]
    return ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]


def main() -> None:
    args = parse_args()

    import torch
    from datasets import load_dataset
    from peft import LoraConfig, prepare_model_for_kbit_training
    from transformers import (
        AutoModelForCausalLM,
        AutoTokenizer,
        BitsAndBytesConfig,
        TrainingArguments,
        set_seed,
    )
    from trl import SFTTrainer

    set_seed(args.seed)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    dataset = load_dataset("json", data_files=str(args.dataset_path), split="train")
    eval_dataset = None
    if args.validation_split > 0 and len(dataset) > 10:
        split_dataset = dataset.train_test_split(test_size=args.validation_split, seed=args.seed)
        dataset = split_dataset["train"]
        eval_dataset = split_dataset["test"]

    tokenizer = AutoTokenizer.from_pretrained(
        args.model_name,
        trust_remote_code=args.trust_remote_code,
        use_fast=True,
    )
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    quantization_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_use_double_quant=True,
    )

    model = AutoModelForCausalLM.from_pretrained(
        args.model_name,
        trust_remote_code=args.trust_remote_code,
        device_map="auto",
        quantization_config=quantization_config,
    )
    model.config.use_cache = False
    model = prepare_model_for_kbit_training(model)

    target_modules = (
        infer_target_modules(args.model_name)
        if args.target_modules == "auto"
        else [item.strip() for item in args.target_modules.split(",") if item.strip()]
    )

    peft_config = LoraConfig(
        r=16,
        lora_alpha=32,
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=target_modules,
    )

    use_bf16 = torch.cuda.is_available() and torch.cuda.is_bf16_supported()

    training_args = TrainingArguments(
        output_dir=str(args.output_dir),
        per_device_train_batch_size=args.batch_size,
        gradient_accumulation_steps=args.gradient_accumulation_steps,
        learning_rate=args.learning_rate,
        logging_steps=args.logging_steps,
        num_train_epochs=args.num_train_epochs,
        save_steps=args.save_steps,
        save_total_limit=2,
        fp16=not use_bf16,
        bf16=use_bf16,
        gradient_checkpointing=True,
        optim="paged_adamw_8bit",
        lr_scheduler_type="cosine",
        warmup_ratio=0.03,
        report_to="none",
        evaluation_strategy="steps" if eval_dataset is not None else "no",
        eval_steps=args.save_steps if eval_dataset is not None else None,
        seed=args.seed,
    )

    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=dataset,
        eval_dataset=eval_dataset,
        dataset_text_field="text",
        peft_config=peft_config,
        max_seq_length=args.max_seq_length,
        packing=False,
        args=training_args,
    )

    trainer.train()
    trainer.model.save_pretrained(args.output_dir)
    tokenizer.save_pretrained(args.output_dir)

    if args.push_to_hub and args.hub_model_id:
        trainer.model.push_to_hub(args.hub_model_id)
        tokenizer.push_to_hub(args.hub_model_id)

    print(f"Saved adapter to {args.output_dir}")


if __name__ == "__main__":
    os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
    main()
