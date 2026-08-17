"""Chat model astream."""

import asyncio

from _shared import init_telemetry, message_text, tracing_config
from langchain_core.language_models.fake_chat_models import FakeListChatModel


async def chat_model_astream() -> None:
    init_telemetry("langchain-chat-model-astream")
    model = FakeListChatModel(responses=["Asynchronous streaming chat output."])
    chunks = []
    async for chunk in model.astream(
        "Stream asynchronously.",
        config=tracing_config("chat_model_astream"),
    ):
        chunks.append(message_text(chunk))
    print("".join(chunks))


if __name__ == "__main__":
    asyncio.run(chat_model_astream())
