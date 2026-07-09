import litellm
from respan import workflow

from _shared import (
    GATEWAY_API_KEY,
    GATEWAY_BASE_URL,
    MODEL,
    create_respan,
    run_with_example_attributes,
)

WORKFLOW_NAME = "litellm_streaming_completion.workflow"


def _chunk_text(chunk) -> str:
    choices = getattr(chunk, "choices", None) or []
    if not choices:
        return ""
    delta = getattr(choices[0], "delta", None)
    content = getattr(delta, "content", None)
    return content or ""


@workflow(name=WORKFLOW_NAME)
def litellm_streaming_completion() -> str:
    stream = litellm.completion(
        api_key=GATEWAY_API_KEY,
        api_base=GATEWAY_BASE_URL,
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": "Write a six-word status update about tracing LiteLLM.",
            }
        ],
        stream=True,
        stream_options={"include_usage": True},
        temperature=0.1,
        max_tokens=40,
    )
    text = "".join(_chunk_text(chunk) for chunk in stream)
    return text.strip()


def main() -> None:
    respan = create_respan("litellm-streaming-completion")
    output = run_with_example_attributes(
        respan,
        workflow_name=WORKFLOW_NAME,
        action=litellm_streaming_completion,
    )
    print(output)
if __name__ == "__main__":
    main()
