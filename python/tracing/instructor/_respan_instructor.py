"""Shared Respan Tracing and Instructor setup for the example scripts."""

from __future__ import annotations

import os
from typing import Any

import instructor
from dotenv import find_dotenv
from dotenv import load_dotenv
from respan_tracing import RespanTelemetry
from respan_instrumentation_instructor import InstructorInstrumentor


def create_respan_instructor_client(
    *,
    app_name: str,
    async_client: bool = False,
) -> tuple[RespanTelemetry, Any]:
    """Create an Instructor client routed through the Respan gateway."""
    load_dotenv(find_dotenv(), override=True)

    respan_api_key = os.environ["RESPAN_API_KEY"]
    respan_base_url = os.getenv("RESPAN_BASE_URL", "https://api.respan.ai/api")
    model = os.getenv("INSTRUCTOR_MODEL", "gpt-4o-mini")

    telemetry = RespanTelemetry(
        api_key=respan_api_key,
        base_url=respan_base_url,
        app_name=app_name,
        is_auto_instrument=False,
    )
    InstructorInstrumentor().activate()
    client = instructor.from_provider(
        f"openai/{model}",
        api_key=respan_api_key,
        base_url=respan_base_url,
        async_client=async_client,
        mode=instructor.Mode.TOOLS,
    )
    return telemetry, client
