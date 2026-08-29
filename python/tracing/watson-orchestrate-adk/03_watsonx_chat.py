from __future__ import annotations

from _shared import (
    create_respan,
    deterministic_chat_client,
    deterministic_watson_runtime,
    example_attributes,
    marker_for,
    workflow_name,
)
from respan import workflow

EXAMPLE_NAME = "watsonx-chat"


@workflow(name=workflow_name(EXAMPLE_NAME))
def watsonx_chat(prompt: str) -> dict:
    return deterministic_chat_client().generate_response(
        input=prompt,
        instructions="Answer in one concise sentence.",
    )


def main() -> None:
    marker = marker_for(EXAMPLE_NAME)
    with deterministic_watson_runtime():
        respan = create_respan(EXAMPLE_NAME, marker)
        try:
            with example_attributes(EXAMPLE_NAME, marker):
                result = watsonx_chat("Explain why tracing agent runs is useful.")
        finally:
            respan.shutdown()
    print({"example": EXAMPLE_NAME, "marker": marker, "result": result}, flush=True)


if __name__ == "__main__":
    main()
