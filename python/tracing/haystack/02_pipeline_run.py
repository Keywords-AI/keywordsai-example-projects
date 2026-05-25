"""One-script example for Pipeline.run."""

from _shared import configure_respan, finish_respan, print_result


def run_pipeline_run_example():
    respan = configure_respan("haystack-pipeline-run")
    try:
        from haystack import Pipeline
        from haystack.components.builders import PromptBuilder

        pipeline = Pipeline()
        pipeline.add_component(
            "prompt_builder",
            PromptBuilder("Hello {{ name }}", required_variables=["name"]),
        )
        result = pipeline.run({"prompt_builder": {"name": "Ada"}})
        print_result("Pipeline.run", result)
        return result
    finally:
        finish_respan(respan)


if __name__ == "__main__":
    run_pipeline_run_example()
