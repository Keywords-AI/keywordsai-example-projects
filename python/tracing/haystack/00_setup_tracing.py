"""Tracing setup for a local Haystack pipeline."""

from _shared import configure_respan, finish_respan, print_result


def run_setup_tracing_example():
    respan = configure_respan("haystack-setup-tracing")
    try:
        from haystack import Pipeline
        from haystack.components.builders import PromptBuilder

        pipeline = Pipeline()
        pipeline.add_component(
            "prompt_builder",
            PromptBuilder(
                "Answer this in one sentence: {{ question }}",
                required_variables=["question"],
            ),
        )

        result = pipeline.run(
            {"prompt_builder": {"question": "What does Haystack provide?"}}
        )
        print_result("Tracing setup result", result)
        return result
    finally:
        finish_respan(respan)


if __name__ == "__main__":
    run_setup_tracing_example()
