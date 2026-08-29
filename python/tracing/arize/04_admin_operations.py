"""Trace Arize admin and configuration operations with Respan.

Run:
    python 04_admin_operations.py
"""

from __future__ import annotations

from arize._generated.api_client import models
from arize.api_keys.types import OrgBinding, SpaceBinding

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

WORKFLOW_NAME = "Arize Admin Operations Workflow"
EXAMPLE_NAME = "04_admin_operations"


def _run_configuration() -> models.TemplateEvaluationRunConfig:
    return models.TemplateEvaluationRunConfig(
        experiment_type="TEMPLATE_EVALUATION",
        ai_integration_id="ai-integration-offline",
        model_name="gpt-4o-mini",
        template="score {{output}}",
        provide_explanation=True,
    )


def run_admin_operations() -> str:
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
        print_result("ai_integrations.list", client.ai_integrations.list(space="space-offline"))
        print_result("ai_integrations.create", client.ai_integrations.create(name="offline-integration", provider=models.AiIntegrationProvider.OPEN_AI))
        print_result("ai_integrations.get", client.ai_integrations.get(integration="offline-integration", space="space-offline"))
        print_result("ai_integrations.update", client.ai_integrations.update(integration="offline-integration", space="space-offline", name="renamed-integration"))
        print_result("ai_integrations.delete", client.ai_integrations.delete(integration="offline-integration", space="space-offline"))
        print_result("annotation_configs.list", client.annotation_configs.list(space="space-offline"))
        print_result("annotation_configs.get", client.annotation_configs.get(annotation_config="quality", space="space-offline"))
        print_result("annotation_configs.delete", client.annotation_configs.delete(annotation_config="quality", space="space-offline"))
        print_result("annotation_queues.list", client.annotation_queues.list(space="space-offline"))
        print_result(
            "annotation_queues.create",
            client.annotation_queues.create(
                name="offline-queue",
                space="space-offline",
                annotation_config_ids=["quality"],
                annotator_emails=["annotator@example.com"],
            ),
        )
        print_result("annotation_queues.get", client.annotation_queues.get(annotation_queue="offline-queue", space="space-offline"))
        print_result("annotation_queues.update", client.annotation_queues.update(annotation_queue="offline-queue", space="space-offline", name="renamed-queue"))
        print_result("annotation_queues.list_records", client.annotation_queues.list_records(annotation_queue="offline-queue", space="space-offline"))
        print_result(
            "annotation_queues.add_records",
            client.annotation_queues.add_records(
                annotation_queue="offline-queue",
                space="space-offline",
                record_sources=[],
            ),
        )
        print_result(
            "annotation_queues.annotate_record",
            client.annotation_queues.annotate_record(
                annotation_queue="offline-queue",
                space="space-offline",
                record_id="record-offline",
                annotations=[],
            ),
        )
        print_result(
            "annotation_queues.assign_record",
            client.annotation_queues.assign_record(
                annotation_queue="offline-queue",
                space="space-offline",
                record_id="record-offline",
                assigned_user_emails=["annotator@example.com"],
            ),
        )
        print_result(
            "annotation_queues.delete_records",
            client.annotation_queues.delete_records(
                annotation_queue="offline-queue",
                record_ids=["record-offline"],
                space="space-offline",
            ),
        )
        print_result("annotation_queues.delete", client.annotation_queues.delete(annotation_queue="offline-queue", space="space-offline"))
        print_result("tasks.list", client.tasks.list(space="space-offline"))
        print_result(
            "tasks.create_evaluation_task",
            client.tasks.create_evaluation_task(
                name="offline-eval-task",
                task_type=models.TaskType.CODE_EVALUATION,
                space="space-offline",
                evaluators=[],
            ),
        )
        print_result(
            "tasks.create_run_experiment_task",
            client.tasks.create_run_experiment_task(
                name="offline-run-task",
                space="space-offline",
                dataset="offline-dataset",
                run_configuration=_run_configuration(),
            ),
        )
        print_result("tasks.get", client.tasks.get(task="offline-task", space="space-offline"))
        print_result("tasks.update", client.tasks.update(task="offline-task", space="space-offline", name="renamed-task"))
        print_result("tasks.trigger_run", client.tasks.trigger_run(task="offline-task", space="space-offline"))
        print_result("tasks.list_runs", client.tasks.list_runs(task="offline-task", space="space-offline"))
        print_result("tasks.get_run", client.tasks.get_run(run_id="run-offline"))
        print_result("tasks.cancel_run", client.tasks.cancel_run(run_id="run-offline"))
        print_result("tasks.wait_for_run", client.tasks.wait_for_run(run_id="run-offline"))
        print_result("tasks.delete", client.tasks.delete(task="offline-task", space="space-offline"))
        print_result("users.list", client.users.list())
        print_result(
            "users.create",
            client.users.create(
                email="person@example.com",
                name="Person",
                role=models.UserRole.MEMBER,
                invite_mode=models.InviteMode.NONE,
            ),
        )
        print_result("users.get", client.users.get(user="person@example.com"))
        print_result("users.update", client.users.update(user_id="user-offline", name="Renamed Person"))
        print_result("users.resend_invitation", client.users.resend_invitation(user_id="user-offline"))
        print_result("users.reset_password", client.users.reset_password(user_id="user-offline"))
        print_result("users.bulk_delete", client.users.bulk_delete(user_ids=["user-offline"]))
        print_result("users.delete", client.users.delete(user_id="user-offline"))
        print_result("organizations.list", client.organizations.list())
        print_result("organizations.create", client.organizations.create(name="offline-org"))
        print_result("organizations.get", client.organizations.get(organization="offline-org"))
        print_result("organizations.update", client.organizations.update(organization="offline-org", name="renamed-org"))
        print_result(
            "organizations.add_user",
            client.organizations.add_user(
                organization="offline-org",
                user_id="user-offline",
                role=models.OrganizationRole.MEMBER,
            ),
        )
        print_result("organizations.remove_user", client.organizations.remove_user(organization="offline-org", user_id="user-offline"))
        print_result("organizations.delete", client.organizations.delete(organization="offline-org"))
        print_result("api_keys.list", client.api_keys.list())
        print_result("api_keys.create", client.api_keys.create(name="offline-key"))
        print_result(
            "api_keys.create_service_key",
            client.api_keys.create_service_key(
                name="offline-service-key",
                orgs=[
                    OrgBinding(
                        org_id="org-offline",
                        spaces=[SpaceBinding(space="space-offline")],
                    )
                ],
            ),
        )
        print_result("api_keys.refresh", client.api_keys.refresh(api_key_id="key-offline"))
        print_result("api_keys.revoke", client.api_keys.revoke(api_key_id="key-offline"))
        print_result("roles.list", client.roles.list())
        print_result("roles.create", client.roles.create(name="offline-role", permissions=[]))
        print_result("roles.get", client.roles.get(role="offline-role"))
        print_result("roles.update", client.roles.update(role="offline-role", name="renamed-role"))
        print_result("roles.delete", client.roles.delete(role="offline-role"))
        print_result("role_bindings.list", client.role_bindings.list(resource_type=models.RoleBindingResourceType.SPACE))
        print_result(
            "role_bindings.create",
            client.role_bindings.create(
                user_id="user-offline",
                role_id="role-offline",
                resource_type=models.RoleBindingResourceType.SPACE,
                resource_id="space-offline",
            ),
        )
        print_result("role_bindings.get", client.role_bindings.get(binding_id="binding-offline"))
        print_result("role_bindings.update", client.role_bindings.update(binding_id="binding-offline", role_id="role-offline"))
        print_result("role_bindings.delete", client.role_bindings.delete(binding_id="binding-offline"))
        print_result("resource_restrictions.restrict", client.resource_restrictions.restrict(resource_id="resource-offline"))
        print_result("resource_restrictions.unrestrict", client.resource_restrictions.unrestrict(resource_id="resource-offline"))

    flush_and_shutdown(respan)
    print_trace_lookup(workflow_name=WORKFLOW_NAME, run_id=run_id)
    return run_id


if __name__ == "__main__":
    run_admin_operations()
