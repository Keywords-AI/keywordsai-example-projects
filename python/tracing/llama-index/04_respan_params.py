"""Query engine: build a SummaryIndex and query it."""

from llama_index.core import SummaryIndex

from _shared import configure_llama_index, create_respan, print_result, sample_documents
from _shared import traced_example


def run_query_engine() -> None:
    context = create_respan(
        app_name="llama-index-04-query-engine",
        example_name="04_query_engine",
    )
    configure_llama_index(settings=context.settings)

    with traced_example(context, root_span_name=context.example_name):
        index = SummaryIndex.from_documents(sample_documents())
        response = index.as_query_engine().query(
            "Summarize what the example documents say about Respan and LlamaIndex."
        )

    print_result("Query answer", response)
    print_result("Example run id", context.run_id)


if __name__ == "__main__":
    run_query_engine()
