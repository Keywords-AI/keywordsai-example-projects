"""OpenRouter chat completion through the OpenAI-compatible Python client."""

from _shared import close_sync, make_client, make_respan
from respan import workflow


def main() -> None:
    respan = None
    client = None
    try:
        respan = make_respan(scenario="basic_chat")
        client, model = make_client()

        @workflow(name="openrouter_basic_chat")
        def run(prompt: str) -> str:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.choices[0].message.content or ""

        print(run("Say hello from OpenRouter in one concise sentence."))
    finally:
        close_sync(respan=respan, client=client)


if __name__ == "__main__":
    main()
