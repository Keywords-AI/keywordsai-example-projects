from _shared import (
    create_respan,
    finish_respan,
    marqo_client,
    print_result,
    unique_index_name,
    workflow_attributes,
)
from marqo.errors import MarqoWebError
from respan import Respan, workflow

WORKFLOW_NAME = "marqo_service_error_workflow"


@workflow(name=WORKFLOW_NAME)
def run_service_error() -> None:
    with marqo_client(force_loopback=True) as client:
        client.index(unique_index_name()).health()


def main() -> None:
    respan = create_respan(WORKFLOW_NAME)
    try:
        try:
            with Respan.propagate_attributes(**workflow_attributes(WORKFLOW_NAME)):
                run_service_error()
        except MarqoWebError as exc:
            print_result(
                WORKFLOW_NAME,
                {"error": type(exc).__name__, "message": str(exc)},
            )
        else:
            raise AssertionError("the loopback Marqo health probe should fail")
    finally:
        finish_respan(respan)


if __name__ == "__main__":
    main()
