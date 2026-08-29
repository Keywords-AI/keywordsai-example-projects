"""Deterministic OpenAI Batch result logging without provider-side polling."""

from respan import task, workflow

from _batch_data import batch_requests, batch_results
from _shared import example_attributes, finish_respan, make_respan, print_result

EXAMPLE = "batch"
respan = make_respan(EXAMPLE)


@task(name="log_batch_results")
def log_results() -> int:
    requests = batch_requests()
    results = batch_results(requests)
    respan.log_batch_results(requests, results)
    return len(results)


@workflow(name="openai_batch_pipeline")
def run() -> str:
    return f"logged_results={log_results()}"


try:
    with example_attributes(EXAMPLE):
        print_result(EXAMPLE, run())
finally:
    finish_respan(respan)
