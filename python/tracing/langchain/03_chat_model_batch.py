"""Chat model batch."""

from langchain_core.language_models.fake_chat_models import FakeListChatModel

from _shared import flush, init_telemetry, message_text, tracing_config


def chat_model_batch() -> None:
    telemetry = init_telemetry("langchain-chat-model-batch")
    model = FakeListChatModel(responses=["alpha", "beta", "gamma"])
    try:
        responses = model.batch(
            ["Return alpha.", "Return beta.", "Return gamma."],
            config=tracing_config("chat_model_batch", {"batch_size": 3}),
        )
        print([message_text(response) for response in responses])
    finally:
        flush(telemetry)


if __name__ == "__main__":
    chat_model_batch()
