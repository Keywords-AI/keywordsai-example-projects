"""One-script example for HTMLToDocument."""

from pathlib import Path
from tempfile import TemporaryDirectory

from _shared import configure_respan, finish_respan, print_result, write_sample_files


def run_html_to_document_example():
    respan = configure_respan("haystack-html-to-document")
    try:
        from haystack.components.converters import HTMLToDocument

        with TemporaryDirectory() as directory:
            files = write_sample_files(Path(directory))
            result = HTMLToDocument().run([files["html"]])
        print_result("HTMLToDocument", result)
        return result
    finally:
        finish_respan(respan)


if __name__ == "__main__":
    run_html_to_document_example()
