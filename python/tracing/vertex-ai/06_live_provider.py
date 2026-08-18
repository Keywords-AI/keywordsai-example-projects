from __future__ import annotations

import os

import vertexai
from _shared import (
    example_attributes,
    load_repo_env,
    make_respan,
    marker_for,
    model_name,
    workflow_name,
)
from respan import workflow
from vertexai.generative_models import GenerativeModel

EXAMPLE_NAME = "live-provider"


@workflow(name=workflow_name(EXAMPLE_NAME))
def live_provider(prompt: str) -> str:
    return GenerativeModel(model_name()).generate_content(prompt).text


def main() -> None:
    load_repo_env()
    required = ("GOOGLE_CLOUD_PROJECT", "GOOGLE_CLOUD_LOCATION")
    if not all(os.getenv(name) for name in required):
        print(
            "live Vertex AI skipped: GOOGLE_CLOUD_PROJECT/LOCATION absent", flush=True
        )
        return
    marker = marker_for(EXAMPLE_NAME)
    vertexai.init(
        project=os.environ["GOOGLE_CLOUD_PROJECT"],
        location=os.environ["GOOGLE_CLOUD_LOCATION"],
    )
    respan = make_respan(EXAMPLE_NAME, marker)
    try:
        with example_attributes(EXAMPLE_NAME, marker):
            result = live_provider("Reply exactly: live Vertex verified")
    finally:
        respan.shutdown()
    print({"example": EXAMPLE_NAME, "marker": marker, "result": result}, flush=True)


if __name__ == "__main__":
    main()
