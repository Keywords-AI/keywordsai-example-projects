"""Shared Respan Tracing and Instructor setup for the example scripts."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import instructor
from dotenv import load_dotenv
from respan import Respan
from respan_instrumentation_instructor import InstructorInstrumentor

REPO_ROOT = Path(__file__).resolve().parents[3]


def create_respan_instructor_client(
    *,
    app_name: str,
    async_client: bool = False,
) -> tuple[Respan, Any]:
    """Create an Instructor client routed through the Respan gateway."""
    load_dotenv(REPO_ROOT / ".env", override=True)

    respan_api_key = os.environ["RESPAN_API_KEY"]
    respan_base_url = os.getenv("RESPAN_BASE_URL", "https://api.respan.ai/api")
    model = os.getenv("INSTRUCTOR_MODEL", "gpt-4o-mini")

    run_id = os.getenv("RESPAN_EXAMPLE_RUN_ID", "instructor-local")
    respan = Respan(
        api_key=respan_api_key,
        base_url=respan_base_url,
        app_name=app_name,
        instrumentations=[InstructorInstrumentor()],
        metadata={
            "example_set": "instructor",
            "run_id": run_id,
        },
        environment="examples",
        is_batching_enabled=False,
    )
    client = instructor.from_provider(
        f"openai/{model}",
        api_key=respan_api_key,
        base_url=respan_base_url,
        async_client=async_client,
        mode=instructor.Mode.TOOLS,
    )
    return respan, client
