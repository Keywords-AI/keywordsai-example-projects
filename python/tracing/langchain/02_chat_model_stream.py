"""Chat model stream."""

from langchain_core.language_models.fake_chat_models import FakeListChatModel

from _shared import flush, init_telemetry, message_text, tracing_config


def chat_model_stream() -> None:
    telemetry = init_telemetry("langchain-chat-model-stream")
    model = FakeListChatModel(responses=["Streaming chat output."])
    try:
        chunks = [
            message_text(chunk)
            for chunk in model.stream(
                "Stream a short status update.",
                config=tracing_config("chat_model_stream"),
            )
        ]
        print("".join(chunks))
    finally:
        flush(telemetry)


if __name__ == "__main__":
    chat_model_stream()
