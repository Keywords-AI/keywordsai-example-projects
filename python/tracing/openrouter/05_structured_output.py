"""OpenRouter structured JSON output."""

from __future__ import annotations

import json

from _shared import make_client, make_respan
from respan import workflow

respan = make_respan()
client, model = make_client()


@workflow(name="openrouter_structured_output")
def run(topic: str) -> dict[str, object]:
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "Return only valid JSON with keys title, difficulty, and "
                    "steps. steps must be an array of three short strings."
                ),
            },
            {"role": "user", "content": f"Create a mini plan for: {topic}"},
        ],
        response_format={"type": "json_object"},
    )
    content = response.choices[0].message.content or "{}"
    parsed = json.loads(content)
    print(json.dumps(parsed, indent=2))
    return parsed


try:
    run("observability for OpenRouter apps")
finally:
    respan.shutdown()
