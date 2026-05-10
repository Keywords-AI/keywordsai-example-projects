"""One-script example for CSVToDocument."""

from pathlib import Path
from tempfile import TemporaryDirectory

from _shared import configure_respan, finish_respan, print_result, write_sample_files


def run_csv_to_document_example():
    respan = configure_respan("haystack-csv-to-document")
    try:
        from haystack.components.converters import CSVToDocument

        with TemporaryDirectory() as directory:
            files = write_sample_files(Path(directory))
            converter = CSVToDocument(conversion_mode="row")
            result = converter.run([files["csv"]], content_column="text")
        print_result("CSVToDocument", result)
        return result
    finally:
        finish_respan(respan)


if __name__ == "__main__":
    run_csv_to_document_example()
