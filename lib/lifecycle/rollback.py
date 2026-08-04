from __future__ import annotations

import os
from datetime import UTC, datetime
from typing import Any


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


def should_interrupt_rollback(*, step_number: int) -> bool:
    raw = os.environ.get("SPI_TEST_ROLLBACK_INTERRUPT_STEP", "").strip()
    if not raw:
        return False
    try:
        return int(raw) == step_number
    except ValueError:
        return False


def initialize_rollback_record(operation: dict[str, Any]) -> dict[str, Any]:
    transaction = operation.get("transaction") or {}
    rollback = operation.setdefault(
        "rollback",
        {
            "status": "not-started",
            "startedAt": None,
            "completedAt": None,
            "currentStep": None,
            "rolledBackCount": 0,
            "outcome": None,
            "plan": [dict(item) for item in transaction.get("rollbackPlan", [])],
        },
    )
    rollback.setdefault("plan", [dict(item) for item in transaction.get("rollbackPlan", [])])
    return rollback


def rollback_status(operation: dict[str, Any]) -> dict[str, Any]:
    rollback = initialize_rollback_record(operation)
    return {
        "operationId": operation.get("operationId"),
        "transactionId": (operation.get("transaction") or {}).get("transactionId"),
        "status": rollback.get("status"),
        "startedAt": rollback.get("startedAt"),
        "completedAt": rollback.get("completedAt"),
        "currentStep": rollback.get("currentStep"),
        "rolledBackCount": rollback.get("rolledBackCount", 0),
        "planCount": len(rollback.get("plan", [])),
        "outcome": rollback.get("outcome"),
        "plan": rollback.get("plan", []),
    }


def execute_rollback_dry_run(
    *,
    operation: dict[str, Any],
    store: Any,
) -> dict[str, Any]:
    rollback = initialize_rollback_record(operation)

    if rollback.get("status") == "completed":
        return operation

    rollback["startedAt"] = rollback.get("startedAt") or utc_now()
    rollback["status"] = "running"
    store.save_operation(operation)
    store.append_evidence(
        operation["operationId"],
        event_type="rollback-started",
        message="Dry-run rollback started.",
        details={
            "planCount": len(rollback["plan"]),
            "transactionId": operation["transaction"]["transactionId"],
        },
    )

    for item in rollback["plan"]:
        if item.get("status") == "rolled-back":
            continue

        step_number = int(item["step"])
        rollback["currentStep"] = step_number
        item["status"] = "rolling-back"
        item["startedAt"] = item.get("startedAt") or utc_now()
        store.save_operation(operation)
        store.append_evidence(
            operation["operationId"],
            event_type="rollback-step-started",
            message=f"Rolling back simulated step {step_number}: {item['plugin']}",
            details={"step": step_number, "plugin": item["plugin"]},
        )

        if should_interrupt_rollback(step_number=step_number):
            item["status"] = "paused"
            rollback["status"] = "paused"
            rollback["outcome"] = {
                "success": False,
                "status": "paused",
                "changed": False,
                "message": f"Rollback paused at step {step_number}.",
                "details": {"retryable": True, "pausedStep": step_number},
            }
            store.save_operation(operation)
            store.append_evidence(
                operation["operationId"],
                event_type="rollback-paused",
                message=f"Rollback paused at step {step_number}.",
                details={"step": step_number, "plugin": item["plugin"]},
            )
            return operation

        item["status"] = "rolled-back"
        item["completedAt"] = utc_now()
        rollback["rolledBackCount"] = int(rollback.get("rolledBackCount", 0)) + 1
        store.save_operation(operation)
        store.append_evidence(
            operation["operationId"],
            event_type="rollback-step-completed",
            message=f"Rolled back simulated step {step_number}: {item['plugin']}",
            details={"step": step_number, "plugin": item["plugin"]},
        )

    rollback["status"] = "completed"
    rollback["completedAt"] = utc_now()
    rollback["currentStep"] = None
    rollback["outcome"] = {
        "success": True,
        "status": "completed",
        "changed": False,
        "message": "Dry-run rollback completed.",
        "details": {"rolledBackCount": rollback["rolledBackCount"]},
    }
    store.save_operation(operation)
    store.append_evidence(
        operation["operationId"],
        event_type="rollback-completed",
        message="Dry-run rollback completed.",
        details={"rolledBackCount": rollback["rolledBackCount"]},
    )
    return operation
