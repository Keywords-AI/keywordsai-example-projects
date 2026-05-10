"""One-script example for DocumentCleaner."""

from _shared import configure_respan, finish_respan, print_result


def run_document_cleaner_example():
    respan = configure_respan("haystack-document-cleaner")
    try:
        from haystack import Document
        from haystack.components.preprocessors import DocumentCleaner

        cleaner = DocumentCleaner(
            remove_regex="SECRET",
            remove_extra_whitespaces=True,
            strip_whitespaces=True,
        )
        result = cleaner.run([Document(content="  Keep   this. SECRET\n\n")])
        print_result("DocumentCleaner", result)
        return result
    finally:
        finish_respan(respan)


if __name__ == "__main__":
    run_document_cleaner_example()
