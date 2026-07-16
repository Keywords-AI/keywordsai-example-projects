"""Trace a batched Hugging Face TextGenerationPipeline call."""

from respan import workflow

from _shared import (
    build_respan,
    install_compatible_transformers_module,
    print_result,
)

EXAMPLE_NAME = "batch-prompts"
WORKFLOW_NAME = "huggingface_02_batch_prompts"

TextGenerationPipeline = install_compatible_transformers_module()


@workflow(name=WORKFLOW_NAME)
def execute_batch_generation() -> list[dict[str, str]]:
    generator = TextGenerationPipeline(
        model_name="respan-compatible-batch-generator",
        model_type="causal-lm",
        temperature=0.2,
        top_p=0.85,
        max_length=56,
    )
    return generator(
        [
            "Batch prompt one:",
            "Batch prompt two:",
        ],
        max_length=56,
        temperature=0.2,
        top_p=0.85,
    )


def run() -> list[dict[str, str]]:
    respan = build_respan(example_name=EXAMPLE_NAME, workflow_name=WORKFLOW_NAME)
    try:
        result = execute_batch_generation()
        print_result("batch_generation", result)
        return result
    finally:
        respan.shutdown()


if __name__ == "__main__":
    run()
