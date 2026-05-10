"""One-script example for DocumentWriter."""

from _shared import configure_respan, finish_respan, print_result, sample_documents


def run_document_writer_example():
    respan = configure_respan("haystack-document-writer")
    try:
        from haystack.components.writers import DocumentWriter
        from haystack.document_stores.in_memory import InMemoryDocumentStore

        store = InMemoryDocumentStore()
        writer = DocumentWriter(store)
        result = writer.run(sample_documents())
        print_result("DocumentWriter", result)
        return result
    finally:
        finish_respan(respan)


if __name__ == "__main__":
    run_document_writer_example()
