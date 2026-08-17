"""Hello-world quickstart for Respan LangChain instrumentation.

Run:
    RESPAN_API_KEY=your_respan_api_key python 00_quickstart.py

The example uses a fake LangChain chat model, so it does not need an OpenAI key.
When RESPAN_API_KEY is set, the LangChain run is exported to Respan.
"""

from __future__ import annotations

from _shared import init_telemetry, tracing_config
from langchain_core.language_models.fake_chat_models import FakeListChatModel
from langchain_core.messages import HumanMessage, SystemMessage


def langchain_instrumentation_quickstart() -> None:
    init_telemetry("langchain-quickstart")

    model = FakeListChatModel(responses=["Hello from a traced LangChain run."])
    response = model.invoke(
        [
            SystemMessage(content="Reply in one short sentence."),
            HumanMessage(content="Say hello to Respan tracing."),
        ],
        config=tracing_config("hello_world"),
    )
    print(response.content)


if __name__ == "__main__":
    langchain_instrumentation_quickstart()
