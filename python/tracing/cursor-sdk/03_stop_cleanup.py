from __future__ import annotations

import json

from _shared import (
    example_attributes,
    make_custom_identifier,
    make_event,
    make_respan,
    print_start,
    state_path,
)

EXAMPLE_NAME = "stop-cleanup"


def main() -> None:
    run_id = make_custom_identifier(EXAMPLE_NAME)
    state_file = state_path(run_id)
    if state_file.exists():
        state_file.unlink()

    respan, instrumentor = make_respan(EXAMPLE_NAME, state_file)
    print_start(EXAMPLE_NAME, run_id)
    with example_attributes(EXAMPLE_NAME, run_id):
        for event in [
            make_event(
                EXAMPLE_NAME,
                run_id,
                "beforeSubmitPrompt",
                prompt="Start a refactor, then cancel the agent turn.",
            ),
            make_event(
                EXAMPLE_NAME,
                run_id,
                "afterAgentThought",
                text="I found the affected files and am preparing a minimal change.",
                duration_ms=300,
            ),
            make_event(EXAMPLE_NAME, run_id, "stop", status="cancelled", loop_count=1),
        ]:
            result = instrumentor.process_event(event)
            print(
                f"event={result.event_name} emitted={result.emitted} span={result.span_name}",
                flush=True,
            )

    state = json.loads(state_file.read_text()) if state_file.exists() else {}
    print(f"state_after_stop={state}", flush=True)


if __name__ == "__main__":
    main()
