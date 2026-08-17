"""Chat, embedding, and precise provider-error tracing with the OpenAI SDK."""

from openai import AuthenticationError
from respan import workflow

from _shared import (
    FAILURE_SENTINEL,
    example_attributes,
    finish_respan,
    make_respan,
    make_sync_client,
    model_name,
    print_result,
)

EXAMPLE = "hello-world"
respan = make_respan(EXAMPLE)


@workflow(name="openai_hello_world")
def run() -> str:
    response = client.chat.completions.create(
        model=model_name(),
        messages=[{"role": "user", "content": "Say hello in three languages."}],
    )
    embedding = client.embeddings.create(
        model="text-embedding-3-small", input="observable OpenAI request"
    )
    try:
        client.chat.completions.create(
            model=model_name(),
            messages=[{"role": "user", "content": FAILURE_SENTINEL}],
        )
    except AuthenticationError as exc:
        if exc.status_code != 401:
            raise
    return f"{response.choices[0].message.content} embedding_dim={len(embedding.data[0].embedding)}"


try:
    client = make_sync_client()
    try:
        with example_attributes(EXAMPLE):
            print_result(EXAMPLE, run())
    finally:
        client.close()
finally:
    finish_respan(respan)
