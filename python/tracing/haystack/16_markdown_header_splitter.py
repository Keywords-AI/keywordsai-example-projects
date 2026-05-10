"""One-script example for MarkdownHeaderSplitter."""

from _shared import configure_respan, finish_respan, print_result


def run_markdown_header_splitter_example():
    respan = configure_respan("haystack-markdown-header-splitter")
    try:
        from haystack import Document
        from haystack.components.preprocessors import MarkdownHeaderSplitter

        splitter = MarkdownHeaderSplitter(
            header_split_levels=[1, 2],
            keep_headers=True,
        )
        result = splitter.run(
            [Document(content="# Intro\nOverview\n## Details\nMore text")]
        )
        print_result("MarkdownHeaderSplitter", result)
        return result
    finally:
        finish_respan(respan)


if __name__ == "__main__":
    run_markdown_header_splitter_example()
