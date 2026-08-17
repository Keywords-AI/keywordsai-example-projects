"""Three-turn Chat history with each provider call auto-traced."""

from respan import workflow

from _shared import (
    example_attributes,
    finish_respan,
    make_respan,
    make_sync_client,
    model_name,
    print_result,
)

EXAMPLE = "multi-turn"
respan = make_respan(EXAMPLE)


@workflow(name="openai_conversation")
def run() -> str:
    messages: list[dict[str, str]] = [
        {"role": "system", "content": "You are a concise cooking assistant."}
    ]
    for question in (
        "What can I make with eggs and cheese?",
        "How long does it take?",
        "How can I make it fluffy?",
    ):
        messages.append({"role": "user", "content": question})
        response = client.chat.completions.create(model=model_name(), messages=messages)
        answer = response.choices[0].message.content or ""
        messages.append({"role": "assistant", "content": answer})
    return messages[-1]["content"]


try:
    client = make_sync_client()
    try:
        with example_attributes(EXAMPLE):
            print_result(EXAMPLE, run())
    finally:
        client.close()
finally:
    finish_respan(respan)
