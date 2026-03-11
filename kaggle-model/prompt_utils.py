import json
from datetime import datetime
from typing import Any, Dict, Iterable, List


SYSTEM_PROMPT = (
    "You are DocuGen AI running in Kaggle fine-tuning mode. "
    "Generate a complete software project as structured JSON with files, "
    "directory structure, and setup instructions."
)


def compact_context(chunks: Iterable[str], limit: int = 5) -> str:
    selected_chunks = [chunk.strip() for chunk in chunks if chunk and chunk.strip()]
    return "\n\n".join(selected_chunks[:limit])


def build_generation_output(result: Any) -> Dict[str, Any]:
    return {
        "files": [
            {
                "name": file_item.name,
                "content": file_item.content,
                "type": file_item.type,
            }
            for file_item in result.files
        ],
        "structure": result.structure,
        "instructions": result.instructions,
    }


def build_training_text(
    technology: str,
    prompt: str,
    context: str,
    output_payload: Dict[str, Any],
) -> str:
    output_json = json.dumps(output_payload, ensure_ascii=False, indent=2)
    return (
        "<|system|>\n"
        f"{SYSTEM_PROMPT}\n"
        "<|technology|>\n"
        f"{technology}\n"
        "<|context|>\n"
        f"{context}\n"
        "<|user|>\n"
        f"{prompt}\n"
        "<|assistant|>\n"
        f"{output_json}"
    )


def build_training_record(
    source: Dict[str, Any],
    technology: str,
    prompt: str,
    context_chunks: List[str],
    result: Any,
) -> Dict[str, Any]:
    context = compact_context(context_chunks)
    output_payload = build_generation_output(result)
    return {
        "input": {
            "system": SYSTEM_PROMPT,
            "technology": technology,
            "context": context,
            "prompt": prompt,
        },
        "output": output_payload,
        "metadata": {
            "source_type": source["type"],
            "source_value": source["value"],
            "generated_at": datetime.utcnow().isoformat(),
        },
        "text": build_training_text(
            technology=technology,
            prompt=prompt,
            context=context,
            output_payload=output_payload,
        ),
    }


def build_inference_prompt(technology: str, prompt: str, context: str) -> str:
    return (
        "<|system|>\n"
        f"{SYSTEM_PROMPT}\n"
        "<|technology|>\n"
        f"{technology}\n"
        "<|context|>\n"
        f"{context}\n"
        "<|user|>\n"
        f"{prompt}\n"
        "<|assistant|>\n"
    )
