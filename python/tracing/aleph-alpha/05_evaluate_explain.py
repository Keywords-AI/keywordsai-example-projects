from __future__ import annotations

from aleph_alpha_client import EvaluationRequest, ExplanationRequest, Prompt
from _shared import (
    example_attributes,
    make_custom_identifier,
    make_respan,
    model_name,
    print_result,
    sync_client_context,
    workflow,
    workflow_name,
)

EXAMPLE_NAME = "evaluate-explain"


@workflow(name=workflow_name(EXAMPLE_NAME))
def _evaluate_explain_workflow(client) -> str:
    evaluation = client.evaluate(
        request=EvaluationRequest(
            prompt=Prompt.from_text("The Respan trace export finished"),
            completion_expected=" successfully.",
        ),
        model=model_name(),
    )
    explanation = client.explain(
        request=ExplanationRequest(
            prompt=Prompt.from_text("Instrumentation captures prompts."),
            target=" Captures completions too.",
        ),
        model=model_name(),
    )
    return (
        f"evaluation_tokens={evaluation.num_tokens_prompt_total}; "
        f"explanations={len(explanation.explanations)}"
    )


def run_evaluate_explain() -> None:
    respan = make_respan(EXAMPLE_NAME)
    custom_identifier = make_custom_identifier(EXAMPLE_NAME)
    text = ""
    mode = "unknown"
    try:
        with sync_client_context() as (client, mode):
            with example_attributes(EXAMPLE_NAME, custom_identifier):
                print(f"custom_identifier={custom_identifier}", flush=True)
                print(f"workflow_name={workflow_name(EXAMPLE_NAME)}", flush=True)
                text = _evaluate_explain_workflow(client)
    finally:
        respan.shutdown()

    print_result(EXAMPLE_NAME, custom_identifier, mode, text)


if __name__ == "__main__":
    run_evaluate_explain()
