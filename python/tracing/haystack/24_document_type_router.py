"""One-script example for DocumentTypeRouter."""

from _shared import configure_respan, finish_respan, print_result


def run_document_type_router_example():
    respan = configure_respan("haystack-document-type-router")
    try:
        from haystack import Document
        from haystack.components.routers import DocumentTypeRouter

        router = DocumentTypeRouter(
            mime_types=["text/plain"],
            mime_type_meta_field="mime",
        )
        result = router.run(
            [
                Document(content="plain text", meta={"mime": "text/plain"}),
                Document(content="<p>html</p>", meta={"mime": "text/html"}),
            ]
        )
        print_result("DocumentTypeRouter", result)
        return result
    finally:
        finish_respan(respan)


if __name__ == "__main__":
    run_document_type_router_example()
