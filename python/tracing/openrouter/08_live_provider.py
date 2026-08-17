"""Optional credential-gated OpenRouter provider response validation."""

from __future__ import annotations

import os

from _shared import close_sync, make_client, make_respan
from respan import workflow


def main() -> None:
    if not os.getenv("OPENROUTER_API_KEY"):
        print("SKIP: set OPENROUTER_API_KEY to run live OpenRouter validation")
        return

    respan = None
    client = None
    try:
        respan = make_respan(scenario="live_provider")
        client, model = make_client(live=True)

        @workflow(name="openrouter_live_provider")
        def run(prompt: str) -> str:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
            )
            if response.usage is None:
                raise AssertionError("live OpenRouter response did not include usage")
            return response.choices[0].message.content or ""

        print(run("Reply with exactly: live OpenRouter verified"))
    finally:
        close_sync(respan=respan, client=client)


if __name__ == "__main__":
    main()
