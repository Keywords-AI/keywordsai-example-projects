"""Chat model invoke."""

from langchain_core.language_models.fake_chat_models import FakeListChatModel
from langchain_core.messages import HumanMessage, SystemMessage

from _shared import flush, init_telemetry, message_text, tracing_config


def chat_model_invoke() -> None:
    telemetry = init_telemetry("langchain-chat-model-invoke")
    model = FakeListChatModel(responses=["Bonjour, Respan."])
    try:
        response = model.invoke(
            [
                SystemMessage(content="Translate English to French."),
                HumanMessage(content="Hello, Respan."),
            ],
            config=tracing_config("chat_model_invoke"),
        )
        print(message_text(response))
    finally:
        flush(telemetry)


if __name__ == "__main__":
    chat_model_invoke()
