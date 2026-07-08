"""Trace Arize span and ML data operations with Respan.

Run:
    python 01_spans_and_ml.py
"""

from __future__ import annotations

from datetime import datetime, timezone

import pandas as pd
from arize.ml.types import Environments, ModelTypes, Schema

from _shared import (
    create_arize_client,
    create_respan,
    flush_and_shutdown,
    install_offline_arize_operations,
    new_run_id,
    print_result,
    print_trace_lookup,
    workflow_context,
)

WORKFLOW_NAME = "Arize Spans And ML Workflow"
EXAMPLE_NAME = "01_spans_and_ml"
START_TIME = datetime(2026, 1, 1, tzinfo=timezone.utc)
END_TIME = datetime(2026, 1, 2, tzinfo=timezone.utc)


def run_spans_and_ml() -> str:
    run_id = new_run_id(EXAMPLE_NAME)
    install_offline_arize_operations()
    respan = create_respan(
        workflow_name=WORKFLOW_NAME,
        run_id=run_id,
        example_name=EXAMPLE_NAME,
    )
    client = create_arize_client()
    spans_df = pd.DataFrame(
        [
            {
                "context.span_id": "span-1",
                "context.trace_id": "trace-1",
                "name": "offline_arize_span",
                "span_kind": "LLM",
                "start_time": "2026-01-01T00:00:00.000000+00:00",
                "end_time": "2026-01-01T00:00:01.000000+00:00",
            }
        ]
    )
    updates_df = pd.DataFrame([{"context.span_id": "span-1", "eval.quality.score": 1}])
    model_schema = Schema()

    with workflow_context(
        respan,
        workflow_name=WORKFLOW_NAME,
        run_id=run_id,
        example_name=EXAMPLE_NAME,
    ):
        print_result(
            "spans.log",
            client.spans.log(
                space_id="space-offline",
                project_name="project-offline",
                dataframe=spans_df,
                evals_dataframe=updates_df,
            ),
        )
        print_result(
            "spans.update_evaluations",
            client.spans.update_evaluations(
                space_id="space-offline",
                project_name="project-offline",
                dataframe=updates_df,
            ),
        )
        print_result(
            "spans.update_annotations",
            client.spans.update_annotations(
                space_id="space-offline",
                project_name="project-offline",
                dataframe=updates_df,
            ),
        )
        print_result(
            "spans.update_metadata",
            client.spans.update_metadata(
                space_id="space-offline",
                project_name="project-offline",
                dataframe=updates_df,
            ),
        )
        print_result("spans.list", client.spans.list(project="project-offline", space="space-offline"))
        print_result(
            "spans.annotate",
            client.spans.annotate(project="project-offline", space="space-offline", annotations=[]),
        )
        print_result(
            "spans.delete",
            client.spans.delete(project="project-offline", span_ids=["span-1"], space="space-offline"),
        )
        print_result(
            "spans.export_to_df",
            client.spans.export_to_df(
                space_id="space-offline",
                project_name="project-offline",
                start_time=START_TIME,
                end_time=END_TIME,
            ),
        )
        print_result(
            "spans.export_to_parquet",
            client.spans.export_to_parquet(
                space_id="space-offline",
                project_name="project-offline",
                start_time=START_TIME,
                end_time=END_TIME,
                path="/tmp/arize-spans.parquet",
            ),
        )
        print_result(
            "ml.log_stream",
            client.ml.log_stream(
                space_id="space-offline",
                model_name="fraud-model",
                model_type=ModelTypes.SCORE_CATEGORICAL,
                environment=Environments.PRODUCTION,
                prediction_label=("not fraud", 0.9),
                actual_label=("not fraud", 1.0),
            ),
        )
        print_result(
            "ml.log",
            client.ml.log(
                space_id="space-offline",
                model_name="fraud-model",
                dataframe=spans_df,
                schema=model_schema,
                model_type=ModelTypes.SCORE_CATEGORICAL,
                environment=Environments.PRODUCTION,
            ),
        )
        print_result(
            "ml.export_to_df",
            client.ml.export_to_df(
                space_id="space-offline",
                model_name="fraud-model",
                environment=Environments.PRODUCTION,
                start_time=START_TIME,
                end_time=END_TIME,
            ),
        )
        print_result(
            "ml.export_to_parquet",
            client.ml.export_to_parquet(
                space_id="space-offline",
                model_name="fraud-model",
                environment=Environments.PRODUCTION,
                start_time=START_TIME,
                end_time=END_TIME,
                path="/tmp/arize-ml.parquet",
            ),
        )

    flush_and_shutdown(respan)
    print_trace_lookup(workflow_name=WORKFLOW_NAME, run_id=run_id)
    return run_id


if __name__ == "__main__":
    run_spans_and_ml()
