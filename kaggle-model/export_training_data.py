import argparse
import asyncio
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.models.schemas import Technology
from prompt_utils import build_training_record


DEFAULT_DOC_SOURCES = [
    {"type": "url", "value": "https://react.dev/learn"},
    {"type": "url", "value": "https://flask.palletsprojects.com/en/stable/"},
    {"type": "url", "value": "https://docs.spring.io/spring-boot/reference/"},
]

DEFAULT_PROMPTS = {
    Technology.SPRING_BOOT: [
        "Create a Spring Boot REST API with PostgreSQL, validation, and a layered architecture.",
        "Build a Spring Boot service with JPA repositories and basic CRUD endpoints.",
    ],
    Technology.REACT: [
        "Create a React dashboard with authentication, navigation, and chart placeholders.",
        "Build a React TypeScript app with forms, tables, and API service scaffolding.",
    ],
    Technology.DJANGO: [
        "Create a Django app with models, admin, and CRUD views for a blog.",
        "Build a Django REST backend with authentication and modular apps.",
    ],
    Technology.FLASK: [
        "Create a Flask REST API with SQLAlchemy, JWT authentication, and CRUD resources.",
        "Build a Flask service with environment config and modular blueprints.",
    ],
    Technology.EXPRESS: [
        "Create an Express API with JWT authentication, routing, and MongoDB integration.",
        "Build an Express.js backend with middleware, validation, and REST endpoints.",
    ],
    Technology.NEXTJS: [
        "Create a Next.js app with API routes, dashboard pages, and reusable components.",
        "Build a Next.js project with dynamic routing and server-side rendering.",
    ],
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export DocuGen training data for Kaggle fine-tuning.")
    parser.add_argument(
        "--sources-file",
        type=Path,
        default=None,
        help="Optional JSON file with a list of source objects: {type, value}.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("kaggle-model/output/training_data.jsonl"),
        help="Output JSONL path.",
    )
    parser.add_argument(
        "--max-prompts-per-tech",
        type=int,
        default=2,
        help="Maximum prompts to use per technology.",
    )
    parser.add_argument(
        "--n-results",
        type=int,
        default=5,
        help="Number of documentation chunks to retrieve per prompt.",
    )
    return parser.parse_args()


def load_sources(source_file: Optional[Path]) -> List[Dict[str, str]]:
    if not source_file:
        return DEFAULT_DOC_SOURCES

    payload = json.loads(source_file.read_text())
    if not isinstance(payload, list):
        raise ValueError("sources-file must contain a JSON list")

    normalized_sources = []
    for item in payload:
        if isinstance(item, str):
            normalized_sources.append({"type": "url", "value": item})
        elif isinstance(item, dict) and item.get("type") and item.get("value"):
            normalized_sources.append({"type": item["type"], "value": item["value"]})
        else:
            raise ValueError(f"Unsupported source entry: {item!r}")
    return normalized_sources


def load_pipeline() -> Tuple[Any, Any, str]:
    try:
        from backend.core.document_processor import DocumentProcessor
        from backend.core.code_generator import CodeGenerator

        return DocumentProcessor, CodeGenerator, "full"
    except Exception:
        from backend.core.document_processor_simple import DocumentProcessor
        from backend.core.code_generator_simple import CodeGenerator

        return DocumentProcessor, CodeGenerator, "simplified"


async def process_source(processor: Any, source: Dict[str, str]) -> str:
    if source["type"] == "url":
        return await processor.process_url(source["value"])

    if source["type"] == "file":
        file_path = Path(source["value"])
        content = file_path.read_bytes()
        return await processor.process_file(content, file_path.name)

    raise ValueError(f"Unsupported source type: {source['type']}")


async def collect_examples(args: argparse.Namespace) -> List[Dict[str, Any]]:
    document_processor_cls, code_generator_cls, mode = load_pipeline()
    processor = document_processor_cls()
    generator = code_generator_cls()
    sources = load_sources(args.sources_file)
    training_examples: List[Dict[str, Any]] = []

    print(f"Using pipeline mode: {mode}")

    for source in sources:
        try:
            doc_id = await process_source(processor, source)
            print(f"Processed source {source['value']} -> {doc_id}")
        except Exception as exc:
            print(f"Skipping source {source['value']}: {exc}")
            continue

        for technology, prompts in DEFAULT_PROMPTS.items():
            for prompt in prompts[: args.max_prompts_per_tech]:
                try:
                    context_chunks = await processor.query_documents(
                        doc_id,
                        prompt,
                        n_results=args.n_results,
                    )
                    result = await generator.generate_project(
                        doc_id=doc_id,
                        prompt=prompt,
                        technology=technology,
                    )
                    training_examples.append(
                        build_training_record(
                            source=source,
                            technology=technology.value,
                            prompt=prompt,
                            context_chunks=context_chunks,
                            result=result,
                        )
                    )
                    print(f"  Collected {technology.value}: {prompt[:60]}...")
                except Exception as exc:
                    print(f"  Failed {technology.value}: {exc}")

    return training_examples


def write_jsonl(path: Path, records: List[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")


async def main() -> None:
    args = parse_args()
    examples = await collect_examples(args)
    write_jsonl(args.output, examples)
    print(f"Wrote {len(examples)} training examples to {args.output}")


if __name__ == "__main__":
    asyncio.run(main())
