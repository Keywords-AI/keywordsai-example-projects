from __future__ import annotations

import ragas
from _shared import create_respan, example_context, finish_respan
from ragas import EvaluationDataset
from ragas.metrics import ExactMatch
from respan import workflow

CASE = "evaluate"


@workflow(name="ragas_evaluate")
def evaluation_workflow(question: str, answer: str) -> dict[str, object]:
    dataset = EvaluationDataset.from_list(
        [{"user_input": question, "response": answer, "reference": "Paris"}]
    )
    result = ragas.evaluate(
        dataset,
        metrics=[ExactMatch()],
        experiment_name="offline-exact-match",
        show_progress=False,
    )
    return {"exact_match": list(result["exact_match"])}


def main() -> None:
    respan = create_respan()
    try:
        with example_context(CASE):
            result = evaluation_workflow("What is France's capital?", "Paris")
            print(result, flush=True)
    finally:
        finish_respan(respan)


if __name__ == "__main__":
    main()
