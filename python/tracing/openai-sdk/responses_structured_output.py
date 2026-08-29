"""Responses.parse structured output on the real OpenAI 3.x parse path."""

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

EXAMPLE = "responses-structured-output"
respan = make_respan(EXAMPLE)


class MovieReview(BaseModel):
    title: str
    rating: int
    summary: str
    pros: list[str]
    cons: list[str]


@workflow(name="openai_responses_movie_review")
def run(movie: str) -> MovieReview:
    response = client.responses.parse(
        model=model_name(), input=f"Review: {movie}", text_format=MovieReview
    )
    return response.output_parsed


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
