"""Shared helpers for the LlamaIndex Respan examples."""

from __future__ import annotations

from contextlib import contextmanager
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
from uuid import uuid4

from dotenv import load_dotenv
from llama_index.core import Document, Settings
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
from respan import Respan

from respan_instrumentation_llama_index import LlamaIndexInstrumentor


@dataclass(frozen=True)
class GatewaySettings:
    api_key: str
    base_url: str
    model: str
    embedding_model: str


@dataclass(frozen=True)
class ExampleContext:
    respan: Respan
    settings: GatewaySettings
    example_name: str
    run_id: str


def load_gateway_settings() -> GatewaySettings:
    _load_env_files()
    api_key = os.environ["RESPAN_API_KEY"]
    base_url = os.getenv("RESPAN_BASE_URL", "https://api.respan.ai/api")
    os.environ["OPENAI_API_KEY"] = api_key
    os.environ["OPENAI_BASE_URL"] = base_url
    os.environ["OPENAI_API_BASE"] = base_url
    return GatewaySettings(
        api_key=api_key,
        base_url=base_url,
        model=os.getenv("RESPAN_MODEL", "gpt-4o-mini"),
        embedding_model=os.getenv("RESPAN_EMBEDDING_MODEL", "text-embedding-3-small"),
    )


def create_respan(
    *,
    app_name: str,
    example_name: str,
    capture_content: bool = True,
    **kwargs,
) -> ExampleContext:
    settings = load_gateway_settings()
    run_id = os.getenv("RESPAN_EXAMPLE_RUN_ID") or uuid4().hex[:8]
    metadata = {
        "example_set": "llama-index",
        "example_name": example_name,
        "example_run_id": run_id,
    }
    metadata.update(kwargs.pop("metadata", {}))
    respan = Respan(
        app_name=app_name,
        api_key=settings.api_key,
        base_url=settings.base_url,
        metadata=metadata,
        instrumentations=[
            LlamaIndexInstrumentor(capture_content=capture_content),
        ],
        **kwargs,
    )
    return ExampleContext(
        respan=respan,
        settings=settings,
        example_name=example_name,
        run_id=run_id,
    )


@contextmanager
def traced_example(context: ExampleContext, *, root_span_name: str | None = None):
    with context.respan.propagate_attributes(
        trace_group_identifier=f"{context.example_name}-{context.run_id}",
        custom_identifier=f"{context.example_name}-{context.run_id}",
        metadata={
            "example_set": "llama-index",
            "example_name": context.example_name,
            "example_run_id": context.run_id,
        },
    ):
        if root_span_name is None:
            yield
            return

        client = context.respan.telemetry.get_client()
        with client.start_span(root_span_name, kind="workflow"):
            yield


def configure_llama_index(settings: GatewaySettings) -> None:
    Settings.llm = OpenAI(
        model=settings.model,
        api_key=settings.api_key,
        api_base=settings.base_url,
    )
    Settings.embed_model = OpenAIEmbedding(
        model=settings.embedding_model,
        api_key=settings.api_key,
        api_base=settings.base_url,
    )


def build_llm(settings: GatewaySettings) -> OpenAI:
    return OpenAI(
        model=settings.model,
        api_key=settings.api_key,
        api_base=settings.base_url,
    )


def build_embedding_model(settings: GatewaySettings) -> OpenAIEmbedding:
    return OpenAIEmbedding(
        model=settings.embedding_model,
        api_key=settings.api_key,
        api_base=settings.base_url,
    )


def sample_documents() -> list[Document]:
    return [
        Document(
            text=(
                "Respan captures traces for LLM calls, tool calls, and workflow "
                "steps so teams can inspect application behavior."
            )
        ),
        Document(
            text=(
                "LlamaIndex applications often combine query engines, retrievers, "
                "agents, and tools into one request path."
            )
        ),
    ]


def print_result(label: str, value: object) -> None:
    print(f"{label}: {value}")


def _load_env_files() -> None:
    for env_path in _env_paths_from(start=Path(__file__).resolve().parent):
        load_dotenv(env_path, override=True)
    for env_path in _env_paths_from(start=Path.cwd()):
        load_dotenv(env_path, override=True)


def _env_paths_from(*, start: Path) -> Iterable[Path]:
    current = start.resolve()
    chain: list[Path] = []
    while True:
        chain.append(current)
        if (current / ".git").exists():
            break
        if current.parent == current:
            break
        current = current.parent

    seen: set[Path] = set()
    for directory in reversed(chain):
        env_path = directory / ".env"
        if env_path.exists() and env_path not in seen:
            seen.add(env_path)
            yield env_path
