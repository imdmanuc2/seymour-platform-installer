from __future__ import annotations

from typing import Any

from state.store import StateStore


class LifecycleExecutor:
    def __init__(self, store: StateStore) -> None:
        self.store = store

    def execute_dry_run(
        self,
        operation: dict[str, Any],
    ) -> dict[str, Any]:
        operation["status"] = "running"
        self.store.save_operation(operation)

        self.store.append_evidence(
            operation["operationId"],
            event_type="operation-started",
            message="Dry-run lifecycle execution started",
        )

        for step in operation["steps"]:
            step_number = step["step"]
            step_key = step["key"]

            operation["currentStep"] = step_number
            step["status"] = "running"

            self.store.save_operation(operation)
            self.store.append_evidence(
                operation["operationId"],
                event_type="step-started",
                message=f"Started step {step_number}: {step_key}",
                details={
                    "step": step_number,
                    "key": step_key,
                },
            )

            # Package 002 never performs a live change.
            step["status"] = "simulated"
            step["message"] = "Dry-run only; no changes applied."

            self.store.save_operation(operation)
            self.store.append_evidence(
                operation["operationId"],
                event_type="step-simulated",
                message=f"Simulated step {step_number}: {step_key}",
                details={
                    "step": step_number,
                    "key": step_key,
                    "changesApplied": False,
                },
            )

        operation["status"] = "simulated"
        self.store.save_operation(operation)

        self.store.append_evidence(
            operation["operationId"],
            event_type="operation-completed",
            message="Dry-run lifecycle execution completed",
            details={
                "changesApplied": False,
            },
        )

        return operation

    def resume_dry_run(
        self,
        operation: dict[str, Any],
    ) -> dict[str, Any]:
        if operation["status"] == "simulated":
            return operation

        return self.execute_dry_run(operation)
