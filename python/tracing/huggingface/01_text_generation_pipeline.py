"""Trace a single Hugging Face TextGenerationPipeline call."""

from respan import workflow

from _shared import (
    build_respan,
    install_compatible_transformers_module,
    print_result,
)

EXAMPLE_NAME = "text-generation-pipeline"
WORKFLOW_NAME = "huggingface_01_text_generation_pipeline"

TextGenerationPipeline = install_compatible_transformers_module()


@workflow(name=WORKFLOW_NAME)
def execute_text_generation() -> list[dict[str, str]]:
    generator = TextGenerationPipeline(
        model_name="respan-compatible-tiny-generator",
        model_type="causal-lm",
    )
    return generator(
        "Tracing Hugging Face pipelines helps",
        max_length=42,
        temperature=0.35,
        top_p=0.9,
        repetition_penalty=1.1,
    )


def run() -> list[dict[str, str]]:
    respan = build_respan(example_name=EXAMPLE_NAME, workflow_name=WORKFLOW_NAME)
    try:
        result = execute_text_generation()
        print_result("text_generation", result)
        return result
    finally:
        respan.flush()
        respan.shutdown()


if __name__ == "__main__":
    run()
