"""Live WatsonxAIClient chat call traced by Respan."""

from pathlib import Path

from ibm_watsonx_orchestrate.client.autodiscover.watsonx_ai.watsonx_ai_client import (
    WatsonxAIClient,
)
from respan import workflow

from _shared import create_respan, optional_env

SCRIPT_NAME = Path(__file__).name
APP_NAME = SCRIPT_NAME.removesuffix(".py")


@workflow(name=SCRIPT_NAME)
def run_live_watsonx_chat() -> dict:
    client = WatsonxAIClient(
        model=optional_env("WATSON_ORCHESTRATE_LLM_MODEL"),
    )
    response = client.generate_response(
        input=optional_env("WATSON_ORCHESTRATE_LLM_PROMPT")
        or "Return one sentence explaining why tracing agent runs is useful.",
        instructions="Answer in one concise sentence.",
    )
    print(response)
    return response


def main() -> None:
    respan = create_respan(APP_NAME)
    try:
        run_live_watsonx_chat()
    finally:
        respan.flush()
        respan.shutdown()


if __name__ == "__main__":
    main()
