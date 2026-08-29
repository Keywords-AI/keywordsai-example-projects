"""Trace Arize dataset, project, and space operations with Respan.

Run:
    python 02_datasets_projects_spaces.py
"""

from __future__ import annotations

from arize._generated.api_client import models

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

WORKFLOW_NAME = "Arize Dataset Project Space Workflow"
EXAMPLE_NAME = "02_datasets_projects_spaces"


def run_dataset_project_space_operations() -> str:
    run_id = new_run_id(EXAMPLE_NAME)
    install_offline_arize_operations()
    respan = create_respan(
        workflow_name=WORKFLOW_NAME,
        run_id=run_id,
        example_name=EXAMPLE_NAME,
    )
    client = create_arize_client()

    with workflow_context(
        respan,
        workflow_name=WORKFLOW_NAME,
        run_id=run_id,
        example_name=EXAMPLE_NAME,
    ):
        examples = [{"query": "hello", "response": "world"}]
        print_result("datasets.list", client.datasets.list(space="space-offline"))
        print_result("datasets.create", client.datasets.create(name="offline-dataset", space="space-offline", examples=examples))
        print_result("datasets.get", client.datasets.get(dataset="offline-dataset", space="space-offline"))
        try:
            client.datasets.get(
                dataset="missing-dataset",
                space="space-offline",
                _respan_force_error=True,
            )
        except RuntimeError as error:
            print(f"datasets.get expected error: {error}")
        print_result("datasets.update", client.datasets.update(dataset="offline-dataset", name="renamed-dataset", space="space-offline"))
        print_result("datasets.list_examples", client.datasets.list_examples(dataset="offline-dataset", space="space-offline"))
        print_result("datasets.append_examples", client.datasets.append_examples(dataset="offline-dataset", space="space-offline", examples=examples))
        print_result("datasets.annotate_examples", client.datasets.annotate_examples(dataset="offline-dataset", space="space-offline", annotations=[]))
        print_result("datasets.delete", client.datasets.delete(dataset="offline-dataset", space="space-offline"))
        print_result("projects.list", client.projects.list(space="space-offline"))
        print_result("projects.create", client.projects.create(name="offline-project", space="space-offline"))
        print_result("projects.get", client.projects.get(project="offline-project", space="space-offline"))
        print_result("projects.update", client.projects.update(project="offline-project", space="space-offline", name="renamed-project"))
        print_result("projects.delete", client.projects.delete(project="offline-project", space="space-offline"))
        print_result("spaces.list", client.spaces.list(organization_id="organization-offline"))
        print_result("spaces.create", client.spaces.create(name="offline-space", organization_id="organization-offline"))
        print_result("spaces.get", client.spaces.get(space="offline-space"))
        print_result("spaces.update", client.spaces.update(space="offline-space", name="renamed-space"))
        print_result(
            "spaces.add_user",
            client.spaces.add_user(
                space="offline-space",
                user_id="user-offline",
                role=models.UserSpaceRole.MEMBER,
            ),
        )
        print_result("spaces.remove_user", client.spaces.remove_user(space="offline-space", user_id="user-offline"))
        print_result("spaces.delete", client.spaces.delete(space="offline-space"))

    flush_and_shutdown(respan)
    print_trace_lookup(workflow_name=WORKFLOW_NAME, run_id=run_id)
    return run_id


if __name__ == "__main__":
    run_dataset_project_space_operations()
