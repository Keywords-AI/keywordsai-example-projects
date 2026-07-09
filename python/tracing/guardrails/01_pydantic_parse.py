"""Validate known LLM output against a Pydantic schema."""

from typing import Literal

from guardrails import Guard
from pydantic import BaseModel, Field
from respan import Respan, workflow
from respan_instrumentation_guardrails import GuardrailsInstrumentor

from _shared import load_guardrails_example_environment

WORKFLOW_NAME = "guardrails_pydantic_parse_workflow"


class SupportTicket(BaseModel):
    issue: str = Field(description="Short customer issue summary")
    urgency: Literal["low", "medium", "high"] = Field(description="Ticket urgency")


@workflow(name=WORKFLOW_NAME)
def pydantic_parse_workflow(guard: Guard):
    return guard.parse(
        llm_output='{"issue": "Shipment arrived late", "urgency": "high"}',
        num_reasks=0,
    )


def run_pydantic_parse() -> None:
    respan_api_key, respan_base_url, _ = load_guardrails_example_environment()
    respan = Respan(
        api_key=respan_api_key,
        base_url=respan_base_url,
        app_name="guardrails-pydantic-parse",
        instrumentations=[GuardrailsInstrumentor()],
        is_auto_instrument=True,
    )

    guard = Guard.for_pydantic(output_class=SupportTicket)
    result = pydantic_parse_workflow(guard=guard)

    print("Workflow name:", WORKFLOW_NAME)
    print("Validation passed:", result.validation_passed)
    print("Validated output:", result.validated_output)


if __name__ == "__main__":
    run_pydantic_parse()
