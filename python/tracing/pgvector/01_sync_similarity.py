from __future__ import annotations

from typing import Any

from _loopback import install_loopback
from _shared import (
    create_respan,
    finish_respan,
    print_result,
    run_id,
    workflow_attributes,
)
from respan import Respan, workflow

WORKFLOW_NAME = "pgvector_sync_similarity_workflow"
SDK: Any | None = None


def _sdk() -> Any:
    if SDK is None:
        raise RuntimeError("PGVector loopback is not initialized")
    return SDK


@workflow(name=WORKFLOW_NAME)
def run_sync_similarity(query_vector: list[float], limit: int) -> dict:
    sdk = _sdk()
    connection = sdk.psycopg.Connection()
    cursor = None
    try:
        sdk.pgvector_psycopg.register_vector(connection)
        cursor = connection.execute(
            "SELECT label, embedding, embedding <-> %s AS distance "
            "FROM documents ORDER BY distance LIMIT %s",
            (query_vector, limit),
        )
        rows = cursor.fetchall()
        return {
            "registered": connection.vector_registered,
            "rows": rows,
        }
    finally:
        try:
            if cursor is not None:
                cursor.close()
        finally:
            try:
                connection.rollback()
            finally:
                connection.close()


def main() -> None:
    global SDK
    marker = run_id()
    SDK = install_loopback()
    respan = create_respan(WORKFLOW_NAME, marker)
    try:
        with Respan.propagate_attributes(**workflow_attributes(WORKFLOW_NAME, marker)):
            result = run_sync_similarity([1.0, 0.0, 0.0], 2)
        print_result(WORKFLOW_NAME, result, marker)
    finally:
        finish_respan(respan)


if __name__ == "__main__":
    main()
