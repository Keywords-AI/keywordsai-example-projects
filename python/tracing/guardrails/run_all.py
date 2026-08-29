"""Run the complete Guardrails tracing example set."""

from importlib import import_module


def main() -> None:
    for module_name, function_name in (
        ("01_pydantic_parse", "run_pydantic_parse"),
        ("02_gateway_structured_generation", "run_gateway_structured_generation"),
        ("03_propagated_attributes", "run_propagated_attributes"),
    ):
        getattr(import_module(module_name), function_name)()


if __name__ == "__main__":
    main()
