"""One-script example for OutputAdapter."""

from _shared import configure_respan, finish_respan, print_result


def run_output_adapter_example():
    respan = configure_respan("haystack-output-adapter")
    try:
        from haystack.components.converters import OutputAdapter

        adapter = OutputAdapter("{{ value | int + 1 }}", output_type=int)
        result = adapter.run(value="41")
        print_result("OutputAdapter", result)
        return result
    finally:
        finish_respan(respan)


if __name__ == "__main__":
    run_output_adapter_example()
