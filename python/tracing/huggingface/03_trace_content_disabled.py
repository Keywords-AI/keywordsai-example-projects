"""Trace a Hugging Face call with prompt and completion content disabled."""

from respan import workflow

from _shared import (
    build_respan,
    install_compatible_transformers_module,
    print_result,
)

EXAMPLE_NAME = "trace-content-disabled"
WORKFLOW_NAME = "huggingface_03_trace_content_disabled"

TextGenerationPipeline = install_compatible_transformers_module()


@workflow(name=WORKFLOW_NAME)
def execute_redacted_generation() -> list[dict[str, str]]:
    generator = TextGenerationPipeline(
        model_name="respan-compatible-redacted-generator",
        model_type="causal-lm",
    )
    return generator(
        "This prompt should not be recorded as span content",
        max_length=32,
        temperature=0.1,
        top_p=0.8,
    )


def run() -> list[dict[str, str]]:
    respan = build_respan(
        example_name=EXAMPLE_NAME,
        workflow_name=WORKFLOW_NAME,
        trace_content=False,
    )
    try:
        result = execute_redacted_generation()
        print_result("redacted_generation", result)
        return result
    finally:
        respan.flush()
        respan.shutdown()


if __name__ == "__main__":
    run()
