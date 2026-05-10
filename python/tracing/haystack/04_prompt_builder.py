"""One-script example for PromptBuilder."""

from _shared import configure_respan, finish_respan, print_result


def run_prompt_builder_example():
    respan = configure_respan("haystack-prompt-builder")
    try:
        from haystack.components.builders import PromptBuilder

        builder = PromptBuilder(
            "Summarize {{ topic }} in {{ style }} style.",
            required_variables=["topic", "style"],
        )
        result = builder.run(topic="Haystack", style="plain")
        print_result("PromptBuilder", result)
        return result
    finally:
        finish_respan(respan)


if __name__ == "__main__":
    run_prompt_builder_example()
