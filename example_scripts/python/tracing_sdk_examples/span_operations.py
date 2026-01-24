#!/usr/bin/env python3
"""
Span Operations - KeywordsAI Tracing SDK
Demonstrates: updating cost, pricing, token usage, metadata, and TTFT
"""
import os
import asyncio
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).parent / ".env"
load_dotenv(env_path, override=True)

from keywordsai_tracing import KeywordsAITelemetry, get_client
from keywordsai_tracing.decorators import workflow, task
from keywordsai_tracing.instruments import Instruments
from opentelemetry.semconv_ai import SpanAttributes

keywords_ai = KeywordsAITelemetry(
    app_name="span-operations",
    api_key=os.getenv("KEYWORDSAI_API_KEY"),
    is_batching_enabled=False,
    block_instruments={Instruments.REQUESTS, Instruments.URLLIB3},
)


def _calculate_cost(
    prompt_tokens: int,
    completion_tokens: int,
    prompt_unit_price: float,
    completion_unit_price: float,
) -> float:
    return (prompt_tokens * prompt_unit_price) + (completion_tokens * completion_unit_price)


@task(name="update_cost_and_pricing")
def update_cost_and_pricing() -> dict:
    """Update cost and unit prices on the current span."""
    client = get_client()
    if not client:
        return {}

    prompt_tokens = 120
    completion_tokens = 80
    prompt_unit_price = 0.0000025
    completion_unit_price = 0.000010
    cost = _calculate_cost(prompt_tokens, completion_tokens, prompt_unit_price, completion_unit_price)

    client.update_current_span(
        keywordsai_params={
            "model": "gpt-4o-mini",
            "prompt_unit_price": prompt_unit_price,
            "completion_unit_price": completion_unit_price,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "cost": cost,
        },
        attributes={
            SpanAttributes.LLM_USAGE_PROMPT_TOKENS: prompt_tokens,
            SpanAttributes.LLM_USAGE_COMPLETION_TOKENS: completion_tokens,
            SpanAttributes.LLM_USAGE_TOTAL_TOKENS: prompt_tokens + completion_tokens,
        },
    )

    updated_prompt_unit_price = 0.0000030
    updated_completion_unit_price = 0.000012
    updated_cost = _calculate_cost(
        prompt_tokens,
        completion_tokens,
        updated_prompt_unit_price,
        updated_completion_unit_price,
    )
    client.update_current_span(
        keywordsai_params={
            "prompt_unit_price": updated_prompt_unit_price,
            "completion_unit_price": updated_completion_unit_price,
            "cost": updated_cost,
        }
    )

    return {
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "prompt_unit_price": updated_prompt_unit_price,
        "completion_unit_price": updated_completion_unit_price,
        "cost": updated_cost,
    }


@task(name="update_token_usage")
def update_token_usage() -> dict:
    """Change input (prompt) and output (completion) token counts."""
    client = get_client()
    if not client:
        return {}

    prompt_tokens = 64
    completion_tokens = 28
    client.update_current_span(
        keywordsai_params={
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
        },
        attributes={
            SpanAttributes.LLM_USAGE_PROMPT_TOKENS: prompt_tokens,
            SpanAttributes.LLM_USAGE_COMPLETION_TOKENS: completion_tokens,
            SpanAttributes.LLM_USAGE_TOTAL_TOKENS: prompt_tokens + completion_tokens,
        },
    )

    completion_tokens += 12
    client.update_current_span(
        keywordsai_params={
            "completion_tokens": completion_tokens,
        },
        attributes={
            SpanAttributes.LLM_USAGE_COMPLETION_TOKENS: completion_tokens,
            SpanAttributes.LLM_USAGE_TOTAL_TOKENS: prompt_tokens + completion_tokens,
        },
    )

    return {
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
    }


@task(name="update_metadata")
def update_metadata() -> dict:
    """Update a custom metadata property on the span."""
    client = get_client()
    if not client:
        return {}

    metadata = {
        "custom_property": "priority:high",
        "source": "span_operations",
    }
    client.update_current_span(keywordsai_params={"metadata": metadata})
    return metadata


@task(name="update_ttft")
def update_ttft() -> dict:
    """Update time to first token (TTFT) on the span."""
    client = get_client()
    if not client:
        return {}

    estimated_ttft = 0.35
    client.update_current_span(keywordsai_params={"time_to_first_token": estimated_ttft})

    measured_ttft = 0.42
    client.update_current_span(keywordsai_params={"time_to_first_token": measured_ttft})
    return {"time_to_first_token": measured_ttft}


@workflow(name="span_operations_updates")
async def span_operations_updates() -> dict:
    print("\n[1] Cost and pricing updates")
    cost_info = update_cost_and_pricing()
    print(f"  Updated cost: {cost_info.get('cost')}")

    print("\n[2] Input/output token updates")
    token_info = update_token_usage()
    print(
        f"  Tokens: {token_info.get('prompt_tokens')} prompt, "
        f"{token_info.get('completion_tokens')} completion"
    )

    print("\n[3] Metadata update")
    metadata = update_metadata()
    print(f"  Metadata: {metadata.get('custom_property')}")

    print("\n[4] TTFT update")
    ttft = update_ttft()
    print(f"  TTFT: {ttft.get('time_to_first_token')}s")

    return {
        "cost": cost_info,
        "tokens": token_info,
        "metadata": metadata,
        "ttft": ttft,
    }


async def main():
    print("=" * 50)
    print("Span Operations Updates Demo")
    print("=" * 50)

    try:
        await span_operations_updates()
    finally:
        keywords_ai.flush()
        await asyncio.sleep(1)

    print("Done.")


if __name__ == "__main__":
    asyncio.run(main())
