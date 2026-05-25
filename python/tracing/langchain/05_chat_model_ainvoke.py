"""Chat model ainvoke."""

import asyncio

from langchain_core.language_models.fake_chat_models import FakeChatModel

from _shared import flush, init_telemetry, message_text, tracing_config


async def chat_model_ainvoke() -> None:
    telemetry = init_telemetry("langchain-chat-model-ainvoke")
    model = FakeChatModel()
    try:
        response = await model.ainvoke(
            "Return a short async greeting.",
            config=tracing_config("chat_model_ainvoke"),
        )
        print(message_text(response))
    finally:
        flush(telemetry)


if __name__ == "__main__":
    asyncio.run(chat_model_ainvoke())
