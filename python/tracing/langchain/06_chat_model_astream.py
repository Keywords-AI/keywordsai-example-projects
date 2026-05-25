"""Chat model astream."""

import asyncio

from langchain_core.language_models.fake_chat_models import FakeChatModel

from _shared import flush, init_telemetry, message_text, tracing_config


async def chat_model_astream() -> None:
    telemetry = init_telemetry("langchain-chat-model-astream")
    model = FakeChatModel()
    try:
        chunks = []
        async for chunk in model.astream(
            "Stream asynchronously.",
            config=tracing_config("chat_model_astream"),
        ):
            chunks.append(message_text(chunk))
        print("".join(chunks))
    finally:
        flush(telemetry)


if __name__ == "__main__":
    asyncio.run(chat_model_astream())
