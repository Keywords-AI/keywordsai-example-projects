#!/usr/bin/env python3
"""
Multi-Processor - KeywordsAI Tracing SDK
Demonstrates: routing spans to multiple destinations with add_processor()
"""
import os
import json
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Sequence
from dotenv import load_dotenv

env_path = Path(__file__).parent / ".env"
load_dotenv(env_path, override=True)

from opentelemetry.sdk.trace import ReadableSpan
from opentelemetry.sdk.trace.export import SpanExporter, SpanExportResult
from keywordsai_tracing import KeywordsAITelemetry, get_client
from keywordsai_tracing.decorators import workflow, task
from keywordsai_tracing.instruments import Instruments


class FileExporter(SpanExporter):
    """Writes spans to a JSONL file."""
    def __init__(self, filepath: str, name: str = "file"):
        self.filepath = filepath
        self.name = name
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        open(filepath, "w").close()

    def export(self, spans: Sequence[ReadableSpan]) -> SpanExportResult:
        with open(self.filepath, "a") as f:
            for span in spans:
                data = {"name": span.name, "exporter": self.name, "time": datetime.now().isoformat()}
                f.write(json.dumps(data) + "\n")
        return SpanExportResult.SUCCESS

    def shutdown(self) -> None:
        pass

    def force_flush(self, timeout_millis: int = 30000) -> bool:
        return True


keywords_ai = KeywordsAITelemetry(
    app_name="multi-processor",
    api_key=os.getenv("KEYWORDSAI_API_KEY"),
    is_batching_enabled=False,
    block_instruments={Instruments.REQUESTS, Instruments.URLLIB3},
)

# Add custom processors
keywords_ai.add_processor(exporter=FileExporter("./output/debug-spans.jsonl", "debug"), name="debug")
keywords_ai.add_processor(exporter=FileExporter("./output/analytics-spans.jsonl", "analytics"), name="analytics")


@task(name="normal_task")
async def normal_task():
    """Goes to default KeywordsAI processor."""
    await asyncio.sleep(0.05)
    return "normal"


@task(name="debug_task", processors="debug")
async def debug_task():
    """Goes to debug processor only."""
    client = get_client()
    if client:
        client.add_event("debug.checkpoint")
    await asyncio.sleep(0.05)
    return "debug"


@task(name="analytics_task", processors="analytics")
async def analytics_task():
    """Goes to analytics processor only."""
    await asyncio.sleep(0.05)
    return "analytics"


@task(name="multi_task", processors=["debug", "analytics"])
async def multi_task():
    """Goes to both debug and analytics processors."""
    await asyncio.sleep(0.05)
    return "multi"


@workflow(name="multi_processor_workflow")
async def run_demo():
    """Demonstrate processor routing."""
    results = {}
    results["normal"] = await normal_task()
    results["debug"] = await debug_task()
    results["analytics"] = await analytics_task()
    results["multi"] = await multi_task()
    return results


async def main():
    print("=" * 50)
    print("Multi-Processor Demo")
    print("=" * 50)
    print("Routing: default=KeywordsAI, debug=file, analytics=file\n")

    try:
        results = await run_demo()
        for k, v in results.items():
            print(f"  {k}: {v}")
    finally:
        keywords_ai.flush()
        await asyncio.sleep(1)

    print("\nOutput files:")
    print("  ./output/debug-spans.jsonl")
    print("  ./output/analytics-spans.jsonl")
    print("Done.")


if __name__ == "__main__":
    asyncio.run(main())
