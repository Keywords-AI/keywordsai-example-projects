"""One-script example for DocumentLengthRouter."""

from _shared import configure_respan, finish_respan, print_result


def run_document_length_router_example():
    respan = configure_respan("haystack-document-length-router")
    try:
        from haystack import Document
        from haystack.components.routers import DocumentLengthRouter

        router = DocumentLengthRouter(threshold=10)
        result = router.run(
            [
                Document(content="short"),
                Document(content="this document is longer than the threshold"),
            ]
        )
        print_result("DocumentLengthRouter", result)
        return result
    finally:
        finish_respan(respan)


if __name__ == "__main__":
    run_document_length_router_example()
