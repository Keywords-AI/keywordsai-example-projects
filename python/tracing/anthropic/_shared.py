"""Shared helpers for the dedicated Python Anthropic examples."""

from __future__ import annotations

import os
import sys
from contextlib import contextmanager
from pathlib import Path
from uuid import uuid4

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[3]
WORKSPACE_ROOT = PROJECT_ROOT.parent
LOCAL_RESPAN_REPO = Path(os.getenv("RESPAN_REPO", WORKSPACE_ROOT / "respan"))
for local_path in (
    LOCAL_RESPAN_REPO / "python-sdks/respan-sdk/src",
    LOCAL_RESPAN_REPO / "python-sdks/respan-tracing/src",
    LOCAL_RESPAN_REPO / "python-sdks/respan/src",
    LOCAL_RESPAN_REPO
    / "python-sdks/instrumentations/respan-instrumentation-anthropic/src",
):
    if local_path.exists():
        sys.path.insert(0, str(local_path))

from anthropic import Anthropic
from respan import Respan
from respan_instrumentation_anthropic import AnthropicInstrumentor

DEFAULT_RESPAN_BASE_URL = "https://api.respan.ai/api"
DEFAULT_MODEL = "claude-sonnet-4-5-20250929"
_DEFAULT_RUN_ID = f"python-anthropic-{uuid4().hex[:8]}"


def load_root_env() -> None:
    load_dotenv(PROJECT_ROOT / ".env", override=True)


def require_respan_api_key() -> str:
    load_root_env()
    api_key = os.getenv("RESPAN_API_KEY") or os.getenv("RESPAN_GATEWAY_API_KEY")
    if not api_key:
        raise RuntimeError("RESPAN_API_KEY must be set in the repo root .env file")
    return api_key


def respan_base_url() -> str:
    return os.getenv("RESPAN_BASE_URL", DEFAULT_RESPAN_BASE_URL).rstrip("/")


def anthropic_base_url() -> str:
    explicit = os.getenv("RESPAN_ANTHROPIC_GATEWAY_BASE_URL")
    if explicit:
        return explicit.rstrip("/")
    base_url = os.getenv("RESPAN_GATEWAY_BASE_URL", respan_base_url()).rstrip("/")
    return base_url if base_url.endswith("/anthropic") else f"{base_url}/anthropic"


def model_name() -> str:
    return os.getenv("RESPAN_ANTHROPIC_MODEL", DEFAULT_MODEL)


def example_run_id() -> str:
    return os.getenv("RESPAN_EXAMPLE_RUN_ID") or _DEFAULT_RUN_ID


def workflow_name(case_id: str) -> str:
    return f"python_anthropic_{case_id}"


def make_respan() -> Respan:
    return Respan(
        api_key=require_respan_api_key(),
        base_url=respan_base_url(),
        app_name="python-anthropic-examples",
        instrumentations=[AnthropicInstrumentor()],
        environment=os.getenv("RESPAN_ENVIRONMENT", "example"),
        metadata={"integration": "anthropic", "run_id": example_run_id()},
    )


def make_client() -> Anthropic:
    return Anthropic(
        api_key=require_respan_api_key(),
        base_url=anthropic_base_url(),
    )


@contextmanager
def example_attributes(respan: Respan, case_id: str):
    run_id = example_run_id()
    with respan.propagate_attributes(
        custom_identifier=f"python-anthropic-{case_id}-{run_id}",
        trace_group_identifier=workflow_name(case_id),
        metadata={
            "integration": "anthropic",
            "case": case_id,
            "run_id": run_id,
        },
    ):
        yield run_id


def message_text(message) -> str:
    return "".join(
        text
        for block in message.content
        if (text := getattr(block, "text", None))
    )


def print_result(case_id: str, value: str) -> None:
    print(f"case={case_id}")
    print(f"example_run_id={example_run_id()}")
    print(f"workflow_name={workflow_name(case_id)}")
    print(value)
