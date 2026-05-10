"""One-script example for TextCleaner."""

from _shared import configure_respan, finish_respan, print_result


def run_text_cleaner_example():
    respan = configure_respan("haystack-text-cleaner")
    try:
        from haystack.components.preprocessors import TextCleaner

        cleaner = TextCleaner(
            convert_to_lowercase=True,
            remove_numbers=True,
            remove_punctuation=True,
        )
        result = cleaner.run(["Haystack 2.0, tracing!"])
        print_result("TextCleaner", result)
        return result
    finally:
        finish_respan(respan)


if __name__ == "__main__":
    run_text_cleaner_example()
