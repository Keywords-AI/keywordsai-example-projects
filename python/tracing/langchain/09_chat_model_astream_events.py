"""Chat model astream_events."""

import asyncio

from langchain_core.language_models.fake_chat_models import FakeChatModel

from _shared import init_telemetry, tracing_config


async def chat_model_astream_events() -> None:
    telemetry = init_telemetry("langchain-chat-model-astream-events")
    model = FakeChatModel()
    events = []
    async for event in model.astream_events(
        "Emit semantic stream events.",
        config=tracing_config("chat_model_astream_events"),
        version="v2",
    ):
        events.append(event["event"])
    print(events)
if __name__ == "__main__":
    asyncio.run(chat_model_astream_events())
