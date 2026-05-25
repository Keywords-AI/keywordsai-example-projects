"""One-script example for FileTypeRouter."""

from pathlib import Path
from tempfile import TemporaryDirectory

from _shared import configure_respan, finish_respan, print_result, write_sample_files


def run_file_type_router_example():
    respan = configure_respan("haystack-file-type-router")
    try:
        from haystack.components.routers import FileTypeRouter

        with TemporaryDirectory() as directory:
            files = write_sample_files(Path(directory))
            router = FileTypeRouter(mime_types=["text/plain", "text/markdown"])
            result = router.run([files["text"], files["markdown"]])
        print_result("FileTypeRouter", result)
        return result
    finally:
        finish_respan(respan)


if __name__ == "__main__":
    run_file_type_router_example()
