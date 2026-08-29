"""Shared setup for AgentOps tracing examples."""

from __future__ import annotations

import os
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from respan import Respan, propagate_attributes
from respan_instrumentation_agentops import AgentOpsInstrumentor

REPO_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(REPO_ROOT / ".env", override=True)

DEFAULT_RESPAN_BASE_URL = "https://api.respan.ai/api"
DEFAULT_RUN_ID = datetime.now(timezone.utc).strftime("agentops-%Y%m%d-%H%M%S")
DEFAULT_GROUP_IDENTIFIER = "otel2-python-agent-frameworks"


def _required_env(name: str) -> str:
    value = os.getenv(name)
    if value:
        return value
    raise RuntimeError(f"Missing {name} in {REPO_ROOT / '.env'}")


def build_respan(*, example_name: str, workflow_name: str) -> Respan:
    run_id = os.getenv("RESPAN_EXAMPLE_RUN_ID", DEFAULT_RUN_ID)
    group_identifier = os.getenv(
        "RESPAN_EXAMPLE_GROUP_ID",
        DEFAULT_GROUP_IDENTIFIER,
    )
    return Respan(
        api_key=_required_env("RESPAN_API_KEY"),
        base_url=os.getenv("RESPAN_BASE_URL", DEFAULT_RESPAN_BASE_URL),
        app_name=f"agentops-{example_name}",
        instrumentations=[AgentOpsInstrumentor()],
        customer_identifier="agentops-example-user",
        thread_identifier=f"{group_identifier}:{example_name}",
        metadata={
            "integration": "agentops",
            "example": example_name,
            "run_id": run_id,
            "workflow_name": workflow_name,
        },
        environment="examples",
    )


@contextmanager
def example_scope(example_name: str):
    run_id = os.getenv("RESPAN_EXAMPLE_RUN_ID", DEFAULT_RUN_ID)
    group_identifier = os.getenv(
        "RESPAN_EXAMPLE_GROUP_ID",
        DEFAULT_GROUP_IDENTIFIER,
    )
    with propagate_attributes(
        trace_group_identifier=group_identifier,
        custom_identifier=f"{run_id}:{example_name}",
    ):
        yield
