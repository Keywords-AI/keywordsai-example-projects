import os
import time
from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import TypeVar

from dotenv import load_dotenv
from respan import Respan
from respan_instrumentation_litellm import LiteLLMInstrumentor

ROOT_DIR = Path(__file__).resolve().parents[3]
load_dotenv(ROOT_DIR / ".env", override=True)

RESPAN_API_KEY = os.environ["RESPAN_API_KEY"]
GATEWAY_API_KEY = os.getenv("RESPAN_GATEWAY_API_KEY") or RESPAN_API_KEY
GATEWAY_BASE_URL = (
    os.getenv("RESPAN_GATEWAY_BASE_URL")
    or os.getenv("RESPAN_BASE_URL")
    or "https://api.respan.ai/api"
)
MODEL = os.getenv("RESPAN_LITELLM_MODEL") or os.getenv("RESPAN_MODEL", "gpt-4o-mini")


def _example_run_id() -> str:
    configured = os.getenv("RESPAN_EXAMPLE_RUN_ID", "").strip()
    if configured and "codex" not in configured.lower():
        return configured
    return f"litellm-{int(time.time())}"


RUN_ID = _example_run_id()

T = TypeVar("T")


def create_respan(app_name: str) -> Respan:
    return Respan(
        api_key=RESPAN_API_KEY,
        base_url=os.getenv("RESPAN_BASE_URL", "https://api.respan.ai/api"),
        app_name=app_name,
        instrumentations=[LiteLLMInstrumentor()],
        is_batching_enabled=False,
    )


def run_with_example_attributes(
    respan: Respan,
    *,
    workflow_name: str,
    action: Callable[[], T],
) -> T:
    with respan.propagate_attributes(
        trace_group_identifier=workflow_name,
        custom_identifier=f"{RUN_ID}:{workflow_name}",
        metadata={
            "example": "litellm",
            "example_run_id": RUN_ID,
            "workflow_name": workflow_name,
        },
    ):
        return action()


async def run_async_with_example_attributes(
    respan: Respan,
    *,
    workflow_name: str,
    action: Callable[[], Awaitable[T]],
) -> T:
    with respan.propagate_attributes(
        trace_group_identifier=workflow_name,
        custom_identifier=f"{RUN_ID}:{workflow_name}",
        metadata={
            "example": "litellm",
            "example_run_id": RUN_ID,
            "workflow_name": workflow_name,
        },
    ):
        return await action()
