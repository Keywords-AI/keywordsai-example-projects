#!/usr/bin/env python3
"""
Tracing — Workflow + task with one short question, one short reply.

Keeps the trace structure (Workflow -> Task -> LLM call) but uses minimal
chat content so the trace UI stays easy to scan.
"""

import os
import uuid
from dotenv import load_dotenv
from dify_client.models import ChatRequest, ResponseMode
from respan_exporter_dify import create_client, flush_pending_exports
from respan_tracing import RespanTelemetry
from respan_tracing.decorators import workflow, task

load_dotenv(override=True)

telemetry = RespanTelemetry(
    app_name="dify-tracing-example",
    api_key=os.getenv("RESPAN_API_KEY"),
)

respan_client = create_client(
    api_key=os.getenv("RESPAN_API_KEY", "your-respan-api-key"),
    gateway_base_url=os.getenv("RESPAN_BASE_URL"),
    gateway_model=os.getenv("RESPAN_MODEL", "gpt-4o"),
)


@task(name="prepare_request")
def prepare_request() -> ChatRequest:
    """Build a minimal chat request: one short question."""
    return ChatRequest(
        query="What is 2+2?",
        user=f"user-{uuid.uuid4().hex[:8]}",
        response_mode=ResponseMode.BLOCKING,
        inputs={},
    )


@workflow(name="dify_simple_trace")
def run_simple_trace() -> str:
    """One task (prepare) + one LLM call; single short reply."""
    req = prepare_request()
    response = respan_client.chat_messages(req=req)
    return response.answer.strip()


def main():
    try:
        answer = run_simple_trace()
        print(answer)
    finally:
        telemetry.flush()
        flush_pending_exports(timeout=20)


if __name__ == "__main__":
    main()
