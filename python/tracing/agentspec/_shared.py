"""Shared setup for AgentSpec tracing examples."""

import os
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from respan import Respan, propagate_attributes
from respan_instrumentation_agentspec import AgentSpecInstrumentor


EXAMPLE_ROOT = Path(__file__).resolve().parent
REPO_ROOT = EXAMPLE_ROOT.parents[2]
DEFAULT_RESPAN_BASE_URL = "https://api.respan.ai/api"
DEFAULT_MODEL = "gpt-4.1-nano"
DEFAULT_RUN_ID = datetime.now(timezone.utc).strftime("agentspec-%Y%m%d-%H%M%S")
DEFAULT_GROUP_IDENTIFIER = "otel2-python-agent-frameworks"


def configure_gateway() -> tuple[str, str, str]:
    """Load the repo-root env file and point OpenAI-compatible calls at Respan."""
    load_dotenv(REPO_ROOT / ".env", override=True)

    respan_api_key = os.getenv("RESPAN_GATEWAY_API_KEY") or os.getenv("RESPAN_API_KEY")
    if not respan_api_key:
        raise RuntimeError("RESPAN_GATEWAY_API_KEY or RESPAN_API_KEY is required")

    respan_base_url = (
        os.getenv("RESPAN_GATEWAY_BASE_URL")
        or os.getenv("RESPAN_BASE_URL")
        or DEFAULT_RESPAN_BASE_URL
    )
    model = os.getenv("RESPAN_MODEL", DEFAULT_MODEL)

    os.environ["OPENAI_API_KEY"] = respan_api_key
    os.environ["OPENAI_BASE_URL"] = respan_base_url
    return respan_api_key, respan_base_url, model


def build_respan(
    *,
    example_name: str,
    workflow_name: str,
    use_static_identity: bool = True,
) -> tuple[Respan, str]:
    """Create a marked, locally instrumented AgentSpec Respan instance."""
    respan_api_key, respan_base_url, model = configure_gateway()
    run_id = os.getenv("RESPAN_EXAMPLE_RUN_ID", DEFAULT_RUN_ID)
    group_identifier = os.getenv(
        "RESPAN_EXAMPLE_GROUP_ID",
        DEFAULT_GROUP_IDENTIFIER,
    )
    identity_kwargs: dict[str, str] = {}
    if use_static_identity:
        identity_kwargs = {
            "customer_identifier": "agentspec-example-user",
            "thread_identifier": f"{group_identifier}:{example_name}",
        }

    return (
        Respan(
            api_key=respan_api_key,
            base_url=respan_base_url,
            app_name=f"agentspec-{example_name}",
            instrumentations=[AgentSpecInstrumentor(workflow_name=workflow_name)],
            metadata={
                "integration": "agentspec",
                "example": example_name,
                "run_id": run_id,
                "workflow_name": workflow_name,
            },
            environment="examples",
            **identity_kwargs,
        ),
        model,
    )


@contextmanager
def example_scope(
    example_name: str,
    *,
    customer_identifier: str | None = None,
    thread_identifier: str | None = None,
    metadata: dict[str, Any] | None = None,
):
    run_id = os.getenv("RESPAN_EXAMPLE_RUN_ID", DEFAULT_RUN_ID)
    group_identifier = os.getenv(
        "RESPAN_EXAMPLE_GROUP_ID",
        DEFAULT_GROUP_IDENTIFIER,
    )
    attrs: dict[str, Any] = {
        "trace_group_identifier": group_identifier,
        "custom_identifier": f"{run_id}:{example_name}",
    }
    if customer_identifier is not None:
        attrs["customer_identifier"] = customer_identifier
    if thread_identifier is not None:
        attrs["thread_identifier"] = thread_identifier
    if metadata is not None:
        attrs["metadata"] = metadata

    with propagate_attributes(**attrs):
        yield


def latest_message_content(result: dict[str, Any]) -> str:
    """Extract the final assistant message text from a LangGraph AgentSpec run."""
    messages = result.get("messages", [])
    if not messages:
        return ""

    latest_message = messages[-1]
    content = getattr(latest_message, "content", None)
    if content is None and isinstance(latest_message, dict):
        content = latest_message.get("content")
    return str(content or "")
