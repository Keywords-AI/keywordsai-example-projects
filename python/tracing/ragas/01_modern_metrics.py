from __future__ import annotations

import asyncio

from _shared import create_respan, example_context, finish_respan
from ragas.metrics.collections import ExactMatch
from respan import workflow

CASE = "modern_metrics"


@workflow(name="ragas_modern_metrics")
def metric_workflow(reference: str, response: str) -> dict[str, object]:
    metric = ExactMatch()
    sync_value = metric.score(reference=reference, response=response).value
    async_value = asyncio.run(
        metric.ascore(reference=reference, response=response)
    ).value
    batch = metric.batch_score(
        [
            {"reference": reference, "response": response},
            {"reference": "Rome", "response": "Milan"},
        ]
    )
    return {
        "sync": sync_value,
        "async": async_value,
        "batch": [item.value for item in batch],
    }


def main() -> None:
    respan = create_respan()
    try:
        with example_context(CASE):
            result = metric_workflow("Paris", "Paris")
            print(result, flush=True)
    finally:
        finish_respan(respan)


if __name__ == "__main__":
    main()
