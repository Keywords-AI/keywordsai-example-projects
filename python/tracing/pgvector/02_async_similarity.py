from __future__ import annotations

import asyncio
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

WORKFLOW_NAME = "pgvector_async_similarity_workflow"
SDK: Any | None = None


def _sdk() -> Any:
    if SDK is None:
        raise RuntimeError("PGVector loopback is not initialized")
    return SDK


@workflow(name=WORKFLOW_NAME)
async def run_async_similarity(query_vector: list[float], limit: int) -> dict:
    sdk = _sdk()
    rows = [("async", [0.4, 0.5, 0.6], 0.0)]
    connection = sdk.psycopg.AsyncConnection(rows)
    cursor = None
    try:
        await sdk.pgvector_psycopg.register_vector_async(connection)
        cursor = await connection.execute(
            "SELECT label, embedding, embedding <=> %s AS distance "
            "FROM documents ORDER BY distance LIMIT %s",
            (query_vector, limit),
        )
        row = await cursor.fetchone()
        return {
            "registered": connection.vector_registered,
            "row": row,
        }
    finally:
        try:
            if cursor is not None:
                await cursor.close()
        finally:
            try:
                await connection.rollback()
            finally:
                await connection.close()


async def run() -> None:
    global SDK
    marker = run_id()
    SDK = install_loopback()
    respan = create_respan(WORKFLOW_NAME, marker)
    try:
        with Respan.propagate_attributes(**workflow_attributes(WORKFLOW_NAME, marker)):
            result = await run_async_similarity([0.4, 0.5, 0.6], 1)
        print_result(WORKFLOW_NAME, result, marker)
    finally:
        finish_respan(respan)


if __name__ == "__main__":
    asyncio.run(run())
