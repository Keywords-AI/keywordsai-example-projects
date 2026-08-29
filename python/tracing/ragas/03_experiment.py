from __future__ import annotations

import asyncio

import ragas
from _shared import create_respan, example_context, finish_respan
from ragas.backends.inmemory import InMemoryBackend
from ragas.dataset import Dataset
from respan import workflow

CASE = "experiment"
BACKEND = InMemoryBackend()


@ragas.experiment(backend=BACKEND, name_prefix="offline")
async def answer_row(row: dict[str, str]) -> dict[str, str]:
    return {"answer": row["answer"].upper()}


@workflow(name="ragas_experiment")
async def experiment_workflow(dataset_name: str) -> dict[str, object]:
    dataset = Dataset(
        name=dataset_name,
        backend=BACKEND,
        data=[{"answer": "Paris"}, {"answer": "Rome"}],
    )
    result = await answer_row.arun(dataset, name="two-rows")
    return {"experiment": result.name, "rows": len(result)}


async def main() -> None:
    respan = create_respan()
    try:
        with example_context(CASE):
            result = await experiment_workflow("capital-answers")
            print(result, flush=True)
    finally:
        finish_respan(respan)


if __name__ == "__main__":
    asyncio.run(main())
