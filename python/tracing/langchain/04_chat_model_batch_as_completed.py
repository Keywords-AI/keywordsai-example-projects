"""Chat model batch_as_completed."""

from langchain_core.language_models.fake_chat_models import FakeListChatModel

from _shared import flush, init_telemetry, message_text, tracing_config


def chat_model_batch_as_completed() -> None:
    telemetry = init_telemetry("langchain-chat-model-batch-as-completed")
    model = FakeListChatModel(responses=["first", "second", "third"])
    try:
        completed = []
        for index, response in model.batch_as_completed(
            ["First", "Second", "Third"],
            config=tracing_config("chat_model_batch_as_completed"),
        ):
            completed.append((index, message_text(response)))
        print(completed)
    finally:
        flush(telemetry)


if __name__ == "__main__":
    chat_model_batch_as_completed()
