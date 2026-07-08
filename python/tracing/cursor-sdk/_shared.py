from __future__ import annotations

import json
import os
from contextlib import contextmanager
from pathlib import Path
from typing import Any
from uuid import uuid4

from dotenv import load_dotenv
from respan import Respan, propagate_attributes
from respan_instrumentation_cursor_sdk import CursorSDKInstrumentor

PROJECT_ROOT = Path(__file__).resolve().parents[3]
EXAMPLE_DIR = Path(__file__).resolve().parent
DEFAULT_RESPAN_BASE_URL = "https://api.respan.ai/api"
DEFAULT_MODEL = "claude-4-sonnet"
DEFAULT_CURSOR_VERSION = "1.0.0"


def load_root_env() -> None:
    load_dotenv(PROJECT_ROOT / ".env", override=True)


def require_respan_api_key() -> str:
    load_root_env()
    api_key = os.getenv("RESPAN_API_KEY")
    if not api_key:
        raise RuntimeError("RESPAN_API_KEY must be set in the repo root .env file")
    return api_key


def respan_base_url() -> str:
    return os.getenv("RESPAN_BASE_URL", DEFAULT_RESPAN_BASE_URL).rstrip("/")


def model_name() -> str:
    return os.getenv("CURSOR_EXAMPLE_MODEL", DEFAULT_MODEL)


def cursor_version() -> str:
    return os.getenv("CURSOR_EXAMPLE_VERSION", DEFAULT_CURSOR_VERSION)


def workflow_name(example_name: str) -> str:
    return f"cursor_sdk_{example_name.replace('-', '_')}"


def conversation_id(example_name: str) -> str:
    return f"sdk_{example_name.replace('-', '_')}"


def generation_id(example_name: str, run_id: str) -> str:
    return f"gen_{example_name.replace('-', '_')}_{run_id[-8:]}"


def state_path(run_id: str) -> Path:
    state_dir = EXAMPLE_DIR / ".cursor_state"
    state_dir.mkdir(exist_ok=True)
    return state_dir / f"{run_id}.json"


def make_custom_identifier(example_name: str) -> str:
    return f"cursor-sdk-{example_name}-{uuid4().hex[:8]}"


def make_event(
    example_name: str,
    run_id: str,
    hook_event_name: str,
    **payload: Any,
) -> dict[str, Any]:
    event = {
        "hook_event_name": hook_event_name,
        "conversation_id": conversation_id(example_name),
        "generation_id": generation_id(example_name, run_id),
        "model": model_name(),
        "cursor_version": cursor_version(),
    }
    event.update(payload)
    return event


def make_respan(example_name: str, state_file: Path) -> tuple[Respan, CursorSDKInstrumentor]:
    api_key = require_respan_api_key()
    instrumentor = CursorSDKInstrumentor(state_path=state_file)
    respan = Respan(
        api_key=api_key,
        base_url=respan_base_url(),
        app_name="cursor-sdk-examples",
        instrumentations=[instrumentor],
        environment=os.getenv("RESPAN_ENVIRONMENT", "example"),
        metadata={"integration": "cursor-sdk", "example": example_name},
        is_batching_enabled=False,
    )
    return respan, instrumentor


@contextmanager
def example_attributes(example_name: str, run_id: str):
    current_workflow_name = workflow_name(example_name)
    with propagate_attributes(
        custom_identifier=run_id,
        trace_group_identifier=current_workflow_name,
        metadata={
            "example": example_name,
            "run_id": run_id,
            "workflow_name": current_workflow_name,
            "integration": "cursor-sdk",
        },
    ):
        yield


def replay_events(
    example_name: str,
    events: list[dict[str, Any]],
    *,
    run_id: str | None = None,
) -> list[Any]:
    run_id = run_id or make_custom_identifier(example_name)
    state_file = state_path(run_id)
    if state_file.exists():
        state_file.unlink()

    respan, instrumentor = make_respan(example_name, state_file)
    print_start(example_name, run_id)
    results = []
    with example_attributes(example_name, run_id):
        for event in events:
            result = instrumentor.process_event(event)
            results.append(result)
            print(
                f"event={result.event_name} emitted={result.emitted} span={result.span_name}",
                flush=True,
            )
    finish_respan(respan)
    return results


def print_start(example_name: str, run_id: str) -> None:
    print(f"example={example_name}", flush=True)
    print(f"custom_identifier={run_id}", flush=True)
    print(f"workflow_name={workflow_name(example_name)}", flush=True)
    print(f"conversation_id={conversation_id(example_name)}", flush=True)
    print(f"model={model_name()}", flush=True)


def print_json(label: str, value: Any) -> None:
    print(f"\n== {label} ==")
    print(json.dumps(value, default=str, indent=2, sort_keys=True))


def finish_respan(respan: Respan) -> None:
    respan.telemetry.flush()
