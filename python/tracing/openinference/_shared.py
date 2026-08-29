from __future__ import annotations

import os
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from opentelemetry import trace
from opentelemetry.sdk.trace import SpanProcessor
from respan import Respan, propagate_attributes
from respan_instrumentation_openinference import OpenInferenceInstrumentor

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_RESPAN_BASE_URL = "https://api.respan.ai/api"
INTEGRATION = "openinference"


class ContractSourceProcessor(SpanProcessor):
    """No-op source processor used to activate the generic OI translator."""

    def on_start(self, span: Any, parent_context: Any = None) -> None:
        del span, parent_context

    def on_end(self, span: Any) -> None:
        del span

    def shutdown(self) -> None:
        pass

    def force_flush(self, timeout_millis: int = 30_000) -> bool:
        del timeout_millis
        return True


def load_root_env() -> None:
    # An exact shell marker must win over any value in the repository .env.
    load_dotenv(PROJECT_ROOT / ".env", override=False)


def require_respan_api_key() -> str:
    load_root_env()
    api_key = os.getenv("RESPAN_API_KEY")
    if not api_key:
        raise RuntimeError("RESPAN_API_KEY must be set in the repo-root .env")
    return api_key


def example_run_id() -> str:
    load_root_env()
    inherited = os.getenv("RESPAN_EXAMPLE_RUN_ID")
    if inherited:
        return inherited
    return f"openinference-{datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')}"


def make_respan(example_name: str, run_id: str) -> Respan:
    current_workflow = workflow_name(example_name)
    return Respan(
        api_key=require_respan_api_key(),
        base_url=os.getenv("RESPAN_BASE_URL", DEFAULT_RESPAN_BASE_URL).rstrip("/"),
        app_name="openinference-contract-examples",
        environment=os.getenv("RESPAN_ENVIRONMENT", "example"),
        metadata={
            "example_run_id": run_id,
            "integration": INTEGRATION,
            "example": example_name,
            "workflow_name": current_workflow,
        },
        instrumentations=[OpenInferenceInstrumentor(ContractSourceProcessor)],
    )


def workflow_name(example_name: str) -> str:
    return f"openinference_{example_name.replace('-', '_')}"


@contextmanager
def example_attributes(example_name: str, run_id: str) -> Iterator[None]:
    current_workflow = workflow_name(example_name)
    with propagate_attributes(
        custom_identifier=f"{INTEGRATION}-{example_name}-{run_id}",
        trace_group_identifier=current_workflow,
        metadata={
            "example_run_id": run_id,
            "integration": INTEGRATION,
            "example": example_name,
            "workflow_name": current_workflow,
        },
    ):
        yield


def tracer():
    return trace.get_tracer("openinference.contract.examples")


def finish_respan(respan: Respan) -> None:
    try:
        respan.flush()
    finally:
        respan.shutdown()


def print_result(example_name: str, run_id: str, result: str) -> None:
    print(f"example={example_name}")
    print(f"example_run_id={run_id}")
    print(f"workflow_name={workflow_name(example_name)}")
    print(result)
