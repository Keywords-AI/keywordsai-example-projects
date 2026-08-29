"""A two-step content workflow around traced OpenAI Chat calls."""

from respan import task, workflow

from _shared import (
    example_attributes,
    finish_respan,
    make_respan,
    make_sync_client,
    model_name,
    print_result,
)

EXAMPLE = "decorators"
respan = make_respan(EXAMPLE)


@task(name="generate_outline")
def generate_outline(topic: str) -> str:
    response = client.chat.completions.create(
        model=model_name(), messages=[{"role": "user", "content": topic}]
    )
    return response.choices[0].message.content or ""


@task(name="write_draft")
def write_draft(outline: str) -> str:
    response = client.chat.completions.create(
        model=model_name(), messages=[{"role": "user", "content": outline}]
    )
    return response.choices[0].message.content or ""


@workflow(name="openai_content_pipeline")
def run(topic: str) -> str:
    return write_draft(generate_outline(topic))


try:
    client = make_sync_client()
    try:
        with example_attributes(EXAMPLE):
            print_result(EXAMPLE, run("Benefits of open-source software"))
    finally:
        client.close()
finally:
    finish_respan(respan)
