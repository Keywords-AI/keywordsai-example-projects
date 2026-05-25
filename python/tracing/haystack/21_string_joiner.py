"""One-script example for StringJoiner."""

from _shared import configure_respan, finish_respan, print_result


def run_string_joiner_example():
    respan = configure_respan("haystack-string-joiner")
    try:
        from haystack.components.joiners import StringJoiner

        result = StringJoiner().run(strings=["alpha", "beta"])
        print_result("StringJoiner", result)
        return result
    finally:
        finish_respan(respan)


if __name__ == "__main__":
    run_string_joiner_example()
