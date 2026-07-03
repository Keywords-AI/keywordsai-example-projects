from __future__ import annotations

from _shared import model_name, prepare_vertexai_runtime

prepare_vertexai_runtime()

from respan import Respan, propagate_attributes, workflow  # noqa: E402
from respan_instrumentation_vertexai import VertexAIInstrumentor  # noqa: E402
from vertexai.generative_models import GenerativeModel  # noqa: E402


WORKFLOW_NAME = "vertexai_chat_streaming_example"


@workflow(name=WORKFLOW_NAME)
def run_example() -> str:
    model = GenerativeModel(
        model_name(),
        system_instruction="Keep responses short and direct.",
    )
    chat = model.start_chat()
    with propagate_attributes(
        trace_group_identifier=WORKFLOW_NAME,
        metadata={"example": WORKFLOW_NAME},
    ):
        chunks = list(chat.send_message("Stream a short Vertex AI reply.", stream=True))
    text = "".join(chunk.text for chunk in chunks)
    print(text)
    return text


if __name__ == "__main__":
    respan = Respan(instrumentations=[VertexAIInstrumentor()])
    try:
        run_example()
    finally:
        respan.flush()
