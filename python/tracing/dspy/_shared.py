"""Shared setup helpers for DSPy + Respan examples."""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
import json
import os
from pathlib import Path
from typing import Any, Iterable
from uuid import uuid4

import dspy
from dotenv import load_dotenv
from opentelemetry.semconv_ai import SpanAttributes
from respan import Respan
from respan_instrumentation_dspy import DSPyInstrumentor

DEFAULT_RESPAN_BASE_URL = "https://api.respan.ai/api"
DEFAULT_DSPY_MODEL = "openai/gpt-4o-mini"


@dataclass(frozen=True)
class GatewaySettings:
    api_key: str
    base_url: str
    model: str


@dataclass(frozen=True)
class ExampleContext:
    respan: Respan
    settings: GatewaySettings
    example_name: str
    run_id: str


@dataclass(frozen=True)
class ExampleSpan:
    span: Any | None

    def set_input(self, value: object) -> None:
        _set_json_attribute(
            span=self.span,
            attribute=SpanAttributes.TRACELOOP_ENTITY_INPUT,
            value=value,
        )

    def set_output(self, value: object) -> None:
        _set_json_attribute(
            span=self.span,
            attribute=SpanAttributes.TRACELOOP_ENTITY_OUTPUT,
            value=value,
        )


def load_gateway_settings() -> GatewaySettings:
    """Load env files and return gateway settings for DSPy."""
    _load_env_files()
    api_key = os.environ["RESPAN_API_KEY"]
    base_url = os.getenv("RESPAN_BASE_URL", DEFAULT_RESPAN_BASE_URL)
    model = (
        os.getenv("RESPAN_DSPY_MODEL")
        or os.getenv("RESPAN_MODEL")
        or DEFAULT_DSPY_MODEL
    )

    os.environ["OPENAI_API_KEY"] = api_key
    os.environ["OPENAI_BASE_URL"] = base_url
    os.environ["OPENAI_API_BASE"] = base_url
    return GatewaySettings(
        api_key=api_key,
        base_url=base_url,
        model=_normalize_dspy_model(model),
    )


def create_respan(
    *,
    app_name: str,
    example_name: str,
    include_content: bool = True,
    temperature: float = 0.2,
) -> ExampleContext:
    """Start Respan tracing and configure DSPy gateway routing."""
    settings = load_gateway_settings()
    run_id = os.getenv("RESPAN_EXAMPLE_RUN_ID") or uuid4().hex[:8]
    metadata = {
        "example_set": "dspy",
        "example_name": example_name,
        "example_run_id": run_id,
        "run_id": run_id,
    }
    respan = Respan(
        api_key=settings.api_key,
        base_url=settings.base_url,
        app_name=app_name,
        metadata=metadata,
        instrumentations=[
            DSPyInstrumentor(include_content=include_content),
        ],
    )
    dspy.configure(
        lm=dspy.LM(
            settings.model,
            api_key=settings.api_key,
            api_base=settings.base_url,
            cache=False,
            temperature=temperature,
        )
    )
    return ExampleContext(
        respan=respan,
        settings=settings,
        example_name=example_name,
        run_id=run_id,
    )


@contextmanager
def managed_example(
    *,
    app_name: str,
    example_name: str,
    include_content: bool = True,
    temperature: float = 0.2,
):
    """Create one example context and always shut down its exporter."""
    context = create_respan(
        app_name=app_name,
        example_name=example_name,
        include_content=include_content,
        temperature=temperature,
    )
    try:
        yield context
    finally:
        context.respan.shutdown()


@contextmanager
def traced_example(
    context: ExampleContext,
    *,
    root_span_name: str | None = None,
    input_data: object | None = None,
):
    """Group one script run under a recognizable root workflow span."""
    span_name = root_span_name or f"dspy_example_{context.example_name}"
    with context.respan.propagate_attributes(
        trace_group_identifier=f"{context.example_name}-{context.run_id}",
        custom_identifier=context.run_id,
        thread_identifier=f"dspy_example_{context.example_name}",
        metadata={
            "example_set": "dspy",
            "example_name": context.example_name,
            "example_run_id": context.run_id,
            "run_id": context.run_id,
        },
    ):
        client = context.respan.telemetry.get_client()
        with client.start_span(span_name, kind="workflow") as span:
            example_span = ExampleSpan(span=span)
            if input_data is not None:
                example_span.set_input(input_data)
            yield example_span


def print_result(label: str, value: object) -> None:
    print(f"{label}: {value}")


def _normalize_dspy_model(model: str) -> str:
    if "/" in model:
        return model
    return f"openai/{model}"


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


def _set_json_attribute(*, span: Any | None, attribute: str, value: object) -> None:
    if span is None:
        return
    try:
        payload = json.dumps(value, default=str)
    except (TypeError, ValueError):
        payload = str(value)
    if len(payload) < 1_000_000:
        span.set_attribute(attribute, payload)
