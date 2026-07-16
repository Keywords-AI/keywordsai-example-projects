from __future__ import annotations

from pydantic import BaseModel
from respan import workflow

from _shared import (
    example_attributes,
    finish_respan,
    make_client,
    make_custom_identifier,
    make_respan,
    model_name,
    print_result,
    print_start,
    workflow_name,
)

EXAMPLE_NAME = "structured-parse"


class TraceSummary(BaseModel):
    summary: str
    sentiment: str


@workflow(name=workflow_name(EXAMPLE_NAME))
def _structured_parse_workflow(client) -> dict[str, str]:
    response = client.chat.parse(
        model=model_name(),
        messages=[{"role": "user", "content": "Summarize Writer tracing as JSON."}],
        response_format=TraceSummary,
        max_tokens=120,
        temperature=0,
    )
    parsed = response.choices[0].message.parsed
    return parsed.model_dump(mode="json") if parsed else {}


def run() -> dict[str, str]:
    respan = make_respan(EXAMPLE_NAME)
    client = make_client()
    custom_identifier = make_custom_identifier(EXAMPLE_NAME)
    result: dict[str, str] = {}
    try:
        with example_attributes(EXAMPLE_NAME, custom_identifier):
            print_start(EXAMPLE_NAME, custom_identifier)
            result = _structured_parse_workflow(client)
    finally:
        finish_respan(respan)
    print_result("structured parse", result)
    return result


if __name__ == "__main__":
    run()
