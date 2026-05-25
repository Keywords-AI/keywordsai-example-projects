"""Chat model abatch_as_completed."""

import asyncio

from langchain_core.language_models.fake_chat_models import FakeChatModel

from _shared import flush, init_telemetry, message_text, tracing_config


async def chat_model_abatch_as_completed() -> None:
    telemetry = init_telemetry("langchain-chat-model-abatch-as-completed")
    model = FakeChatModel()
    try:
        completed = []
        async for index, response in model.abatch_as_completed(
            ["Return north.", "Return south."],
            config=tracing_config("chat_model_abatch_as_completed"),
        ):
            completed.append((index, message_text(response)))
        print(completed)
    finally:
        flush(telemetry)


if __name__ == "__main__":
    asyncio.run(chat_model_abatch_as_completed())
