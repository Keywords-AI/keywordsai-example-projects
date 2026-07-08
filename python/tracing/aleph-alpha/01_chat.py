from __future__ import annotations

from aleph_alpha_client import ChatRequest, Message
from aleph_alpha_client.chat import Role
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

EXAMPLE_NAME = "chat"


@workflow(name=workflow_name(EXAMPLE_NAME))
def _chat_workflow(client) -> str:
    request = ChatRequest(
        model=model_name(),
        messages=[
            Message(role=Role.System, content="Answer concisely."),
            Message(role=Role.User, content="Explain why SDK tracing matters."),
        ],
        tools=[
            {
                "type": "function",
                "function": {
                    "name": "lookup_policy",
                    "description": "Look up a short policy note.",
                    "parameters": {
                        "type": "object",
                        "properties": {"topic": {"type": "string"}},
                        "required": ["topic"],
                    },
                },
            }
        ],
        tool_choice="auto",
    )
    response = client.chat(request=request, model=model_name())
    return response.message.content


def run_chat() -> None:
    respan = make_respan(EXAMPLE_NAME)
    custom_identifier = make_custom_identifier(EXAMPLE_NAME)
    text = ""
    mode = "unknown"
    try:
        with sync_client_context() as (client, mode):
            with example_attributes(EXAMPLE_NAME, custom_identifier):
                print(f"custom_identifier={custom_identifier}", flush=True)
                print(f"workflow_name={workflow_name(EXAMPLE_NAME)}", flush=True)
                text = _chat_workflow(client)
    finally:
        respan.flush()
        respan.shutdown()

    print_result(EXAMPLE_NAME, custom_identifier, mode, text)


if __name__ == "__main__":
    run_chat()
