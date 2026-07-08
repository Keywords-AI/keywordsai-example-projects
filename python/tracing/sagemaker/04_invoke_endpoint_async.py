from __future__ import annotations

from respan import workflow

from _shared import (
    custom_attributes,
    endpoint_name,
    example_attributes,
    make_client,
    make_custom_identifier,
    make_respan,
    print_result,
    print_run_header,
    stubbed_response,
    workflow_name,
)

EXAMPLE_NAME = "invoke-endpoint-async"


@workflow(name=workflow_name(EXAMPLE_NAME))
def _invoke_async_workflow(client) -> dict:
    params = {
        "EndpointName": endpoint_name(),
        "InputLocation": "s3://respan-sagemaker-example/input.json",
        "ContentType": "application/json",
        "Accept": "application/json",
        "CustomAttributes": custom_attributes(),
    }
    response = {
        "InferenceId": "respan-example-inference",
        "OutputLocation": "s3://respan-sagemaker-example/output.json",
    }

    with stubbed_response(client, "invoke_endpoint_async", response, params):
        result = client.invoke_endpoint_async(**params)
        return {
            "inference_id": result.get("InferenceId"),
            "output_location": result.get("OutputLocation"),
        }


def run_invoke_endpoint_async() -> None:
    respan = make_respan(EXAMPLE_NAME)
    client = make_client()
    custom_identifier = make_custom_identifier(EXAMPLE_NAME)
    result: dict = {}

    try:
        with example_attributes(EXAMPLE_NAME, custom_identifier):
            print_run_header(EXAMPLE_NAME, custom_identifier)
            result = _invoke_async_workflow(client)
    finally:
        respan.flush()
        respan.shutdown()

    print_result(EXAMPLE_NAME, custom_identifier, result)


if __name__ == "__main__":
    run_invoke_endpoint_async()
