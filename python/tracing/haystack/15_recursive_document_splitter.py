"""One-script example for RecursiveDocumentSplitter."""

from _shared import configure_respan, finish_respan, print_result


def run_recursive_document_splitter_example():
    respan = configure_respan("haystack-recursive-document-splitter")
    try:
        from haystack import Document
        from haystack.components.preprocessors import RecursiveDocumentSplitter

        splitter = RecursiveDocumentSplitter(
            split_unit="word",
            split_length=4,
            split_overlap=1,
            separators=[" "],
        )
        result = splitter.run(
            [Document(content="one two three four five six seven eight")]
        )
        print_result("RecursiveDocumentSplitter", result)
        return result
    finally:
        finish_respan(respan)


if __name__ == "__main__":
    run_recursive_document_splitter_example()
