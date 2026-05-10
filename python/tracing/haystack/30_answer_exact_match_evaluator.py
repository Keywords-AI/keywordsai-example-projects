"""One-script example for AnswerExactMatchEvaluator."""

from _shared import configure_respan, finish_respan, print_result


def run_answer_exact_match_evaluator_example():
    respan = configure_respan("haystack-answer-exact-match-evaluator")
    try:
        from haystack.components.evaluators import AnswerExactMatchEvaluator

        evaluator = AnswerExactMatchEvaluator()
        result = evaluator.run(
            ground_truth_answers=["Paris"],
            predicted_answers=["Paris"],
        )
        print_result("AnswerExactMatchEvaluator", result)
        return result
    finally:
        finish_respan(respan)


if __name__ == "__main__":
    run_answer_exact_match_evaluator_example()
