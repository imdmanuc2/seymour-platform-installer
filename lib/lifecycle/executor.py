from __future__ import annotations

from typing import Any

from lifecycle.failure_injection import should_inject_failure
from lifecycle.health_gate import (
    evaluate_health_gate,
    mark_verification_failed,
)
from lifecycle.crash_injection import should_inject_crash
from lifecycle.transaction import (
    commit_checkpoint,
    create_checkpoint,
    mark_transaction_completed,
    mark_transaction_interrupted,
    mark_transaction_started,
)
from lifecycle.operation import (
    mark_operation_completed,
    mark_operation_started,
)
from lifecycle.retry import retry_policy_for
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

    def _first_incomplete_index(
        self,
        operation: dict[str, Any],
    ) -> int:
        for index, step in enumerate(operation["steps"]):
            if step.get("status") not in {"simulated", "complete"}:
                return index
        return len(operation["steps"])

    def execute_dry_run(
        self,
        operation: dict[str, Any],
        *,
        manifest: dict[str, Any],
        resumed: bool = False,
    ) -> dict[str, Any]:
        mark_operation_started(operation)
        mark_transaction_started(operation)
        self.store.save_operation(operation)

        self.store.append_evidence(
            operation["operationId"],
            event_type=("transaction-resumed" if resumed else "transaction-started"),
            message=(
                "Dry-run transaction resumed"
                if resumed
                else "Dry-run transaction started"
            ),
            details={
                "transactionId": operation["transaction"]["transactionId"],
            },
        )

        self.store.append_evidence(
            operation["operationId"],
            event_type=("operation-resumed" if resumed else "operation-started"),
            message=(
                "Plugin-based dry-run execution resumed"
                if resumed
                else "Plugin-based dry-run execution started"
            ),
        )

        context = {
            "operationId": operation["operationId"],
            "product": operation["product"],
            "adapter": operation["adapter"],
            "manifest": manifest,
        }

        start_index = self._first_incomplete_index(operation)
        failure_message: str | None = None

        for step in operation["steps"][start_index:]:
            step_number = step["step"]
            step_key = step["key"]
            policy = retry_policy_for(step_key)

            attempt = int(step.get("attempts", 0)) + 1
            step["attempts"] = attempt
            step["retryPolicy"] = policy.to_dict()
            operation["currentStep"] = step_number
            checkpoint = create_checkpoint(
                operation,
                step_number=step_number,
                plugin_key=step_key,
            )
            step["checkpointId"] = checkpoint["checkpointId"]
            step["status"] = "running"
            self.store.save_operation(operation)

            self.store.append_evidence(
                operation["operationId"],
                event_type="checkpoint-prepared",
                message=f"Prepared checkpoint for {step_key}.",
                details={
                    "step": step_number,
                    "plugin": step_key,
                    "checkpointId": checkpoint["checkpointId"],
                },
            )

            self.store.append_evidence(
                operation["operationId"],
                event_type="plugin-started",
                message=f"Executing plugin: {step_key}",
                details={
                    "step": step_number,
                    "plugin": step_key,
                    "attempt": attempt,
                },
            )

            plugin = self.registry.require(step_key)

            if should_inject_crash(plugin_key=step_key):
                message = f"Injected transaction interruption for {step_key}."
                step["status"] = "paused"
                step["message"] = message
                operation["status"] = "paused"
                operation["completedAt"] = None
                operation["durationMilliseconds"] = None
                operation["outcome"] = {
                    "success": False,
                    "status": "paused",
                    "changed": False,
                    "message": message,
                    "details": {
                        "changesApplied": False,
                        "interruptedStep": step_number,
                    },
                }
                mark_transaction_interrupted(operation, message=message)
                self.store.save_operation(operation)
                self.store.append_evidence(
                    operation["operationId"],
                    event_type="transaction-interrupted",
                    message=message,
                    details={
                        "step": step_number,
                        "plugin": step_key,
                        "transactionId": operation["transaction"]["transactionId"],
                        "lastCommittedStep": operation["transaction"]["lastCommittedStep"],
                    },
                )
                return operation

            if should_inject_failure(
                plugin_key=step_key,
                attempt=attempt,
            ):
                failure_message = (
                    f"Injected retryable failure for {step_key} "
                    f"on attempt {attempt}."
                )
                step["status"] = "paused"
                step["message"] = failure_message
                step["lastError"] = "test-failure-injection"
                operation["status"] = "paused"
                operation["completedAt"] = None
                operation["durationMilliseconds"] = None
                operation["outcome"] = {
                    "success": False,
                    "status": "paused",
                    "changed": False,
                    "message": failure_message,
                    "details": {
                        "changesApplied": False,
                        "pausedStep": step_number,
                        "retryable": True,
                    },
                }
                self.store.save_operation(operation)

                self.store.append_evidence(
                    operation["operationId"],
                    event_type="plugin-retry",
                    message=failure_message,
                    details={
                        "step": step_number,
                        "plugin": step_key,
                        "attempt": attempt,
                        "maxAttempts": policy.max_attempts,
                        "retryable": True,
                    },
                )
                self.store.append_evidence(
                    operation["operationId"],
                    event_type="operation-paused",
                    message=f"Operation paused at plugin {step_key}.",
                    details={
                        "step": step_number,
                        "plugin": step_key,
                        "attempt": attempt,
                    },
                )
                return operation

            if not plugin.supports_adapter(operation["adapter"]):
                failure_message = (
                    f"Plugin {step_key} does not support "
                    f"adapter {operation['adapter']}"
                )
                step["status"] = "failed"
                step["message"] = failure_message
                break

            result = plugin.execute(
                context=context,
                dry_run=True,
            )

            step["status"] = result.status
            step["message"] = result.message
            step["pluginResult"] = result.to_dict()
            step.pop("lastError", None)
            self.store.save_operation(operation)

            checkpoint = commit_checkpoint(
                operation,
                step_number=step_number,
            )
            self.store.save_operation(operation)
            self.store.append_evidence(
                operation["operationId"],
                event_type="checkpoint-committed",
                message=f"Committed checkpoint for {step_key}.",
                details={
                    "step": step_number,
                    "plugin": step_key,
                    "checkpointId": checkpoint["checkpointId"],
                },
            )

            self.store.append_evidence(
                operation["operationId"],
                event_type="plugin-result",
                message=result.message,
                details={
                    "step": step_number,
                    "plugin": step_key,
                    "attempt": attempt,
                    "result": result.to_dict(),
                },
            )

            if not result.success:
                failure_message = result.message
                if result.retryable and attempt < policy.max_attempts:
                    step["status"] = "paused"
                    operation["status"] = "paused"
                    operation["completedAt"] = None
                    operation["durationMilliseconds"] = None
                    operation["outcome"] = {
                        "success": False,
                        "status": "paused",
                        "changed": False,
                        "message": failure_message,
                        "details": {
                            "changesApplied": False,
                            "pausedStep": step_number,
                            "retryable": True,
                        },
                    }
                    self.store.append_evidence(
                        operation["operationId"],
                        event_type="plugin-retry",
                        message=(
                            f"Plugin {step_key} is retryable after "
                            f"attempt {attempt}."
                        ),
                        details={
                            "step": step_number,
                            "plugin": step_key,
                            "attempt": attempt,
                            "maxAttempts": policy.max_attempts,
                        },
                    )
                    self.store.append_evidence(
                        operation["operationId"],
                        event_type="operation-paused",
                        message=f"Operation paused at plugin {step_key}.",
                        details={
                            "step": step_number,
                            "plugin": step_key,
                            "attempt": attempt,
                        },
                    )
                    self.store.save_operation(operation)
                    return operation
                break

        if failure_message is None:
            self.store.append_evidence(
                operation["operationId"],
                event_type="health-gate-started",
                message="Post-action verification started.",
            )

            health_gate = evaluate_health_gate(operation)

            if health_gate["healthy"]:
                self.store.append_evidence(
                    operation["operationId"],
                    event_type="health-gate-passed",
                    message="Post-action verification passed.",
                    details={"healthGate": health_gate},
                )
            else:
                failure_message = (
                    "Post-action verification failed: "
                    + ", ".join(health_gate["failedChecks"])
                )
                mark_verification_failed(
                    operation,
                    health_gate=health_gate,
                )
                self.store.append_evidence(
                    operation["operationId"],
                    event_type="health-gate-failed",
                    message=failure_message,
                    details={"healthGate": health_gate},
                )

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

        if operation["status"] == "simulated":
            mark_transaction_completed(operation)

        self.store.save_operation(operation)

        if operation["status"] == "simulated":
            self.store.append_evidence(
                operation["operationId"],
                event_type="transaction-committed",
                message="Dry-run transaction committed.",
                details={
                    "transactionId": operation["transaction"]["transactionId"],
                    "lastCommittedStep": operation["transaction"]["lastCommittedStep"],
                },
            )

        self.store.append_evidence(
            operation["operationId"],
            event_type="operation-completed",
            message=operation["outcome"]["message"],
            details={
                "changesApplied": False,
                "status": operation["status"],
                "outcome": operation["outcome"],
                "durationMilliseconds": operation["durationMilliseconds"],
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

        for step in operation.get("steps", []):
            if step.get("status") not in {"simulated", "complete"}:
                step["status"] = "pending"
                step.pop("message", None)
                step.pop("pluginResult", None)

        operation["completedAt"] = None
        operation["durationMilliseconds"] = None
        operation["outcome"] = None
        operation["status"] = "planned"
        self.store.save_operation(operation)

        return self.execute_dry_run(
            operation,
            manifest=manifest,
            resumed=True,
        )
