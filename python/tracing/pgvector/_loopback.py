"""Deterministic psycopg/pgvector loopback used by committed examples."""

from __future__ import annotations

import sys
from types import ModuleType, SimpleNamespace
from typing import Any


class LoopbackDatabaseError(RuntimeError):
    """Predictable local database error for failure-span validation."""


class Cursor:
    rowcount = 2
    statusmessage = "SELECT 2"
    rownumber = 0
    description = None

    def __init__(self, rows: list[Any] | None = None) -> None:
        self._rows = rows or [
            ("python", [1.0, 0.0, 0.0], 0.0),
            ("rust", [0.9, 0.1, 0.0], 0.1414),
        ]
        self.closed = False

    def execute(self, query: str, params: Any = None):
        if "BROKEN" in query:
            raise LoopbackDatabaseError("deterministic vector query failure")
        self.statusmessage = query.lstrip().split(maxsplit=1)[0].upper()
        return self

    def executemany(self, query: str, params_seq: Any):
        if "BROKEN" in query:
            raise LoopbackDatabaseError("deterministic bulk vector failure")
        self.rowcount = sum(1 for _ in params_seq)
        self.statusmessage = f"INSERT {self.rowcount}"

    def fetchall(self) -> list[Any]:
        self.rownumber = len(self._rows)
        return list(self._rows)

    def fetchmany(self, size: int = 1) -> list[Any]:
        rows = self._rows[:size]
        self.rownumber += len(rows)
        return list(rows)

    def fetchone(self) -> Any:
        self.rownumber += 1
        return self._rows[0] if self._rows else None

    def close(self) -> None:
        self.closed = True

    def __enter__(self):
        return self

    def __exit__(self, *_exc_info) -> None:
        self.close()


class ServerCursor(Cursor):
    pass


class Connection:
    def __init__(self, rows: list[Any] | None = None) -> None:
        self._rows = rows
        self.closed = False
        self.vector_registered = False

    def __repr__(self) -> str:
        return (
            "<Connection postgresql://loopback:do-not-export@localhost/private "
            "at 0x1234abcd>"
        )

    def execute(self, query: str, params: Any = None) -> Cursor:
        return Cursor(self._rows).execute(query, params)

    def cursor(self, name: str | None = None):
        cursor_type = ServerCursor if name else Cursor
        return cursor_type(self._rows)

    def rollback(self) -> None:
        return None

    def close(self) -> None:
        self.closed = True


class AsyncCursor(Cursor):
    async def execute(self, query: str, params: Any = None):
        return super().execute(query, params)

    async def executemany(self, query: str, params_seq: Any):
        return super().executemany(query, params_seq)

    async def fetchall(self) -> list[Any]:
        return super().fetchall()

    async def fetchmany(self, size: int = 1) -> list[Any]:
        return super().fetchmany(size)

    async def fetchone(self) -> Any:
        return super().fetchone()

    async def close(self) -> None:
        self.closed = True

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_exc_info) -> None:
        await self.close()


class AsyncServerCursor(AsyncCursor):
    pass


class AsyncConnection(Connection):
    async def execute(self, query: str, params: Any = None) -> AsyncCursor:
        return await AsyncCursor(self._rows).execute(query, params)

    def cursor(self, name: str | None = None):
        cursor_type = AsyncServerCursor if name else AsyncCursor
        return cursor_type(self._rows)

    async def rollback(self) -> None:
        return None

    async def close(self) -> None:
        self.closed = True


def _register_vector(connection: Connection) -> None:
    connection.vector_registered = True


async def _register_vector_async(connection: AsyncConnection) -> None:
    connection.vector_registered = True


def install_loopback() -> SimpleNamespace:
    """Install process-local SDK-shaped modules before instrumentation activates."""
    psycopg = ModuleType("psycopg")
    psycopg.Connection = Connection
    psycopg.Cursor = Cursor
    psycopg.ServerCursor = ServerCursor
    psycopg.AsyncConnection = AsyncConnection
    psycopg.AsyncCursor = AsyncCursor
    psycopg.AsyncServerCursor = AsyncServerCursor

    pgvector_psycopg = ModuleType("pgvector.psycopg")
    pgvector_psycopg.register_vector = _register_vector
    pgvector_psycopg.register_vector_async = _register_vector_async

    pgvector_psycopg2 = ModuleType("pgvector.psycopg2")
    pgvector_psycopg2.register_vector = _register_vector

    sys.modules["psycopg"] = psycopg
    sys.modules["pgvector.psycopg"] = pgvector_psycopg
    sys.modules["pgvector.psycopg2"] = pgvector_psycopg2
    return SimpleNamespace(
        psycopg=psycopg,
        pgvector_psycopg=pgvector_psycopg,
        pgvector_psycopg2=pgvector_psycopg2,
    )
