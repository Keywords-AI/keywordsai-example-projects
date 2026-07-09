from __future__ import annotations

from respan import workflow

from _shared import (
    custom_attributes,
    endpoint_name,
    example_attributes,
    json_bytes,
    make_client,
    make_custom_identifier,
    make_respan,
    print_result,
    print_run_header,
    read_json_body,
    streaming_body,
    stubbed_response,
    workflow_name,
)

EXAMPLE_NAME = "invoke-endpoint-text"


@workflow(name=workflow_name(EXAMPLE_NAME))
def _invoke_text_workflow(client) -> dict:
    request_body = json_bytes(
        {
            "inputs": "Reply with one concise sentence about SageMaker observability.",
            "parameters": {"max_new_tokens": 32, "temperature": 0.1},
        }
    )
    params = {
        "EndpointName": endpoint_name(),
        "Body": request_body,
        "ContentType": "application/json",
        "Accept": "application/json",
        "CustomAttributes": custom_attributes(),
    }
    response = {
        "Body": streaming_body(
            [
                {
                    "generated_text": "SageMaker observability links model calls to production traces.",
                    "details": {"input_tokens": 9, "generated_tokens": 10},
                }
            ]
        ),
        "ContentType": "application/json",
    }

    with stubbed_response(client, "invoke_endpoint", response, params):
        result = client.invoke_endpoint(**params)
        return {"response": read_json_body(result)}


def run_invoke_endpoint_text() -> None:
    respan = make_respan(EXAMPLE_NAME)
    client = make_client()
    custom_identifier = make_custom_identifier(EXAMPLE_NAME)
    result: dict = {}

    try:
        with example_attributes(EXAMPLE_NAME, custom_identifier):
            print_run_header(EXAMPLE_NAME, custom_identifier)
            result = _invoke_text_workflow(client)
    finally:
        respan.shutdown()

    print_result(EXAMPLE_NAME, custom_identifier, result)


if __name__ == "__main__":
    run_invoke_endpoint_text()
