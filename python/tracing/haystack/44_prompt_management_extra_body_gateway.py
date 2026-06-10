"""Use Respan prompt management from Haystack via ``extra_body``.

Haystack's ``OpenAIChatGenerator`` accepts OpenAI SDK keyword arguments through
``generation_kwargs``. Put Respan prompt management config under
``generation_kwargs.extra_body.prompt`` so the Respan gateway resolves the
managed prompt at request time.

This example uses the Respan gateway for the LLM call too. ``configure_respan``
sets ``OPENAI_API_KEY`` to ``RESPAN_API_KEY`` and points ``OPENAI_BASE_URL`` at
the Respan OpenAI-compatible gateway, so no OpenAI provider key is required when
the Respan key has credits or managed gateway access.
"""

from __future__ import annotations

import json
import os
from typing import Any

from dotenv import find_dotenv, load_dotenv

from _shared import configure_respan, finish_respan, print_result


def _prompt_variables() -> dict[str, Any]:
    variables_json = os.getenv("RESPAN_PROMPT_VARIABLES_JSON")
    if variables_json:
        try:
            variables = json.loads(variables_json)
        except json.JSONDecodeError as exc:
            raise RuntimeError(
                "RESPAN_PROMPT_VARIABLES_JSON must be valid JSON."
            ) from exc
        if not isinstance(variables, dict):
            raise RuntimeError("RESPAN_PROMPT_VARIABLES_JSON must decode to an object.")
        return variables

    return {
        "question": os.getenv("RESPAN_PROMPT_QUESTION", "Who created Python?"),
        "context": os.getenv(
            "RESPAN_PROMPT_CONTEXT",
            "Python was created by Guido van Rossum and first released in 1991.",
        ),
    }


def _schema_version() -> int:
    value = os.getenv("RESPAN_PROMPT_SCHEMA_VERSION", "2")
    try:
        return int(value)
    except ValueError as exc:
        raise RuntimeError("RESPAN_PROMPT_SCHEMA_VERSION must be an integer.") from exc


def _haystack_required_message(prompt_variables: dict[str, Any]) -> str:
    for key in ("customer_inquiry", "question", "user_query"):
        value = prompt_variables.get(key)
        if isinstance(value, str) and value:
            return value
    return "Run the managed Respan prompt."


def run_prompt_management_extra_body_gateway_example() -> dict[str, Any]:
    load_dotenv(find_dotenv(), override=False)

    prompt_id = os.getenv("RESPAN_PROMPT_ID")
    if not prompt_id:
        raise RuntimeError(
            "Set RESPAN_PROMPT_ID to a deployed Respan prompt before running "
            "the extra_body prompt management example."
        )

    prompt_variables = _prompt_variables()
    prompt_config = {
        "prompt_id": prompt_id,
        "schema_version": _schema_version(),
        "variables": prompt_variables,
        "override": True,
    }

    respan = configure_respan(
        "haystack-prompt-management-extra-body-gateway",
        use_gateway=True,
    )
    try:
        from haystack import Pipeline
        from haystack.components.generators.chat import OpenAIChatGenerator
        from haystack.dataclasses import ChatMessage

        pipeline = Pipeline()
        pipeline.add_component(
            "managed_prompt_llm",
            OpenAIChatGenerator(model=os.getenv("RESPAN_MODEL", "gpt-4o")),
        )

        with respan.propagate_attributes(prompt=prompt_config):
            result = pipeline.run(
                {
                    "managed_prompt_llm": {
                        # Haystack requires at least one message to call the
                        # OpenAI-compatible generator. The Respan gateway reads
                        # extra_body.prompt and overrides this placeholder.
                        "messages": [
                            ChatMessage.from_user(
                                _haystack_required_message(prompt_variables)
                            )
                        ],
                        "generation_kwargs": {
                            "temperature": 0.0,
                            "extra_body": {
                                "prompt": prompt_config,
                            },
                        },
                    }
                }
            )

        print_result("Respan prompt management via extra_body", result)
        return result
    finally:
        finish_respan(respan)


if __name__ == "__main__":
    run_prompt_management_extra_body_gateway_example()
