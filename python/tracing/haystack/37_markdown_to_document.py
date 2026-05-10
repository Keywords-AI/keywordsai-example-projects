"""One-script example for MarkdownToDocument."""

from pathlib import Path
from tempfile import TemporaryDirectory

from _shared import configure_respan, finish_respan, print_result, write_sample_files


def run_markdown_to_document_example():
    respan = configure_respan("haystack-markdown-to-document")
    try:
        from haystack.components.converters import MarkdownToDocument

        with TemporaryDirectory() as directory:
            files = write_sample_files(Path(directory))
            result = MarkdownToDocument().run([files["markdown"]])
        print_result("MarkdownToDocument", result)
        return result
    finally:
        finish_respan(respan)


if __name__ == "__main__":
    run_markdown_to_document_example()
