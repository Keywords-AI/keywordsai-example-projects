"""Exercise current Langfuse SDK spans through the linked Respan instrumentor."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parents[3]
load_dotenv(ROOT_DIR / ".env", override=True)

os.environ.setdefault("LANGFUSE_PUBLIC_KEY", "pk-lf-respan-example")
os.environ.setdefault("LANGFUSE_SECRET_KEY", "sk-lf-respan-example")
os.environ.setdefault("LANGFUSE_BASE_URL", "https://cloud.langfuse.com")

from langfuse import get_client, observe
from respan import Respan
from respan_instrumentation_langfuse import LangfuseInstrumentor

RUN_ID = os.getenv("RESPAN_EXAMPLE_RUN_ID", "").strip() or "langfuse-local"
MODEL = os.getenv("RESPAN_LANGFUSE_MODEL", "gpt-4o-mini")
EXPECTED_SPANS = 6


def _mark_trace(workflow_name: str, input_value: object) -> None:
    get_client().update_current_trace(
        name=workflow_name,
        user_id="langfuse-example-user",
        session_id=f"{RUN_ID}:session",
        input=input_value,
        metadata={
            "example": "langfuse",
            "example_run_id": RUN_ID,
            "workflow_name": workflow_name,
        },
    )


@observe(as_type="generation", name="answer-question")
def answer_question(question: str) -> str:
    answer = f"A concise answer about: {question}"
    get_client().update_current_generation(
        input=[{"role": "user", "content": question}],
        output=[{"role": "assistant", "content": answer}],
        model=MODEL,
        usage_details={
            "prompt_tokens": 9,
            "completion_tokens": 7,
            "total_tokens": 16,
        },
        metadata={"example_run_id": RUN_ID},
    )
    return answer


@observe(as_type="tool", name="search-source")
def search_source(source: str, query: str) -> dict[str, str]:
    result = {"source": source, "result": f"{source} evidence for {query}"}
    get_client().update_current_span(
        output=result,
        metadata={"example_run_id": RUN_ID},
    )
    return result


@observe(name="langfuse_simple.workflow")
def simple_workflow() -> str:
    _mark_trace("langfuse_simple.workflow", {"question": "What is tracing?"})
    return answer_question("What is tracing?")


@observe(name="langfuse_research.workflow")
def research_workflow() -> str:
    query = "OpenTelemetry"
    _mark_trace("langfuse_research.workflow", {"query": query})
    evidence = [
        search_source("docs", query),
        search_source("examples", query),
    ]
    return answer_question(
        f"Summarize {query} using {', '.join(item['source'] for item in evidence)}"
    )


def main() -> None:
    api_key = os.environ["RESPAN_API_KEY"]
    respan = Respan(
        api_key=api_key,
        base_url=os.getenv("RESPAN_BASE_URL", "https://api.respan.ai/api"),
        app_name="langfuse-current-sdk",
        instrumentations=[],
        is_batching_enabled=False,
    )
    instrumentor = LangfuseInstrumentor()
    instrumentor.instrument()
    client = get_client()

    try:
        print(simple_workflow())
        print(research_workflow())
        client.flush()
        respan.flush()
        if instrumentor.exported_span_count != EXPECTED_SPANS:
            raise RuntimeError(
                "Langfuse exported "
                f"{instrumentor.exported_span_count} spans; expected {EXPECTED_SPANS}"
            )
        print(f"Langfuse exported {EXPECTED_SPANS} canonical spans.")
    finally:
        client.flush()
        instrumentor.uninstrument()
        respan.shutdown()


if __name__ == "__main__":
    main()
