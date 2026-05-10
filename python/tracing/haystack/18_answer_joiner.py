"""One-script example for AnswerJoiner."""

from _shared import configure_respan, finish_respan, print_result


def run_answer_joiner_example():
    respan = configure_respan("haystack-answer-joiner")
    try:
        from haystack.components.joiners import AnswerJoiner
        from haystack.dataclasses import GeneratedAnswer

        answers = [
            [GeneratedAnswer(data="first answer", query="q", documents=[])],
            [GeneratedAnswer(data="second answer", query="q", documents=[])],
        ]
        result = AnswerJoiner().run(answers=answers)
        print_result("AnswerJoiner", result)
        return result
    finally:
        finish_respan(respan)


if __name__ == "__main__":
    run_answer_joiner_example()
