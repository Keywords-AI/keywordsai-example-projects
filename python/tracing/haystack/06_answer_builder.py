"""One-script example for AnswerBuilder."""

from _shared import configure_respan, finish_respan, print_result, sample_documents


def run_answer_builder_example():
    respan = configure_respan("haystack-answer-builder")
    try:
        from haystack.components.builders import AnswerBuilder

        builder = AnswerBuilder()
        result = builder.run(
            query="Who created Python?",
            replies=["Python was created by Guido van Rossum."],
            documents=sample_documents()[:1],
        )
        print_result("AnswerBuilder", result)
        return result
    finally:
        finish_respan(respan)


if __name__ == "__main__":
    run_answer_builder_example()
