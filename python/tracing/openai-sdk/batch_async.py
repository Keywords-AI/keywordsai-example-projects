"""Log deterministic batch results after the submission workflow completes."""

from respan import get_client, task, workflow

from _batch_data import batch_requests, batch_results
from _shared import example_attributes, finish_respan, make_respan, print_result

EXAMPLE = "batch-async"
respan = make_respan(EXAMPLE)


@task(name="submit_batch")
def submit_batch() -> dict[str, str]:
    return {
        "batch_id": "batch_deterministic",
        "trace_id": get_client().get_current_trace_id(),
    }


@workflow(name="openai_batch_submit")
def submit() -> dict[str, str]:
    return submit_batch()


try:
    with example_attributes(EXAMPLE):
        saved = submit()
        requests = batch_requests()
        results = batch_results(requests)
        respan.log_batch_results(requests, results, trace_id=saved["trace_id"])
        print_result(EXAMPLE, f"batch_id={saved['batch_id']} logged={len(results)}")
finally:
    finish_respan(respan)
