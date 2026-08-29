"""Query engine: build a SummaryIndex and query it."""

from _shared import (
    configure_llama_index,
    create_respan,
    print_result,
    sample_documents,
    traced_example,
)
from llama_index.core import SummaryIndex


def run_query_engine() -> None:
    context = create_respan(
        app_name="llama-index-04-query-engine",
        example_name="04_query_engine",
    )
    configure_llama_index(settings=context.settings)
    query = "Summarize what the example documents say about Respan and LlamaIndex."

    with traced_example(
        context,
        root_span_name=context.example_name,
        input_data={"query": query},
    ) as root_span:
        index = SummaryIndex.from_documents(sample_documents())
        response = index.as_query_engine().query(query)
        root_span.set_output({"answer": str(response)})

    print_result("Query answer", response)
    print_result("Example run id", context.run_id)


if __name__ == "__main__":
    run_query_engine()
