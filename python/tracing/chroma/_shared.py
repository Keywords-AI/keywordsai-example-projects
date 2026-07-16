"""Shared helpers for Chroma tracing examples."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any
from uuid import uuid4

from chromadb.config import Settings
from dotenv import load_dotenv
from respan import Respan
from respan_instrumentation_chroma import ChromaInstrumentor

EXAMPLE_DIR = Path(__file__).resolve().parent
REPO_ROOT = EXAMPLE_DIR.parents[2]
RESPAN_BASE_URL = "https://api.respan.ai/api"
EXAMPLE_SET = "chroma"


class DeterministicEmbeddingFunction:
    """Small local embedding function to keep examples offline and repeatable."""

    def __call__(self, input: list[str]) -> list[list[float]]:
        return self._embed(input)

    def embed_documents(self, input: list[str]) -> list[list[float]]:
        return self._embed(input)

    def embed_query(self, input: list[str]) -> list[list[float]]:
        return self._embed(input)

    def name(self) -> str:
        return "respan-deterministic-embedding"

    def _embed(self, input: list[str]) -> list[list[float]]:
        vectors: list[list[float]] = []
        for text in input:
            normalized = str(text)
            base = sum(ord(char) for char in normalized)
            vectors.append([float((base + index * 7) % 23) / 23 for index in range(8)])
        return vectors


def load_example_env() -> None:
    env_path = REPO_ROOT / ".env"
    load_dotenv(env_path, override=True)
    if not os.getenv("RESPAN_API_KEY"):
        raise RuntimeError(f"RESPAN_API_KEY is required in {env_path}")
    os.environ.setdefault("RESPAN_BASE_URL", RESPAN_BASE_URL)


def create_respan(workflow_name: str) -> Respan:
    load_example_env()
    return Respan(
        api_key=os.environ["RESPAN_API_KEY"],
        base_url=os.getenv("RESPAN_BASE_URL", RESPAN_BASE_URL),
        app_name=workflow_name,
        metadata={
            "example_set": EXAMPLE_SET,
            "workflow_name": workflow_name,
        },
        instrumentations=[ChromaInstrumentor()],
        is_batching_enabled=False,
        log_level=os.getenv("RESPAN_LOG_LEVEL", "WARNING"),
    )


def create_chroma_client():
    import chromadb

    return chromadb.Client(Settings(anonymized_telemetry=False))


def workflow_attributes(workflow_name: str) -> dict[str, object]:
    run_id = os.getenv("RESPAN_EXAMPLE_RUN_ID") or uuid4().hex[:8]
    return {
        "trace_group_identifier": workflow_name,
        "custom_identifier": f"{workflow_name}-{run_id}",
        "metadata": {
            "example_set": EXAMPLE_SET,
            "workflow_name": workflow_name,
            "example_run_id": run_id,
        },
    }


def collection_name(workflow_name: str) -> str:
    suffix = uuid4().hex[:8]
    return f"respan_{workflow_name}_{suffix}".replace("-", "_")


def sample_records() -> dict[str, Any]:
    return {
        "ids": ["doc-python", "doc-rust", "doc-pasta"],
        "documents": [
            "Python was created by Guido van Rossum and first released in 1991.",
            "Rust is a systems programming language focused on safety and performance.",
            "Pasta water should be salted before noodles are added.",
        ],
        "metadatas": [
            {"topic": "programming", "source": "python", "rank": 1},
            {"topic": "programming", "source": "rust", "rank": 2},
            {"topic": "cooking", "source": "pasta", "rank": 3},
        ],
        "embeddings": [
            [0.9, 0.1, 0.0, 0.0],
            [0.7, 0.3, 0.0, 0.0],
            [0.1, 0.9, 0.0, 0.0],
        ],
    }


def compact_result(value: Any) -> Any:
    if isinstance(value, dict):
        result: dict[str, Any] = {}
        for key, item in value.items():
            if key in {"embeddings", "data"}:
                result[key] = "present" if item is not None else None
            else:
                result[key] = compact_result(item)
        return result
    if isinstance(value, list):
        return [compact_result(item) for item in value]
    return value


def print_result(label: str, value: Any) -> None:
    print(f"\n== {label} ==")
    print(json.dumps(compact_result(value), default=str, indent=2, sort_keys=True))


def finish_respan(respan: Respan) -> None:
    respan.shutdown()
