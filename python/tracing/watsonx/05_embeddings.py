from __future__ import annotations

import asyncio

from _shared import (
    close_provider,
    example_attributes,
    make_custom_identifier,
    make_embeddings,
    make_respan,
    print_lookup,
    workflow_name,
)
from respan import workflow

EXAMPLE_NAME = "embeddings"
_EMBEDDINGS = None


def _shape(value) -> str:
    if isinstance(value, dict):
        results = value.get("results", [])
        return f"dict_results={len(results)}"
    if not isinstance(value, list):
        return type(value).__name__
    if value and isinstance(value[0], list):
        return f"vectors={len(value)}x{len(value[0])}"
    return f"vector={len(value)}"


@workflow(name=workflow_name(EXAMPLE_NAME))
async def _embeddings_workflow(query_text: str) -> str:
    raw = _EMBEDDINGS.generate(inputs=["Watsonx tracing", "Respan observability"])
    documents = _EMBEDDINGS.embed_documents(
        texts=["Trace model calls", "Inspect embedding usage"]
    )
    query = _EMBEDDINGS.embed_query(text=query_text)
    async_raw = await _EMBEDDINGS.agenerate(inputs=["Async embedding request"])
    async_documents = await _EMBEDDINGS.aembed_documents(
        texts=["Async one", "Async two"]
    )
    async_query = await _EMBEDDINGS.aembed_query(text="Async query")
    return "\n".join(
        [
            f"generate={_shape(raw)}",
            f"embed_documents={_shape(documents)}",
            f"embed_query={_shape(query)}",
            f"agenerate={_shape(async_raw)}",
            f"aembed_documents={_shape(async_documents)}",
            f"aembed_query={_shape(async_query)}",
        ]
    )


async def _run_embeddings(custom_identifier: str) -> str:
    global _EMBEDDINGS
    embeddings = make_embeddings()
    _EMBEDDINGS = embeddings
    with example_attributes(EXAMPLE_NAME, custom_identifier):
        try:
            return await _embeddings_workflow("What does tracing capture?")
        finally:
            close_provider(embeddings)


def run_embeddings() -> None:
    respan = make_respan(EXAMPLE_NAME)
    custom_identifier = make_custom_identifier(EXAMPLE_NAME)
    output = ""

    try:
        output = asyncio.run(_run_embeddings(custom_identifier))
    finally:
        respan.shutdown()

    print_lookup(EXAMPLE_NAME, custom_identifier, output)


if __name__ == "__main__":
    run_embeddings()
