"""Live Watson Orchestrate ADK run-client call traced by Respan."""

from pathlib import Path

from ibm_watsonx_orchestrate.client.chat.run_client import RunClient
from respan import workflow

from _shared import create_respan, optional_env, require_env

SCRIPT_NAME = Path(__file__).name
APP_NAME = SCRIPT_NAME.removesuffix(".py")


@workflow(name=SCRIPT_NAME)
def run_live_agent() -> dict:
    client = RunClient(
        base_url=require_env("WATSON_ORCHESTRATE_BASE_URL"),
        api_key=require_env("WATSON_ORCHESTRATE_API_KEY"),
        is_local=optional_env("WATSON_ORCHESTRATE_IS_LOCAL") == "true",
        verify=optional_env("WATSON_ORCHESTRATE_VERIFY_SSL"),
    )
    response = client.create_run(
        message=optional_env("WATSON_ORCHESTRATE_MESSAGE")
        or "Reply with one concise sentence from a traced Respan example.",
        agent_id=require_env("WATSON_ORCHESTRATE_AGENT_ID"),
        thread_id=optional_env("WATSON_ORCHESTRATE_THREAD_ID"),
        capture_logs=True,
    )
    print(response)
    return response


def main() -> None:
    respan = create_respan(APP_NAME)
    try:
        run_live_agent()
    finally:
        respan.flush()
        respan.shutdown()


if __name__ == "__main__":
    main()
