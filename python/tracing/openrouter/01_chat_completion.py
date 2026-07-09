"""OpenRouter chat completion through the OpenAI-compatible Python client."""

from _shared import make_client, make_respan
from respan import workflow

respan = make_respan()
client, model = make_client()


@workflow(name="openrouter_basic_chat")
def run() -> str:
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": "Say hello from OpenRouter in one concise sentence.",
            }
        ],
    )
    return response.choices[0].message.content or ""


try:
    print(run())
finally:
    respan.shutdown()
