import asyncio
from builtins import ExceptionGroup

from _shared import (
    create_respan,
    finish_respan,
    print_result,
    with_session,
    workflow_attributes,
)
from respan import Respan, workflow

WORKFLOW_NAME = "mcp_connection_failure_workflow"


@workflow(name=WORKFLOW_NAME)
async def run_connection_failure_example() -> None:
    async with with_session(server_args=("--exit-immediately",)):
        raise AssertionError("The MCP server unexpectedly initialized")


async def main() -> None:
    respan = create_respan(WORKFLOW_NAME)
    try:
        with Respan.propagate_attributes(**workflow_attributes(WORKFLOW_NAME)):
            try:
                await run_connection_failure_example()
            except ExceptionGroup as exc:
                if "Connection closed" not in repr(exc):
                    raise
                print_result(
                    WORKFLOW_NAME,
                    {"expected_error": "Connection closed"},
                )
            else:
                raise AssertionError("The deliberate MCP failure did not occur")
    finally:
        finish_respan(respan)


if __name__ == "__main__":
    asyncio.run(main())
