from __future__ import annotations

import asyncio
import math
import os
from itertools import islice
from typing import Any

import pgvector.psycopg as pgvector_psycopg
import psycopg
from _shared import (
    create_respan,
    finish_respan,
    load_repo_env,
    print_result,
    run_id,
    workflow_attributes,
)
from pgvector import Vector
from respan import Respan, workflow

WORKFLOW_NAME = "pgvector_live_postgres_workflow"
LIVE_DSN: str | None = None
MAX_RESULT_VECTOR_VALUES = 16
MAX_RESULT_TEXT_BYTES = 256


def _dsn() -> str:
    if LIVE_DSN is None:
        raise RuntimeError("PGVECTOR_DSN is not initialized")
    return LIVE_DSN


def _bounded_text(value: object) -> str:
    if type(value) is not str:
        value_type = type(value)
        return f"<{value_type.__module__}.{value_type.__qualname__}>"
    encoded = value.encode("utf-8", errors="replace")
    if len(encoded) <= MAX_RESULT_TEXT_BYTES:
        return value
    suffix = b"...[truncated]"
    prefix = encoded[: MAX_RESULT_TEXT_BYTES - len(suffix)].decode(
        "utf-8", errors="ignore"
    )
    return f"{prefix}{suffix.decode()}"


def _bounded_vector(value: object) -> dict[str, object]:
    if type(value) is not Vector:
        value_type = type(value)
        return {
            "type": f"{value_type.__module__}.{value_type.__qualname__}",
            "values": [],
            "truncated": True,
        }

    storage = value._value
    values: list[float | str] = []
    for item in islice(storage, MAX_RESULT_VECTOR_VALUES):
        number = float(item)
        values.append(number if math.isfinite(number) else "<non-finite>")
    return {
        "type": "pgvector.Vector",
        "values": values,
        "truncated": len(storage) > MAX_RESULT_VECTOR_VALUES,
    }


def _bounded_row(row: object) -> dict[str, object] | None:
    if row is None:
        return None
    if type(row) is not tuple:
        row_type = type(row)
        return {"type": f"{row_type.__module__}.{row_type.__qualname__}"}
    try:
        label = row[0]
        embedding = row[1]
    except IndexError:
        return {"type": "builtins.tuple", "columns": []}
    return {
        "label": _bounded_text(label),
        "embedding": _bounded_vector(embedding),
    }


def _sync_path(query_vector: list[float], limit: int) -> dict[str, Any]:
    connection = psycopg.connect(_dsn())
    try:
        extension = connection.execute(
            "SELECT 1 FROM pg_extension WHERE extname = 'vector'"
        )
        try:
            if not extension.fetchone():
                raise RuntimeError("PGVECTOR_DSN database does not install pgvector")
        finally:
            extension.close()

        pgvector_psycopg.register_vector(connection)
        create_cursor = connection.execute(
            "CREATE TEMP TABLE respan_pgvector_sync_example ("
            "label text, embedding vector(3))"
        )
        create_cursor.close()
        insert_cursor = connection.execute(
            "INSERT INTO respan_pgvector_sync_example VALUES (%s, %s)",
            ("sync-live", [0.1, 0.2, 0.3]),
        )
        insert_cursor.close()
        server_cursor = connection.cursor(name="respan_pgvector_live_server_cursor")
        try:
            server_cursor.execute(
                "SELECT label, embedding FROM respan_pgvector_sync_example "
                "ORDER BY embedding <-> %s LIMIT %s",
                (query_vector, limit),
            )
            row = server_cursor.fetchone()
        finally:
            server_cursor.close()
        return {
            "registered": True,
            "row": _bounded_row(row),
            "server_cursor": True,
        }
    finally:
        try:
            connection.rollback()
        finally:
            connection.close()


async def _async_path(query_vector: list[float], limit: int) -> dict[str, Any]:
    connection = await psycopg.AsyncConnection.connect(_dsn())
    try:
        extension = await connection.execute(
            "SELECT 1 FROM pg_extension WHERE extname = 'vector'"
        )
        try:
            if not await extension.fetchone():
                raise RuntimeError("PGVECTOR_DSN database does not install pgvector")
        finally:
            await extension.close()

        await pgvector_psycopg.register_vector_async(connection)
        create_cursor = await connection.execute(
            "CREATE TEMP TABLE respan_pgvector_async_example ("
            "label text, embedding vector(3))"
        )
        await create_cursor.close()
        insert_cursor = await connection.execute(
            "INSERT INTO respan_pgvector_async_example VALUES (%s, %s)",
            ("async-live", [0.4, 0.5, 0.6]),
        )
        await insert_cursor.close()
        server_cursor = connection.cursor(
            name="respan_pgvector_live_async_server_cursor"
        )
        try:
            await server_cursor.execute(
                "SELECT label, embedding FROM respan_pgvector_async_example "
                "ORDER BY embedding <-> %s LIMIT %s",
                (query_vector, limit),
            )
            row = await server_cursor.fetchone()
        finally:
            await server_cursor.close()
        return {
            "registered": True,
            "row": _bounded_row(row),
            "server_cursor": True,
        }
    finally:
        try:
            await connection.rollback()
        finally:
            await connection.close()


def _psycopg2_path(query_vector: list[float], limit: int) -> dict[str, Any]:
    import pgvector.psycopg2 as pgvector_psycopg2
    import psycopg2

    connection = psycopg2.connect(_dsn())
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1 FROM pg_extension WHERE extname = 'vector'")
            if not cursor.fetchone():
                raise RuntimeError("PGVECTOR_DSN database does not install pgvector")
        pgvector_psycopg2.register_vector(connection)
        with connection.cursor() as cursor:
            cursor.execute(
                "CREATE TEMP TABLE respan_pgvector_psycopg2_example ("
                "label text, embedding vector(3))"
            )
            cursor.execute(
                "INSERT INTO respan_pgvector_psycopg2_example VALUES (%s, %s)",
                ("psycopg2-live", [0.7, 0.8, 0.9]),
            )
            cursor.execute(
                "SELECT label, embedding FROM respan_pgvector_psycopg2_example "
                "ORDER BY embedding <-> %s LIMIT %s",
                (query_vector, limit),
            )
            row = cursor.fetchone()
        return {"registered": True, "row": _bounded_row(row)}
    finally:
        try:
            connection.rollback()
        finally:
            connection.close()


@workflow(name=WORKFLOW_NAME)
async def run_live_postgres(query_vector: list[float], limit: int) -> dict:
    return {
        "psycopg3_sync": _sync_path(query_vector, limit),
        "psycopg3_async": await _async_path(query_vector, limit),
        "psycopg2_registration": _psycopg2_path(query_vector, limit),
    }


async def run() -> None:
    global LIVE_DSN
    load_repo_env()
    dsn = os.getenv("PGVECTOR_DSN", "").strip()
    if not dsn:
        print("SKIP: PGVECTOR_DSN is not configured")
        return
    LIVE_DSN = dsn
    marker = run_id()
    respan = create_respan(WORKFLOW_NAME, marker)
    try:
        with Respan.propagate_attributes(**workflow_attributes(WORKFLOW_NAME, marker)):
            result = await run_live_postgres([0.1, 0.2, 0.3], 1)
        print_result(WORKFLOW_NAME, result, marker)
    finally:
        finish_respan(respan)


if __name__ == "__main__":
    asyncio.run(run())
