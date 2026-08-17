from __future__ import annotations

import asyncio

from _shared import (
    chat_context,
    example_attributes,
    finish_respan,
    live_openai_settings,
    make_custom_identifier,
    make_respan,
    print_result,
    print_start,
)
from livekit.agents.types import APIConnectOptions
from livekit.plugins import openai as livekit_openai

LIVE_CALL_TIMEOUT_SECONDS = 20.0
LIVE_CLOSE_TIMEOUT_SECONDS = 5.0


async def main() -> None:
    example_name = "05-live-openai"
    client_mode = "live-openai-gateway"
    custom_identifier = make_custom_identifier(example_name)
    api_key, base_url, model_name = live_openai_settings()
    respan = make_respan(example_name, client_mode=client_mode)
    model: livekit_openai.LLM | None = None
    try:
        model = livekit_openai.LLM(
            model=model_name,
            api_key=api_key,
            base_url=base_url,
            temperature=0,
            max_completion_tokens=64,
            max_retries=0,
        )
        print_start(
            example_name,
            custom_identifier,
            client_mode=client_mode,
        )
        with example_attributes(
            example_name,
            custom_identifier,
            client_mode=client_mode,
        ):
            response = await asyncio.wait_for(
                model.chat(
                    chat_ctx=chat_context(
                        "Reply with one short sentence confirming LiveKit is connected."
                    ),
                    conn_options=APIConnectOptions(
                        max_retry=0,
                        retry_interval=0,
                        timeout=15,
                    ),
                ).collect(),
                timeout=LIVE_CALL_TIMEOUT_SECONDS,
            )
        print_result(
            "live_response",
            {
                "model": model_name,
                "text": response.text,
                "usage": response.usage,
            },
        )
    finally:
        try:
            if model is not None:
                await asyncio.wait_for(
                    model.aclose(),
                    timeout=LIVE_CLOSE_TIMEOUT_SECONDS,
                )
        finally:
            finish_respan(respan)


if __name__ == "__main__":
    asyncio.run(main())
