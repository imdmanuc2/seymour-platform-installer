from __future__ import annotations

from typing import Any

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
        operation["status"] = "running"
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
                step["status"] = "failed"
                step["message"] = (
                    f"Plugin {step_key} does not support "
                    f"adapter {operation['adapter']}"
                )
                operation["status"] = "failed"
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
                operation["status"] = "failed"
                self.store.save_operation(operation)
                break

        if operation["status"] != "failed":
            operation["status"] = "simulated"

        self.store.save_operation(operation)

        self.store.append_evidence(
            operation["operationId"],
            event_type="operation-completed",
            message=(
                "Plugin-based dry-run execution completed "
                f"with status {operation['status']}"
            ),
            details={
                "changesApplied": False,
                "status": operation["status"],
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
