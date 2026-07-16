#!/usr/bin/env python3
"""Dify text completion message traced by Respan."""

from _shared import DifyExampleRuntime, print_result


def main() -> None:
    workflow_name = "dify_completion.workflow"
    with DifyExampleRuntime(workflow_name) as runtime:
        client = runtime.completion_client()
        response = client.create_completion_message(
            inputs={"query": "Translate tracing to French."},
            response_mode="blocking",
            user=runtime.user("completion"),
        )
        response.raise_for_status()
        result = response.json()
        print_result("completion", {"workflow": workflow_name, "answer": result.get("answer")})


if __name__ == "__main__":
    main()
