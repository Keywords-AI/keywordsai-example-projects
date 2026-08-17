"""Deterministic OpenRouter-compatible 429 failure coverage."""

from __future__ import annotations

from _shared import close_sync, make_mock_client, make_respan
from openai import RateLimitError
from respan import workflow


def main() -> None:
    respan = None
    client = None
    try:
        respan = make_respan(scenario="expected_429")
        client, model = make_mock_client()

        @workflow(name="openrouter_expected_429")
        def run(trigger_prompt: str) -> str:
            try:
                client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": trigger_prompt}],
                )
            except RateLimitError as exc:
                if exc.status_code != 429:
                    raise AssertionError(
                        f"expected HTTP 429, received {exc.status_code}"
                    ) from exc
                return "Observed expected deterministic OpenRouter 429"
            raise AssertionError(
                "expected the deterministic OpenRouter request to fail"
            )

        print(run("trigger deterministic 429"))
    finally:
        close_sync(respan=respan, client=client)


if __name__ == "__main__":
    main()
