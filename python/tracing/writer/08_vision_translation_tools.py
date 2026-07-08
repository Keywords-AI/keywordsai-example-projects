from __future__ import annotations

from respan import workflow

from _shared import (
    example_attributes,
    file_id,
    finish_respan,
    make_client,
    make_custom_identifier,
    make_respan,
    print_result,
    print_start,
    translation_model_name,
    vision_model_name,
    workflow_name,
)

EXAMPLE_NAME = "vision-translation-tools"


@workflow(name=workflow_name(EXAMPLE_NAME))
def _vision_translation_tools_workflow(client) -> dict[str, str]:
    vision = client.vision.analyze(
        model=vision_model_name(),
        prompt="Describe the file {{example_file}} in one sentence.",
        variables=[{"name": "example_file", "file_id": file_id()}],
    )
    translation = client.translation.translate(
        model=translation_model_name(),
        text="Hello from Writer tracing.",
        source_language_code="en",
        target_language_code="fr",
        formality=False,
        length_control=False,
        mask_profanity=False,
    )
    web = client.tools.web_search(
        query="Respan tracing instrumentation",
        include_answer=True,
        max_results=1,
    )
    pdf = client.tools.parse_pdf(file_id(), format="markdown")
    return {
        "vision": vision.data,
        "translation": translation.data,
        "web_search": web.answer or "",
        "parse_pdf": pdf.content[:120],
    }


def run() -> dict[str, str]:
    respan = make_respan(EXAMPLE_NAME)
    client = make_client()
    custom_identifier = make_custom_identifier(EXAMPLE_NAME)
    result: dict[str, str] = {}
    try:
        with example_attributes(EXAMPLE_NAME, custom_identifier):
            print_start(EXAMPLE_NAME, custom_identifier)
            result = _vision_translation_tools_workflow(client)
    finally:
        finish_respan(respan)
    print_result("vision translation tools", result)
    return result


if __name__ == "__main__":
    run()
