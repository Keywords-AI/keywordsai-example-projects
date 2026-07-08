from __future__ import annotations

from respan import workflow

from _shared import (
    example_attributes,
    generated_text,
    make_custom_identifier,
    make_model,
    make_respan,
    print_lookup,
    workflow_name,
)

EXAMPLE_NAME = "text-generation"


@workflow(name=workflow_name(EXAMPLE_NAME))
def _text_generation_workflow(model) -> str:
    raw_response = model.generate(
        prompt="Explain why tracing IBM watsonx.ai calls is useful in one sentence.",
        params={"max_new_tokens": 60},
    )
    text_response = model.generate_text(
        prompt="Write a six-word summary of LLM observability.",
        params={"max_new_tokens": 20},
    )
    return f"generate={generated_text(raw_response)}\ngenerate_text={text_response}"


def run_text_generation() -> None:
    model = make_model()
    respan = make_respan(EXAMPLE_NAME)
    custom_identifier = make_custom_identifier(EXAMPLE_NAME)
    output = ""

    try:
        with example_attributes(EXAMPLE_NAME, custom_identifier):
            output = _text_generation_workflow(model)
    finally:
        respan.flush()
        respan.shutdown()

    print_lookup(EXAMPLE_NAME, custom_identifier, output)


if __name__ == "__main__":
    run_text_generation()
