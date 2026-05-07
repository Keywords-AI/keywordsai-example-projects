"""Chat model with_structured_output."""

from pydantic import BaseModel, Field

from _shared import flush, init_telemetry, make_openai_chat_model, tracing_config


class Movie(BaseModel):
    """A movie with details."""

    title: str = Field(description="Movie title")
    year: int = Field(description="Release year")
    director: str = Field(description="Director name")


def model_with_structured_output() -> None:
    telemetry = init_telemetry("langchain-model-with-structured-output")
    try:
        model = make_openai_chat_model()
        if model is None:
            print("Set OPENAI_API_KEY or RESPAN_API_KEY to run this provider-backed example.")
            return

        structured_model = model.with_structured_output(Movie)
        response = structured_model.invoke(
            "Provide details for the movie Inception.",
            config=tracing_config("model_with_structured_output"),
        )
        print(response)
    finally:
        flush(telemetry)


if __name__ == "__main__":
    model_with_structured_output()
