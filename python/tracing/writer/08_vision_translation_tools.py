from __future__ import annotations

from _shared import (
    close_client,
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
from respan import workflow

EXAMPLE_NAME = "vision-translation-tools"
_CLIENT = None


@workflow(name=workflow_name(EXAMPLE_NAME))
def _vision_translation_tools_workflow(text: str) -> dict[str, str]:
    vision = _CLIENT.vision.analyze(
        model=vision_model_name(),
        prompt="Describe the file {{example_file}} in one sentence.",
        variables=[{"name": "example_file", "file_id": file_id()}],
    )
    translation = _CLIENT.translation.translate(
        model=translation_model_name(),
        text=text,
        source_language_code="en",
        target_language_code="fr",
        formality=False,
        length_control=False,
        mask_profanity=False,
    )
    web = _CLIENT.tools.web_search(
        query="Respan tracing instrumentation",
        include_answer=True,
        max_results=1,
    )
    pdf = _CLIENT.tools.parse_pdf(file_id(), format="markdown")
    return {
        "vision": vision.data,
        "translation": translation.data,
        "web_search": web.answer or "",
        "parse_pdf": pdf.content[:120],
    }


def run() -> dict[str, str]:
    global _CLIENT
    respan = make_respan(EXAMPLE_NAME)
    client = make_client()
    _CLIENT = client
    custom_identifier = make_custom_identifier(EXAMPLE_NAME)
    result: dict[str, str] = {}
    try:
        with example_attributes(EXAMPLE_NAME, custom_identifier):
            print_start(EXAMPLE_NAME, custom_identifier)
            result = _vision_translation_tools_workflow("Hello from Writer tracing.")
    finally:
        try:
            close_client(client)
        finally:
            finish_respan(respan)
    print_result("vision translation tools", result)
    return result


if __name__ == "__main__":
    run()
