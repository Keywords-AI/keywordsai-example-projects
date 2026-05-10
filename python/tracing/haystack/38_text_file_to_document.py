"""One-script example for TextFileToDocument."""

from pathlib import Path
from tempfile import TemporaryDirectory

from _shared import configure_respan, finish_respan, print_result, write_sample_files


def run_text_file_to_document_example():
    respan = configure_respan("haystack-text-file-to-document")
    try:
        from haystack.components.converters import TextFileToDocument

        with TemporaryDirectory() as directory:
            files = write_sample_files(Path(directory))
            result = TextFileToDocument().run([files["text"]])
        print_result("TextFileToDocument", result)
        return result
    finally:
        finish_respan(respan)


if __name__ == "__main__":
    run_text_file_to_document_example()
