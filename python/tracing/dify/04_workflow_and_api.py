#!/usr/bin/env python3
"""Dify workflow, parameters, conversations, messages, and feedback tracing."""

from _shared import DifyExampleRuntime, print_result


def main() -> None:
    workflow_name = "dify_workflow_and_api.workflow"
    with DifyExampleRuntime(workflow_name) as runtime:
        raw_client = runtime.raw_client()
        chat_client = runtime.chat_client()
        user = runtime.user("api")

        workflow_response = raw_client._send_request(
            "POST",
            "/workflows/run",
            json={
                "inputs": {"query": "Summarize Dify tracing."},
                "response_mode": "blocking",
                "user": user,
            },
        )
        workflow_response.raise_for_status()

        parameters = chat_client.get_application_parameters(user=user)
        parameters.raise_for_status()
        conversations = chat_client.get_conversations(user=user)
        conversations.raise_for_status()
        messages = chat_client.get_conversation_messages(
            user=user,
            conversation_id="conv-local-001",
        )
        messages.raise_for_status()
        feedback = raw_client.message_feedback(
            message_id="msg-local-001",
            rating="like",
            user=user,
        )
        feedback.raise_for_status()
        rename = chat_client.rename_conversation(
            conversation_id="conv-local-001",
            name="Renamed local conversation",
            user=user,
        )
        rename.raise_for_status()

        print_result(
            "workflow_and_api",
            {
                "workflow": workflow_name,
                "workflow_run_id": workflow_response.json().get("workflow_run_id"),
                "parameters_keys": sorted(parameters.json().keys()),
                "conversations": len(conversations.json().get("data", [])),
                "messages": len(messages.json().get("data", [])),
                "feedback": feedback.json().get("result"),
                "rename": rename.json().get("result"),
            },
        )


if __name__ == "__main__":
    main()
