import argparse
from pathlib import Path

from prompt_utils import build_inference_prompt


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run inference with the Kaggle DocuGen adapter.")
    parser.add_argument("--base-model", type=str, required=True)
    parser.add_argument(
        "--adapter-path",
        type=Path,
        default=None,
        help="Optional LoRA adapter path. Omit this when using a merged model.",
    )
    parser.add_argument("--model-path", type=Path, default=None, help="Optional merged model directory.")
    parser.add_argument("--technology", type=str, default="react")
    parser.add_argument("--prompt", type=str, required=True)
    parser.add_argument("--context", type=str, default="")
    parser.add_argument("--context-file", type=Path, default=None)
    parser.add_argument("--max-new-tokens", type=int, default=768)
    parser.add_argument("--temperature", type=float, default=0.2)
    parser.add_argument("--top-p", type=float, default=0.95)
    parser.add_argument("--trust-remote-code", action="store_true")
    return parser.parse_args()


def load_context(args: argparse.Namespace) -> str:
    if args.context_file:
        return args.context_file.read_text(encoding="utf-8")
    return args.context


def main() -> None:
    args = parse_args()

    import torch
    from peft import PeftModel
    from transformers import AutoModelForCausalLM, AutoTokenizer

    model_source = str(args.model_path) if args.model_path else args.base_model
    tokenizer = AutoTokenizer.from_pretrained(
        model_source,
        trust_remote_code=args.trust_remote_code,
        use_fast=True,
    )
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        model_source if args.model_path else args.base_model,
        trust_remote_code=args.trust_remote_code,
        device_map="auto",
        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
    )

    if args.adapter_path:
        model = PeftModel.from_pretrained(model, str(args.adapter_path))

    prompt = build_inference_prompt(
        technology=args.technology,
        prompt=args.prompt,
        context=load_context(args),
    )
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    generated = model.generate(
        **inputs,
        max_new_tokens=args.max_new_tokens,
        temperature=args.temperature,
        top_p=args.top_p,
        do_sample=True,
        pad_token_id=tokenizer.eos_token_id,
    )
    output = tokenizer.decode(generated[0], skip_special_tokens=False)
    print(output)


if __name__ == "__main__":
    main()
