"""Trace Arize experiment, prompt, and evaluator operations with Respan.

Run:
    python 03_experiments_prompts_evaluators.py
"""

from __future__ import annotations

from arize._generated.api_client import models
from arize.experiments.types import ExperimentTaskFieldNames

from _shared import (
    create_arize_client,
    create_respan,
    flush_and_shutdown,
    install_offline_arize_operations,
    new_run_id,
    print_result,
    print_trace_lookup,
    workflow_context,
)

WORKFLOW_NAME = "Arize Experiment Prompt Evaluator Workflow"
EXAMPLE_NAME = "03_experiments_prompts_evaluators"


def _prompt_messages() -> list[models.LLMMessage]:
    return [models.LLMMessage(role=models.MessageRole.USER, content="Score {{output}}")]


def _template_config() -> models.TemplateConfig:
    invocation_params = models.InvocationParams(temperature=0)
    provider_params = models.ProviderParams()
    llm_config = models.EvaluatorLlmConfig(
        ai_integration_id="ai-integration-offline",
        model_name="gpt-4o-mini",
        invocation_parameters=invocation_params,
        provider_parameters=provider_params,
    )
    return models.TemplateConfig(
        name="offline-template",
        template="score {{output}}",
        include_explanations=True,
        use_function_calling_if_available=False,
        llm_config=llm_config,
    )


def _code_config() -> models.CustomCodeConfig:
    return models.CustomCodeConfig(
        type="CUSTOM",
        name="offline-code",
        code="def evaluate(row): return 1",
        variables=[],
    )


def run_experiment_prompt_evaluator_operations() -> str:
    run_id = new_run_id(EXAMPLE_NAME)
    install_offline_arize_operations()
    respan = create_respan(
        workflow_name=WORKFLOW_NAME,
        run_id=run_id,
        example_name=EXAMPLE_NAME,
    )
    client = create_arize_client()
    experiment_runs = [{"example_id": "example-1", "output": "offline output"}]
    task_fields = ExperimentTaskFieldNames(example_id="example_id", output="output")

    with workflow_context(
        respan,
        workflow_name=WORKFLOW_NAME,
        run_id=run_id,
        example_name=EXAMPLE_NAME,
    ):
        print_result("experiments.list", client.experiments.list(space="space-offline"))
        print_result(
            "experiments.create",
            client.experiments.create(
                name="offline-experiment",
                dataset="offline-dataset",
                space="space-offline",
                experiment_runs=experiment_runs,
                task_fields=task_fields,
            ),
        )
        print_result("experiments.get", client.experiments.get(experiment="offline-experiment", space="space-offline"))
        print_result("experiments.list_runs", client.experiments.list_runs(experiment="offline-experiment", space="space-offline"))
        print_result(
            "experiments.append_runs",
            client.experiments.append_runs(
                experiment="offline-experiment",
                space="space-offline",
                experiment_runs=experiment_runs,
            ),
        )
        print_result("experiments.annotate_runs", client.experiments.annotate_runs(experiment="offline-experiment", space="space-offline", annotations=[]))
        print_result(
            "experiments.run",
            client.experiments.run(
                name="offline-experiment-run",
                dataset="offline-dataset",
                task=lambda example: example,
                evaluators=[],
                space="space-offline",
                dry_run=True,
            ),
        )
        print_result("experiments.delete", client.experiments.delete(experiment="offline-experiment", space="space-offline"))
        print_result("prompts.list", client.prompts.list(space="space-offline"))
        print_result(
            "prompts.create",
            client.prompts.create(
                name="offline-prompt",
                messages=_prompt_messages(),
                space="space-offline",
                commit_message="initial offline prompt",
                input_variable_format=models.InputVariableFormat.MUSTACHE,
                provider=models.LlmProvider.OPEN_AI,
            ),
        )
        print_result("prompts.get", client.prompts.get(prompt="offline-prompt", space="space-offline"))
        print_result("prompts.get_version", client.prompts.get_version(version_id="version-offline"))
        print_result("prompts.update", client.prompts.update(prompt="offline-prompt", space="space-offline", description="Renamed offline prompt"))
        print_result("prompts.list_versions", client.prompts.list_versions(prompt="offline-prompt", space="space-offline"))
        print_result(
            "prompts.create_version",
            client.prompts.create_version(
                prompt="offline-prompt",
                space="space-offline",
                messages=_prompt_messages(),
                commit_message="offline prompt update",
                input_variable_format=models.InputVariableFormat.MUSTACHE,
                provider=models.LlmProvider.OPEN_AI,
            ),
        )
        print_result(
            "prompts.get_version_by_label",
            client.prompts.get_version_by_label(prompt="offline-prompt", label_name="production", space="space-offline"),
        )
        print_result("prompts.set_labels", client.prompts.set_labels(version_id="version-offline", labels=["production"]))
        print_result("prompts.delete_label", client.prompts.delete_label(version_id="version-offline", label_name="production"))
        print_result("prompts.delete", client.prompts.delete(prompt="offline-prompt", space="space-offline"))
        print_result("evaluators.list", client.evaluators.list(space="space-offline"))
        print_result(
            "evaluators.create_template_evaluator",
            client.evaluators.create_template_evaluator(
                name="offline-template",
                template_config=_template_config(),
                space="space-offline",
                commit_message="initial template evaluator",
            ),
        )
        print_result(
            "evaluators.create_code_evaluator",
            client.evaluators.create_code_evaluator(
                name="offline-code",
                code_config=_code_config(),
                space="space-offline",
                commit_message="initial code evaluator",
            ),
        )
        print_result("evaluators.get", client.evaluators.get(evaluator="offline-evaluator", space="space-offline"))
        print_result("evaluators.update", client.evaluators.update(evaluator="offline-evaluator", space="space-offline", name="renamed-evaluator"))
        print_result("evaluators.list_versions", client.evaluators.list_versions(evaluator="offline-evaluator", space="space-offline"))
        print_result("evaluators.get_version", client.evaluators.get_version(version_id="evaluator-version"))
        print_result(
            "evaluators.create_template_version",
            client.evaluators.create_template_version(
                evaluator="offline-evaluator",
                template_config=_template_config(),
                space="space-offline",
                commit_message="template evaluator update",
            ),
        )
        print_result(
            "evaluators.create_code_version",
            client.evaluators.create_code_version(
                evaluator="offline-evaluator",
                code_config=_code_config(),
                space="space-offline",
                commit_message="code evaluator update",
            ),
        )
        print_result("evaluators.delete", client.evaluators.delete(evaluator="offline-evaluator", space="space-offline"))

    flush_and_shutdown(respan)
    print_trace_lookup(workflow_name=WORKFLOW_NAME, run_id=run_id)
    return run_id


if __name__ == "__main__":
    run_experiment_prompt_evaluator_operations()
