"""One-script example for OpenAIGenerator through the Respan gateway."""

import os

from _shared import configure_respan, finish_respan, print_result


def run_openai_generator_gateway_example():
    respan = configure_respan("haystack-openai-generator-gateway", use_gateway=True)
    try:
        from haystack.components.generators import OpenAIGenerator

        generator = OpenAIGenerator(model=os.getenv("RESPAN_MODEL", "gpt-4o-mini"))
        result = generator.run(
            prompt="Answer in one sentence: what is retrieval augmented generation?",
            generation_kwargs={"temperature": 0.0},
        )
        print_result("OpenAIGenerator gateway", result)
        return result
    finally:
        finish_respan(respan)


if __name__ == "__main__":
    run_openai_generator_gateway_example()
