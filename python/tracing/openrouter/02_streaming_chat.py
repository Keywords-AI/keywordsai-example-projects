"""OpenRouter streaming chat completion."""

from _shared import close_sync, make_client, make_respan
from respan import workflow


def main() -> None:
    respan = None
    client = None
    try:
        respan = make_respan(scenario="sync_stream")
        client, model = make_client()

        @workflow(name="openrouter_streaming_chat")
        def run(prompt: str) -> str:
            chunks: list[str] = []
            stream = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                stream=True,
                stream_options={"include_usage": True},
            )
            with stream:
                for chunk in stream:
                    if not chunk.choices:
                        continue
                    content = chunk.choices[0].delta.content
                    if content:
                        chunks.append(content)
                        print(content, end="", flush=True)
            print()
            return "".join(chunks)

        run("Write a four-line haiku about trace data.")
    finally:
        close_sync(respan=respan, client=client)


if __name__ == "__main__":
    main()
