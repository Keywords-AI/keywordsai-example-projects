"""One-script example for JSONConverter."""

from pathlib import Path
from tempfile import TemporaryDirectory

from _shared import configure_respan, finish_respan, print_result, write_sample_files


def run_json_converter_example():
    respan = configure_respan("haystack-json-converter")
    try:
        from haystack.components.converters import JSONConverter

        with TemporaryDirectory() as directory:
            files = write_sample_files(Path(directory))
            converter = JSONConverter(
                jq_schema=".[]",
                content_key="text",
                extra_meta_fields={"kind"},
            )
            result = converter.run([files["json"]])
        print_result("JSONConverter", result)
        return result
    finally:
        finish_respan(respan)


if __name__ == "__main__":
    run_json_converter_example()
