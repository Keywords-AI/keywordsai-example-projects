#!/usr/bin/env python3
import os
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
from keywordsai_tracing import KeywordsAITelemetry
from keywordsai_tracing.decorators import workflow, task
from keywordsai_tracing.instruments import Instruments

load_dotenv(Path(__file__).with_name(".env"), override=True)

BASE_URL = os.getenv("KEYWORDSAI_BASE_URL", "https://api.keywordsai.co/api")
MODEL = os.getenv("BASIC_USAGE_CHAT_MODEL", "gpt-4o-mini")

telemetry = KeywordsAITelemetry(
    app_name="basic-usage",
    api_key=os.getenv("KEYWORDSAI_API_KEY"),
    is_batching_enabled=False,
    block_instruments={Instruments.REQUESTS, Instruments.URLLIB3, Instruments.ANTHROPIC},
)
client = OpenAI(api_key=os.getenv("KEYWORDSAI_API_KEY"), base_url=BASE_URL)


@task(name="child_task")
def child_task():
    client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": "Say hello briefly."}],
        max_tokens=20,
        temperature=0.0,
    )


@workflow(name="parent_trace")
async def parent_trace():
    child_task()


async def main():
    try:
        await parent_trace()
    finally:
        telemetry.flush()
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
