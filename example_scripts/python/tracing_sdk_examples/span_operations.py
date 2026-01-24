#!/usr/bin/env python3
import os
import asyncio
import time
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
from keywordsai_tracing import KeywordsAITelemetry, get_client
from keywordsai_tracing.decorators import workflow, task
from keywordsai_tracing.instruments import Instruments
from opentelemetry.semconv_ai import SpanAttributes, GenAISystem

load_dotenv(Path(__file__).with_name(".env"), override=True)

BASE_URL = os.getenv("KEYWORDSAI_BASE_URL", "https://api.keywordsai.co/api")
MODEL = os.getenv("SPAN_OPERATIONS_CHAT_MODEL", "gpt-4o-mini")
PROMPT = os.getenv("SPAN_OPERATIONS_CHAT_PROMPT", "Reply with exactly: Span updates verified.")
DELAY = float(os.getenv("SPAN_OPERATIONS_STEP_DELAY_SEC", "1.1"))

telemetry = KeywordsAITelemetry(
    app_name="span-operations",
    api_key=os.getenv("KEYWORDSAI_API_KEY"),
    is_batching_enabled=False,
    block_instruments={Instruments.REQUESTS, Instruments.URLLIB3, Instruments.ANTHROPIC},
)
client = OpenAI(api_key=os.getenv("KEYWORDSAI_API_KEY"), base_url=BASE_URL)


def _attrs(prompt_tokens, completion_tokens, **extra):
    total = prompt_tokens + completion_tokens
    attrs = {
        SpanAttributes.LLM_SYSTEM: GenAISystem.OPENAI.value,
        SpanAttributes.LLM_REQUEST_MODEL: MODEL,
        SpanAttributes.LLM_RESPONSE_MODEL: MODEL,
        SpanAttributes.LLM_USAGE_PROMPT_TOKENS: prompt_tokens,
        SpanAttributes.LLM_USAGE_COMPLETION_TOKENS: completion_tokens,
        SpanAttributes.LLM_USAGE_TOTAL_TOKENS: total,
        "model": MODEL,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_request_tokens": total,
    }
    attrs.update(extra)
    return attrs


@task(name="chat_before_updates")
def chat_before_updates():
    time.sleep(DELAY)
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": PROMPT}],
        temperature=0.0,
        max_tokens=40,
    )
    usage = resp.usage
    return (
        {"prompt_tokens": usage.prompt_tokens, "completion_tokens": usage.completion_tokens}
        if usage
        else {}
    )


@task(name="update_cost_and_pricing")
def update_cost_and_pricing(prompt_tokens, completion_tokens):
    c = get_client()
    if not c:
        return
    p1, c1 = 0.0000025, 0.000010
    cost1 = prompt_tokens * p1 + completion_tokens * c1
    c.update_current_span(
        attributes=_attrs(
            prompt_tokens,
            completion_tokens,
            cost=cost1,
            prompt_unit_price=p1,
            completion_unit_price=c1,
        )
    )
    time.sleep(DELAY)
    p2, c2 = 0.0000030, 0.000012
    cost2 = prompt_tokens * p2 + completion_tokens * c2
    c.update_current_span(
        attributes=_attrs(
            prompt_tokens,
            completion_tokens,
            cost=cost2,
            prompt_unit_price=p2,
            completion_unit_price=c2,
        )
    )


@task(name="update_token_usage")
def update_token_usage():
    c = get_client()
    if not c:
        return
    time.sleep(DELAY)
    p, comp = 64, 28
    c.update_current_span(attributes=_attrs(p, comp))
    time.sleep(DELAY)
    c.update_current_span(attributes=_attrs(p + 12, comp + 12))


@task(name="update_customer")
def update_customer():
    c = get_client()
    if not c:
        return
    c.update_current_span(
        keywordsai_params={
            "customer_email": "demo_user@keywordsai.co",
            "customer_name": "Demo User",
        }
    )


@task(name="update_ttft")
def update_ttft():
    c = get_client()
    if not c:
        return
    start = time.perf_counter()
    time.sleep(max(DELAY / 2, 0.1))
    t1 = round(time.perf_counter() - start, 2)
    c.update_current_span(
        keywordsai_params={"metadata": {"time_to_first_token": t1, "ttft": t1}}
    )
    time.sleep(max(DELAY / 2, 0.1))
    t2 = round(time.perf_counter() - start, 2)
    c.update_current_span(
        keywordsai_params={"metadata": {"time_to_first_token": t2, "ttft": t2}}
    )


@workflow(name="span_operations_updates")
async def span_operations_updates():
    usage = chat_before_updates()
    update_cost_and_pricing(usage.get("prompt_tokens", 120), usage.get("completion_tokens", 80))
    update_token_usage()
    update_customer()
    update_ttft()


async def main():
    try:
        await span_operations_updates()
    finally:
        telemetry.flush()
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())