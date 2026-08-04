from __future__ import annotations

from typing import Any

from lifecycle.operation import (
    mark_operation_completed,
    mark_operation_started,
)
from plugins.registry import PluginRegistry
from state.store import StateStore


class LifecycleExecutor:
    def __init__(
        self,
        store: StateStore,
        registry: PluginRegistry,
    ) -> None:
        self.store = store
        self.registry = registry

    def execute_dry_run(
        self,
        operation: dict[str, Any],
        *,
        manifest: dict[str, Any],
    ) -> dict[str, Any]:
        mark_operation_started(operation)
        self.store.save_operation(operation)

        self.store.append_evidence(
            operation["operationId"],
            event_type="operation-started",
            message="Plugin-based dry-run execution started",
        )

        context = {
            "operationId": operation["operationId"],
            "product": operation["product"],
            "adapter": operation["adapter"],
            "manifest": manifest,
        }

        failure_message: str | None = None

        for step in operation["steps"]:
            step_number = step["step"]
            step_key = step["key"]

            operation["currentStep"] = step_number
            step["status"] = "running"
            self.store.save_operation(operation)

            self.store.append_evidence(
                operation["operationId"],
                event_type="plugin-started",
                message=f"Executing plugin: {step_key}",
                details={
                    "step": step_number,
                    "plugin": step_key,
                },
            )

            plugin = self.registry.require(step_key)

            if not plugin.supports_adapter(operation["adapter"]):
                failure_message = (
                    f"Plugin {step_key} does not support "
                    f"adapter {operation['adapter']}"
                )
                step["status"] = "failed"
                step["message"] = failure_message
                self.store.save_operation(operation)
                break

            result = plugin.execute(
                context=context,
                dry_run=True,
            )

            step["status"] = result.status
            step["message"] = result.message
            step["pluginResult"] = result.to_dict()

            self.store.save_operation(operation)

            self.store.append_evidence(
                operation["operationId"],
                event_type="plugin-result",
                message=result.message,
                details={
                    "step": step_number,
                    "plugin": step_key,
                    "result": result.to_dict(),
                },
            )

            if not result.success:
                failure_message = result.message
                break

        if failure_message is not None:
            mark_operation_completed(
                operation,
                status="failed",
                success=False,
                changed=False,
                message=failure_message,
                details={
                    "changesApplied": False,
                    "failedStep": operation.get("currentStep"),
                },
            )
        else:
            mark_operation_completed(
                operation,
                status="simulated",
                success=True,
                changed=False,
                message="Plugin-based dry-run execution completed",
                details={
                    "changesApplied": False,
                },
            )

        self.store.save_operation(operation)

        self.store.append_evidence(
            operation["operationId"],
            event_type="operation-completed",
            message=operation["outcome"]["message"],
            details={
                "changesApplied": False,
                "status": operation["status"],
                "outcome": operation["outcome"],
                "durationMilliseconds": (
                    operation["durationMilliseconds"]
                ),
            },
        )

        return operation

    def resume_dry_run(
        self,
        operation: dict[str, Any],
        *,
        manifest: dict[str, Any],
    ) -> dict[str, Any]:
        if operation["status"] == "simulated":
            return operation

        return self.execute_dry_run(
            operation,
            manifest=manifest,
        )
