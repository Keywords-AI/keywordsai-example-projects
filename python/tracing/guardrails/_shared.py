"""Shared setup for Guardrails AI tracing examples."""

import json
import os
from contextlib import contextmanager
from pathlib import Path
from typing import Any
from uuid import uuid4

from dotenv import load_dotenv
from respan import Respan, get_client, propagate_attributes
from respan_instrumentation_guardrails import GuardrailsInstrumentor


def load_guardrails_example_environment() -> tuple[str, str, str]:
    env_path = Path(__file__).resolve().parents[3] / ".env"
    load_dotenv(env_path, override=True)

    respan_api_key = os.environ["RESPAN_API_KEY"]
    respan_base_url = os.getenv("RESPAN_BASE_URL", "https://api.respan.ai/api")
    model = os.getenv("RESPAN_MODEL", "gpt-4o-mini")

    os.environ["OPENAI_API_KEY"] = respan_api_key
    os.environ["OPENAI_BASE_URL"] = respan_base_url
    os.environ["OPENAI_API_BASE"] = respan_base_url

    return respan_api_key, respan_base_url, model


def make_respan(app_name: str) -> tuple[Respan, str]:
    respan_api_key, respan_base_url, model = load_guardrails_example_environment()
    instrumentor = GuardrailsInstrumentor()
    respan = Respan(
        api_key=respan_api_key,
        base_url=respan_base_url,
        app_name=app_name,
        instrumentations=[instrumentor],
        is_auto_instrument=True,
    )
    if not instrumentor.is_instrumented:
        respan.shutdown()
        raise RuntimeError("Guardrails instrumentation did not activate")
    return respan, model


@contextmanager
def example_attributes(
    example_name: str,
    workflow_name: str,
    *,
    customer_identifier: str | None = None,
    thread_identifier: str | None = None,
):
    run_id = os.getenv("RESPAN_EXAMPLE_RUN_ID") or f"guardrails-{uuid4().hex[:12]}"
    attributes: dict[str, Any] = {
        "custom_identifier": f"guardrails-{example_name}-{uuid4().hex[:8]}",
        "trace_group_identifier": workflow_name,
        "metadata": {
            "example": example_name,
            "run_id": run_id,
            "workflow_name": workflow_name,
        },
    }
    if customer_identifier is not None:
        attributes["customer_identifier"] = customer_identifier
    if thread_identifier is not None:
        attributes["thread_identifier"] = thread_identifier
    with propagate_attributes(
        **attributes,
    ):
        yield run_id


def set_workflow_input(payload: dict[str, Any]) -> None:
    get_client().update_current_span(
        attributes={"traceloop.entity.input": json.dumps(payload, default=str)}
    )


def result_summary(result: Any) -> dict[str, Any]:
    return {
        "validation_passed": bool(getattr(result, "validation_passed", False)),
        "validated_output": getattr(result, "validated_output", None),
        "raw_llm_output": getattr(result, "raw_llm_output", None),
        "error": getattr(result, "error", None),
    }
