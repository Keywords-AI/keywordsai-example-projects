from __future__ import annotations

from _shared import (
    close_provider,
    example_attributes,
    generated_text,
    make_custom_identifier,
    make_model,
    make_respan,
    print_lookup,
    workflow_name,
)
from respan import workflow

EXAMPLE_NAME = "text-generation"
_MODEL = None


@workflow(name=workflow_name(EXAMPLE_NAME))
def _text_generation_workflow(generation_prompt: str, summary_prompt: str) -> str:
    raw_response = _MODEL.generate(
        prompt=generation_prompt,
        params={"max_new_tokens": 60},
    )
    text_response = _MODEL.generate_text(
        prompt=summary_prompt,
        params={"max_new_tokens": 20},
    )
    return f"generate={generated_text(raw_response)}\ngenerate_text={text_response}"


def run_text_generation() -> None:
    global _MODEL
    model = make_model()
    _MODEL = model
    respan = make_respan(EXAMPLE_NAME)
    custom_identifier = make_custom_identifier(EXAMPLE_NAME)
    output = ""

    try:
        with example_attributes(EXAMPLE_NAME, custom_identifier):
            output = _text_generation_workflow(
                "Explain why tracing IBM watsonx.ai calls is useful in one sentence.",
                "Write a six-word summary of LLM observability.",
            )
    finally:
        try:
            close_provider(model)
        finally:
            respan.shutdown()

    print_lookup(EXAMPLE_NAME, custom_identifier, output)


if __name__ == "__main__":
    run_text_generation()
