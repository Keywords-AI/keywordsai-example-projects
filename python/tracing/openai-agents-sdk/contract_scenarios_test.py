"""Deterministic current-SDK traces for content-level instrumentation checks."""

# ruff: noqa: SIM117 - nesting is the span-tree contract under test.

from __future__ import annotations

import os

from agents.tracing import (
    SpanError,
    agent_span,
    function_span,
    generation_span,
    guardrail_span,
    handoff_span,
    set_trace_processors,
    task_span,
    trace,
    turn_span,
)

from respan_exporter_openai_agents import RespanTraceProcessor

set_trace_processors(
    [
        RespanTraceProcessor(
            os.getenv("RESPAN_API_KEY"),
            endpoint=os.getenv("RESPAN_OAIA_TRACING_ENDPOINT"),
        )
    ]
)


def _metadata(scenario: str) -> dict[str, str]:
    marker = os.environ["RESPAN_EXAMPLE_RUN_ID"]
    return {"example_run_id": marker, "scenario": scenario}


def test_success_structure():
    with trace("openai-agents.success", metadata=_metadata("success")):
        with task_span("successful agent run"):
            with agent_span("Assistant", output_type="str"):
                with turn_span(1, "Assistant"):
                    with generation_span(
                        input=[{"role": "user", "content": "Say hello."}],
                        output=[{"role": "assistant", "content": "Hello!"}],
                        model="gpt-4o-mini",
                        usage={
                            "input_tokens": 4,
                            "output_tokens": 2,
                            "total_tokens": 6,
                        },
                    ):
                        pass


def test_function_tool_structure():
    with trace("openai-agents.tool", metadata=_metadata("tool")):
        with task_span("tool agent run"):
            with agent_span("Weather Agent", tools=["get_weather"]):
                with turn_span(1, "Weather Agent"):
                    with generation_span(
                        input=[
                            {
                                "role": "user",
                                "content": "What is the weather in Tokyo?",
                            }
                        ],
                        output=[
                            {
                                "role": "assistant",
                                "content": None,
                                "tool_calls": [
                                    {
                                        "id": "call_weather_1",
                                        "type": "function",
                                        "function": {
                                            "name": "get_weather",
                                            "arguments": '{"city":"Tokyo"}',
                                        },
                                    }
                                ],
                            }
                        ],
                        model="gpt-4o-mini",
                        usage={"input_tokens": 10, "output_tokens": 5},
                    ):
                        pass
                    with function_span(
                        "get_weather",
                        input='{"city":"Tokyo"}',
                        output='{"condition":"sunny","temperature_c":22}',
                    ):
                        pass


def test_handoff_structure():
    with trace("openai-agents.handoff", metadata=_metadata("handoff")):
        with task_span("handoff agent run"):
            with agent_span("Triage", handoffs=["Spanish Assistant"]):
                with turn_span(1, "Triage"):
                    with generation_span(
                        input=[{"role": "user", "content": "Hola"}],
                        output=[
                            {
                                "type": "function_call",
                                "call_id": "call_handoff_1",
                                "name": "transfer_to_spanish_assistant",
                                "arguments": "{}",
                            }
                        ],
                        model="gpt-4o-mini",
                    ):
                        pass
                    with handoff_span("Triage", "Spanish Assistant"):
                        pass
            with agent_span("Spanish Assistant"):
                with turn_span(2, "Spanish Assistant"):
                    with generation_span(
                        input=[{"role": "user", "content": "Hola"}],
                        output=[{"role": "assistant", "content": "¡Hola!"}],
                        model="gpt-4o-mini",
                    ):
                        pass


def test_guardrail_and_provider_failure_structure():
    with trace("openai-agents.failure", metadata=_metadata("failure")):
        with task_span("failed agent run"):
            with agent_span("Guarded Agent"):
                with guardrail_span("safe_input", triggered=True):
                    pass
                with (
                    turn_span(1, "Guarded Agent"),
                    generation_span(
                        input=[{"role": "user", "content": "Trigger failure"}],
                        model="gpt-4o-mini",
                    ) as failed,
                ):
                    failed.set_error(
                        SpanError(
                            message="Provider temporarily unavailable",
                            data={"status_code": 503},
                        )
                    )


def test_streaming_structure():
    with trace("openai-agents.stream", metadata=_metadata("stream")):
        with task_span("streaming agent run"):
            with agent_span("Streaming Agent"):
                with turn_span(1, "Streaming Agent"):
                    with generation_span(
                        input=[{"role": "user", "content": "Stream a greeting."}],
                        output=[
                            {"role": "assistant", "content": "Hello from a stream!"}
                        ],
                        model="gpt-4o-mini",
                        model_config={"stream": True},
                        usage={
                            "input_tokens": 5,
                            "output_tokens": 5,
                            "total_tokens": 10,
                        },
                    ):
                        pass
