"""Runnable custom event."""

from typing import Any

from langchain_core.callbacks import dispatch_custom_event
from langchain_core.runnables import RunnableLambda

from _shared import init_telemetry, tracing_config


def custom_event() -> None:
    telemetry = init_telemetry("langchain-custom-event")

    def normalize(payload: dict[str, str], config: dict[str, Any] | None = None) -> dict[str, str]:
        dispatch_custom_event(
            "langchain.example.progress",
            {"stage": "normalize", "text": payload["text"]},
            config=config,
        )
        return {"text": payload["text"].upper()}

    runnable = RunnableLambda(normalize)
    response = runnable.invoke(
        {"text": "respan"},
        config=tracing_config("custom_event"),
    )
    print(response)
if __name__ == "__main__":
    custom_event()
