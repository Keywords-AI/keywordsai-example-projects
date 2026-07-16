from __future__ import annotations

from aleph_alpha_client import CompletionRequest, Prompt
from _shared import (
    example_attributes,
    make_custom_identifier,
    make_respan,
    model_name,
    print_result,
    sync_client_context,
    workflow,
    workflow_name,
)

EXAMPLE_NAME = "completion"


@workflow(name=workflow_name(EXAMPLE_NAME))
def _completion_workflow(client) -> str:
    request = CompletionRequest(
        prompt=Prompt.from_text("Observability for LLM SDKs helps teams"),
        maximum_tokens=32,
        temperature=0.0,
        stop_sequences=["\n"],
    )
    response = client.complete(request=request, model=model_name())
    return response.completions[0].completion or ""


def run_completion() -> None:
    respan = make_respan(EXAMPLE_NAME)
    custom_identifier = make_custom_identifier(EXAMPLE_NAME)
    text = ""
    mode = "unknown"
    try:
        with sync_client_context() as (client, mode):
            with example_attributes(EXAMPLE_NAME, custom_identifier):
                print(f"custom_identifier={custom_identifier}", flush=True)
                print(f"workflow_name={workflow_name(EXAMPLE_NAME)}", flush=True)
                text = _completion_workflow(client)
    finally:
        respan.shutdown()

    print_result(EXAMPLE_NAME, custom_identifier, mode, text)


if __name__ == "__main__":
    run_completion()
