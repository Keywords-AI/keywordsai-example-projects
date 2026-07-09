import litellm
from respan import workflow

from _shared import (
    GATEWAY_API_KEY,
    GATEWAY_BASE_URL,
    MODEL,
    create_respan,
    run_with_example_attributes,
)

WORKFLOW_NAME = "litellm_basic_completion.workflow"


@workflow(name=WORKFLOW_NAME)
def litellm_basic_completion() -> str:
    response = litellm.completion(
        api_key=GATEWAY_API_KEY,
        api_base=GATEWAY_BASE_URL,
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": "In one sentence, explain what LiteLLM helps developers do.",
            }
        ],
        temperature=0.1,
        max_tokens=80,
    )
    return response.choices[0].message.content


def main() -> None:
    respan = create_respan("litellm-basic-completion")
    output = run_with_example_attributes(
        respan,
        workflow_name=WORKFLOW_NAME,
        action=litellm_basic_completion,
    )
    print(output)
if __name__ == "__main__":
    main()
