"""One-script example for DocumentSplitter."""

from _shared import configure_respan, finish_respan, print_result


def run_document_splitter_example():
    respan = configure_respan("haystack-document-splitter")
    try:
        from haystack import Document
        from haystack.components.preprocessors import DocumentSplitter

        splitter = DocumentSplitter(split_by="word", split_length=4, split_overlap=1)
        result = splitter.run(
            [Document(content="one two three four five six seven eight")]
        )
        print_result("DocumentSplitter", result)
        return result
    finally:
        finish_respan(respan)


if __name__ == "__main__":
    run_document_splitter_example()
