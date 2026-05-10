"""One-script example for DocumentJoiner."""

from _shared import configure_respan, finish_respan, print_result, sample_documents


def run_document_joiner_example():
    respan = configure_respan("haystack-document-joiner")
    try:
        from haystack.components.joiners import DocumentJoiner

        documents = sample_documents()
        joiner = DocumentJoiner(join_mode="concatenate", top_k=2)
        result = joiner.run(documents=[documents[:2], documents[2:]])
        print_result("DocumentJoiner", result)
        return result
    finally:
        finish_respan(respan)


if __name__ == "__main__":
    run_document_joiner_example()
