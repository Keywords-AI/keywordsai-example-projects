from __future__ import annotations

from typing import Any

from _loopback import LoopbackDatabaseError, install_loopback
from _shared import (
    create_respan,
    finish_respan,
    print_result,
    run_id,
    workflow_attributes,
)
from respan import Respan, workflow

WORKFLOW_NAME = "pgvector_bulk_server_cursor_failure_workflow"
SDK: Any | None = None


def _sdk() -> Any:
    if SDK is None:
        raise RuntimeError("PGVector loopback is not initialized")
    return SDK


@workflow(name=WORKFLOW_NAME)
def run_bulk_server_cursor_failure(scenario: str) -> dict:
    sdk = _sdk()
    vector = [round(index / 256, 6) for index in range(256)]
    rows = [("bounded-vector", vector, 0.0)]
    connection = sdk.psycopg.Connection(rows)
    server_cursor = None
    mutation_cursor = None
    try:
        server_cursor = connection.cursor(name="respan_pgvector_server_cursor")
        mutation_cursor = connection.cursor()
        sdk.pgvector_psycopg.register_vector(connection)
        mutation_cursor.executemany(
            "INSERT INTO documents (label, embedding) VALUES (%s, %s)",
            [("bounded-vector", vector), ("basis", [1.0, 0.0, 0.0])],
        )
        server_cursor.execute(
            "SELECT label, embedding, embedding <#> %s AS distance "
            "FROM documents ORDER BY distance LIMIT 1",
            (vector,),
        )
        fetched = server_cursor.fetchmany(1)
        try:
            mutation_cursor.execute("BROKEN VECTOR QUERY", ([0.0, 0.0, 0.0],))
        except LoopbackDatabaseError as exc:
            failure = {"error": type(exc).__name__, "message": str(exc)}
        else:
            raise AssertionError("the deterministic failure path did not fail")
        return {
            "failure": failure,
            "fetched": {
                "count": len(fetched),
                "labels": [row[0] for row in fetched],
                "vector_dimensions": [len(row[1]) for row in fetched],
            },
            "inserted": mutation_cursor.rowcount,
            "registered": connection.vector_registered,
            "scenario": scenario,
        }
    finally:
        try:
            if server_cursor is not None:
                server_cursor.close()
        finally:
            try:
                if mutation_cursor is not None:
                    mutation_cursor.close()
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
            result = run_bulk_server_cursor_failure("bulk-server-cursor-failure")
        print_result(WORKFLOW_NAME, result, marker)
    finally:
        finish_respan(respan)


if __name__ == "__main__":
    main()
