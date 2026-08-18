from __future__ import annotations

from _shared import (
    close_client,
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
from pydantic import BaseModel
from respan import workflow

EXAMPLE_NAME = "structured-parse"
_CLIENT = None


class TraceSummary(BaseModel):
    summary: str
    sentiment: str


@workflow(name=workflow_name(EXAMPLE_NAME))
def _structured_parse_workflow(prompt: str) -> dict[str, str]:
    response = _CLIENT.chat.parse(
        model=model_name(),
        messages=[{"role": "user", "content": prompt}],
        response_format=TraceSummary,
        max_tokens=120,
        temperature=0,
    )
    parsed = response.choices[0].message.parsed
    return parsed.model_dump(mode="json") if parsed else {}


def run() -> dict[str, str]:
    global _CLIENT
    respan = make_respan(EXAMPLE_NAME)
    client = make_client()
    _CLIENT = client
    custom_identifier = make_custom_identifier(EXAMPLE_NAME)
    result: dict[str, str] = {}
    try:
        with example_attributes(EXAMPLE_NAME, custom_identifier):
            print_start(EXAMPLE_NAME, custom_identifier)
            result = _structured_parse_workflow("Summarize Writer tracing as JSON.")
    finally:
        try:
            close_client(client)
        finally:
            finish_respan(respan)
    print_result("structured parse", result)
    return result


if __name__ == "__main__":
    run()
