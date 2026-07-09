from __future__ import annotations

from _shared import model_name, prepare_vertexai_runtime

prepare_vertexai_runtime()

from respan import Respan, propagate_attributes, workflow  # noqa: E402
from respan_instrumentation_vertexai import VertexAIInstrumentor  # noqa: E402
from vertexai.generative_models import FunctionDeclaration, GenerativeModel, Tool  # noqa: E402


WORKFLOW_NAME = "vertexai_generate_content_example"


@workflow(name=WORKFLOW_NAME)
def run_example() -> str:
    weather_tool = Tool(
        function_declarations=[
            FunctionDeclaration(
                name="get_weather",
                description="Get a short weather summary for a city.",
                parameters={
                    "type": "object",
                    "properties": {"city": {"type": "string"}},
                    "required": ["city"],
                },
            )
        ]
    )
    model = GenerativeModel(
        model_name(),
        system_instruction="Answer with one concise sentence.",
        tools=[weather_tool],
    )
    with propagate_attributes(
        trace_group_identifier=WORKFLOW_NAME,
        metadata={"example": WORKFLOW_NAME},
    ):
        response = model.generate_content("Say hello from Vertex AI tracing.")
    print(response.text)
    return response.text


if __name__ == "__main__":
    respan = Respan(instrumentations=[VertexAIInstrumentor()])
    run_example()
