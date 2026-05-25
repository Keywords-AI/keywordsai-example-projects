"""One-script example for RegexTextExtractor."""

from _shared import configure_respan, finish_respan, print_result


def run_regex_text_extractor_example():
    respan = configure_respan("haystack-regex-text-extractor")
    try:
        from haystack.components.extractors import RegexTextExtractor

        extractor = RegexTextExtractor(r"ticket=(\d+)")
        result = extractor.run("support ticket=42")
        print_result("RegexTextExtractor", result)
        return result
    finally:
        finish_respan(respan)


if __name__ == "__main__":
    run_regex_text_extractor_example()
