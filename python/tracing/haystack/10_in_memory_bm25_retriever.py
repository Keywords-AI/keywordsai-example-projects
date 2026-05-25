"""One-script example for InMemoryBM25Retriever."""

from _shared import configure_respan, finish_respan, print_result, sample_document_store


def run_in_memory_bm25_retriever_example():
    respan = configure_respan("haystack-in-memory-bm25-retriever")
    try:
        from haystack.components.retrievers.in_memory import InMemoryBM25Retriever

        retriever = InMemoryBM25Retriever(sample_document_store(), top_k=2)
        result = retriever.run(query="Python programming")
        print_result("InMemoryBM25Retriever", result)
        return result
    finally:
        finish_respan(respan)


if __name__ == "__main__":
    run_in_memory_bm25_retriever_example()
