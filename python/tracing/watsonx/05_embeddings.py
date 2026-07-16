from __future__ import annotations

import asyncio

from respan import workflow

from _shared import (
    example_attributes,
    make_custom_identifier,
    make_embeddings,
    make_respan,
    print_lookup,
    workflow_name,
)

EXAMPLE_NAME = "embeddings"


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
async def _embeddings_workflow(embeddings) -> str:
    raw = embeddings.generate(inputs=["Watsonx tracing", "Respan observability"])
    documents = embeddings.embed_documents(
        texts=["Trace model calls", "Inspect embedding usage"]
    )
    query = embeddings.embed_query(text="What does tracing capture?")
    async_raw = await embeddings.agenerate(inputs=["Async embedding request"])
    async_documents = await embeddings.aembed_documents(texts=["Async one", "Async two"])
    async_query = await embeddings.aembed_query(text="Async query")
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
    embeddings = make_embeddings()
    with example_attributes(EXAMPLE_NAME, custom_identifier):
        return await _embeddings_workflow(embeddings)


def run_embeddings() -> None:
    respan = make_respan(EXAMPLE_NAME)
    custom_identifier = make_custom_identifier(EXAMPLE_NAME)
    output = ""

    try:
        output = asyncio.run(_run_embeddings(custom_identifier))
    finally:
        respan.flush()
        respan.shutdown()

    print_lookup(EXAMPLE_NAME, custom_identifier, output)


if __name__ == "__main__":
    run_embeddings()
