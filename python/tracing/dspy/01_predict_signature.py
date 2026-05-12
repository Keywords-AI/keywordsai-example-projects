"""Trace a DSPy Predict program built from a typed Signature."""

from __future__ import annotations

import dspy

from _shared import create_respan, print_result, traced_example


class BasicQuestion(dspy.Signature):
    """Answer the question with one concise sentence."""

    question: str = dspy.InputField()
    answer: str = dspy.OutputField()


def run_predict_signature_example() -> None:
    context = create_respan(
        app_name="dspy-01-predict-signature",
        example_name="01_predict_signature",
        temperature=0.1,
    )
    predict = dspy.Predict(BasicQuestion)
    question = "What does DSPy help developers build?"

    with traced_example(context, input_data={"question": question}) as span:
        prediction = predict(question=question)
        span.set_output({"answer": prediction.answer})

    print_result("Answer", prediction.answer)
    context.respan.flush()


if __name__ == "__main__":
    run_predict_signature_example()
