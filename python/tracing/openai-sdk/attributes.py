"""Customer, thread, and metadata propagation across OpenAI calls."""

from respan import propagate_attributes, workflow

from _shared import (
    example_attributes,
    finish_respan,
    make_respan,
    make_sync_client,
    model_name,
    print_result,
)

EXAMPLE = "attributes"
respan = make_respan(EXAMPLE)


@workflow(name="openai_handle_request")
def handle_request(user_id: str, question: str) -> str:
    with propagate_attributes(
        customer_identifier=user_id,
        thread_identifier="openai-conversation-001",
        metadata={"plan": "pro"},
    ):
        response = client.chat.completions.create(
            model=model_name(), messages=[{"role": "user", "content": question}]
        )
    return response.choices[0].message.content or ""


try:
    client = make_sync_client()
    try:
        with example_attributes(EXAMPLE):
            first = handle_request("user_alice", "What is an API gateway?")
            second = handle_request("user_bob", "Explain rate limiting.")
            print_result(EXAMPLE, f"first={first} second={second}")
    finally:
        client.close()
finally:
    finish_respan(respan)
