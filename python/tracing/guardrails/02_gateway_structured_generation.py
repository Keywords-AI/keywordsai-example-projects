"""Generate structured output through the Respan gateway and validate it."""

from typing import Literal

from guardrails import Guard
from pydantic import BaseModel, Field
from respan import Respan, workflow
from respan_instrumentation_guardrails import GuardrailsInstrumentor

from _shared import load_guardrails_example_environment

WORKFLOW_NAME = "guardrails_gateway_structured_generation_workflow"


class ProductRecommendation(BaseModel):
    product: str = Field(description="Recommended product name")
    reason: str = Field(description="One sentence explaining the recommendation")
    confidence: Literal["low", "medium", "high"] = Field(
        description="Confidence in the recommendation"
    )


@workflow(name=WORKFLOW_NAME)
def gateway_structured_generation_workflow(guard: Guard, model: str):
    return guard(
        model=model,
        messages=[
            {
                "role": "user",
                "content": (
                    "Recommend one durable backpack for a weekend hiking trip. "
                    "Return JSON with product, reason, and confidence."
                ),
            }
        ],
        num_reasks=1,
    )


def run_gateway_structured_generation() -> None:
    respan_api_key, respan_base_url, model = load_guardrails_example_environment()
    respan = Respan(
        api_key=respan_api_key,
        base_url=respan_base_url,
        app_name="guardrails-gateway-structured-generation",
        instrumentations=[GuardrailsInstrumentor()],
        is_auto_instrument=True,
    )

    guard = Guard.for_pydantic(output_class=ProductRecommendation)
    result = gateway_structured_generation_workflow(guard=guard, model=model)

    print("Workflow name:", WORKFLOW_NAME)
    print("Raw output:", result.raw_llm_output)
    print("Validation passed:", result.validation_passed)
    print("Validated output:", result.validated_output)


if __name__ == "__main__":
    run_gateway_structured_generation()
