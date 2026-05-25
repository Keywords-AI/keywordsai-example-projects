"""Attach user, thread, and metadata attributes to Guardrails spans."""

from guardrails import Guard
from respan import Respan, propagate_attributes, workflow
from respan_instrumentation_guardrails import GuardrailsInstrumentor

from _shared import load_guardrails_example_environment

WORKFLOW_NAME = "guardrails_propagated_attributes_workflow"


@workflow(name=WORKFLOW_NAME)
def propagated_attributes_workflow(guard: Guard):
    return guard.parse(
        llm_output="Guardrails keeps structured outputs reliable.",
        num_reasks=0,
    )


def run_propagated_attributes() -> None:
    respan_api_key, respan_base_url, _ = load_guardrails_example_environment()
    respan = Respan(
        api_key=respan_api_key,
        base_url=respan_base_url,
        app_name="guardrails-propagated-attributes",
        instrumentations=[GuardrailsInstrumentor()],
        is_auto_instrument=True,
    )

    guard = Guard()
    with propagate_attributes(
        customer_identifier="example-user-guardrails",
        thread_identifier="guardrails-thread-001",
        metadata={"example": "guardrails", "path": "local-parse"},
    ):
        result = propagated_attributes_workflow(guard=guard)

    print("Workflow name:", WORKFLOW_NAME)
    print("Validation passed:", result.validation_passed)
    print("Validated output:", result.validated_output)
    respan.flush()


if __name__ == "__main__":
    run_propagated_attributes()
