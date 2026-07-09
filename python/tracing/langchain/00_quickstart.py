"""Hello-world quickstart for Respan LangChain instrumentation.

Run:
    RESPAN_API_KEY=your_respan_api_key python 00_quickstart.py

The example uses a fake LangChain chat model, so it does not need an OpenAI key.
When RESPAN_API_KEY is set, the LangChain run is exported to Respan.
"""

from __future__ import annotations

import os

from dotenv import find_dotenv, load_dotenv
from langchain_core.language_models.fake_chat_models import FakeListChatModel
from langchain_core.messages import HumanMessage, SystemMessage
from respan_instrumentation_langchain import add_respan_callback
from respan_tracing import RespanTelemetry

load_dotenv(find_dotenv(), override=False)


def langchain_instrumentation_quickstart() -> None:
    api_key = os.getenv("RESPAN_API_KEY")
    telemetry: RespanTelemetry | None = None

    if api_key:
        telemetry = RespanTelemetry(
            app_name="langchain-quickstart",
            api_key=api_key,
            base_url=os.getenv("RESPAN_BASE_URL", "https://api.respan.ai/api"),
            is_auto_instrument=False,
            is_batching_enabled=False,
            is_enabled=True,
        )
    else:
        print("RESPAN_API_KEY is not set; running locally without exporting spans.")

    model = FakeListChatModel(responses=["Hello from a traced LangChain run."])
    config = {
        "run_name": "hello_world",
        "tags": ["respan-langchain-example", "quickstart"],
        "metadata": {"example": "quickstart"},
    }
    if telemetry:
        config = add_respan_callback(config)

    response = model.invoke(
        [
            SystemMessage(content="Reply in one short sentence."),
            HumanMessage(content="Say hello to Respan tracing."),
        ],
        config=config,
    )
    print(response.content)


if __name__ == "__main__":
    langchain_instrumentation_quickstart()
