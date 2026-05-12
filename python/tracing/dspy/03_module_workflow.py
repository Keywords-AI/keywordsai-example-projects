"""Trace a custom DSPy Module composed from smaller predictors."""

from __future__ import annotations

import dspy

from _shared import create_respan, print_result, traced_example


class ContextBuilder(dspy.Signature):
    """Create a short supporting context for the question."""

    question: str = dspy.InputField()
    context: str = dspy.OutputField()


class ContextualAnswer(dspy.Signature):
    """Answer the question using the provided context."""

    question: str = dspy.InputField()
    context: str = dspy.InputField()
    answer: str = dspy.OutputField()


class SupportAnswerer(dspy.Module):
    def __init__(self) -> None:
        super().__init__()
        self.build_context = dspy.Predict(ContextBuilder)
        self.answer_question = dspy.ChainOfThought(ContextualAnswer)

    def forward(self, question: str) -> dspy.Prediction:
        context = self.build_context(question=question).context
        prediction = self.answer_question(question=question, context=context)
        return dspy.Prediction(context=context, answer=prediction.answer)


def run_module_workflow_example() -> None:
    context = create_respan(
        app_name="dspy-03-module-workflow",
        example_name="03_module_workflow",
        temperature=0.1,
    )
    answerer = SupportAnswerer()
    question = "Why is a single trace tree useful for DSPy programs?"

    with traced_example(context, input_data={"question": question}) as span:
        prediction = answerer(question=question)
        span.set_output(
            {
                "context": prediction.context,
                "answer": prediction.answer,
            }
        )

    print_result("Context", prediction.context)
    print_result("Answer", prediction.answer)
    context.respan.flush()


if __name__ == "__main__":
    run_module_workflow_example()
