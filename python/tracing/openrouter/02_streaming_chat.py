"""OpenRouter streaming chat completion."""

from _shared import make_client, make_respan
from respan import workflow

respan = make_respan()
client, model = make_client()


@workflow(name="openrouter_streaming_chat")
def run() -> str:
    chunks: list[str] = []
    stream = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": "Write a four-line haiku about trace data.",
            }
        ],
        stream=True,
    )
    for chunk in stream:
        content = chunk.choices[0].delta.content
        if content:
            chunks.append(content)
            print(content, end="", flush=True)
    print()
    return "".join(chunks)


try:
    run()
finally:
    respan.flush()
    respan.shutdown()
