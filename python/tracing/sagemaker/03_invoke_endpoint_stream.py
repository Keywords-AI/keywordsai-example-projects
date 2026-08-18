from __future__ import annotations

import json

from _shared import (
    collect_stream_text,
    custom_attributes,
    endpoint_name,
    example_attributes,
    json_bytes,
    make_client,
    make_custom_identifier,
    make_respan,
    print_result,
    print_run_header,
    stubbed_response,
    workflow_name,
)
from respan import workflow

EXAMPLE_NAME = "invoke-endpoint-stream"


@workflow(name=workflow_name(EXAMPLE_NAME))
def _invoke_stream_workflow(prompt: str) -> dict:
    client = make_client()
    request_body = json_bytes({"inputs": prompt})
    params = {
        "EndpointName": endpoint_name(),
        "Body": request_body,
        "ContentType": "application/json",
        "Accept": "application/json",
        "CustomAttributes": custom_attributes(),
    }
    response = {
        "Body": {
            "PayloadPart": {
                "Bytes": json.dumps(
                    {
                        "token": {
                            "text": "Streaming SageMaker responses still become one traceable output."
                        },
                        "usage": {"input_tokens": 7, "generated_tokens": 9},
                    }
                ).encode("utf-8")
            }
        },
        "ContentType": "application/json",
    }

    try:
        with stubbed_response(
            client,
            "invoke_endpoint_with_response_stream",
            response,
            params,
        ):
            result = client.invoke_endpoint_with_response_stream(**params)
            return {"stream_text": collect_stream_text(result)}
    finally:
        client.close()


def run_invoke_endpoint_stream() -> None:
    respan = make_respan(EXAMPLE_NAME)
    custom_identifier = make_custom_identifier(EXAMPLE_NAME)
    result: dict = {}

    try:
        with example_attributes(EXAMPLE_NAME, custom_identifier):
            print_run_header(EXAMPLE_NAME, custom_identifier)
            result = _invoke_stream_workflow("Stream a concise SageMaker sentence.")
    finally:
        respan.shutdown()

    print_result(EXAMPLE_NAME, custom_identifier, result)


if __name__ == "__main__":
    run_invoke_endpoint_stream()
