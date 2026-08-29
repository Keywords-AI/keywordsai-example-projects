"""Chat Completions.parse structured output on OpenAI 3.x."""

from pydantic import BaseModel
from respan import workflow

from _shared import (
    example_attributes,
    finish_respan,
    make_respan,
    make_sync_client,
    model_name,
    print_result,
)

EXAMPLE = "structured-output"
respan = make_respan(EXAMPLE)


class MovieReview(BaseModel):
    title: str
    rating: int
    summary: str
    pros: list[str]
    cons: list[str]


@workflow(name="openai_chat_movie_review")
def run(movie: str) -> MovieReview:
    response = client.beta.chat.completions.parse(
        model=model_name(),
        messages=[{"role": "user", "content": f"Review: {movie}"}],
        response_format=MovieReview,
    )
    return response.choices[0].message.parsed


try:
    client = make_sync_client()
    try:
        with example_attributes(EXAMPLE):
            result = run("The Matrix")
            print_result(EXAMPLE, f"{result.title} rating={result.rating}")
    finally:
        client.close()
finally:
    finish_respan(respan)
