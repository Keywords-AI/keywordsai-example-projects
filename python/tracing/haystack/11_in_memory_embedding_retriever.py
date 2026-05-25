"""One-script example for InMemoryEmbeddingRetriever."""

from _shared import configure_respan, finish_respan, print_result, sample_document_store


def run_in_memory_embedding_retriever_example():
    respan = configure_respan("haystack-in-memory-embedding-retriever")
    try:
        from haystack.components.retrievers.in_memory import InMemoryEmbeddingRetriever

        retriever = InMemoryEmbeddingRetriever(sample_document_store(), top_k=2)
        result = retriever.run(query_embedding=[1.0, 0.0, 0.0])
        print_result("InMemoryEmbeddingRetriever", result)
        return result
    finally:
        finish_respan(respan)


if __name__ == "__main__":
    run_in_memory_embedding_retriever_example()
