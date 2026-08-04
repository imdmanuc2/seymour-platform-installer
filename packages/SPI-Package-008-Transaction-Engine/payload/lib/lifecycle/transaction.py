from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

TRANSACTION_SCHEMA_VERSION = 1

def utc_now() -> str:
    return datetime.now(UTC).isoformat()

def initialize_transaction(operation: dict[str, Any]) -> dict[str, Any]:
    return operation.setdefault(
        "transaction",
        {
            "schemaVersion": TRANSACTION_SCHEMA_VERSION,
            "transactionId": str(uuid4()),
            "status": "planned",
            "createdAt": utc_now(),
            "startedAt": None,
            "completedAt": None,
            "lastCommittedStep": 0,
            "checkpoints": [],
            "rollbackPlan": [],
        },
    )

def mark_transaction_started(operation: dict[str, Any]) -> dict[str, Any]:
    transaction = initialize_transaction(operation)
    transaction["startedAt"] = transaction.get("startedAt") or utc_now()
    transaction["status"] = "running"
    return transaction

def create_checkpoint(
    operation: dict[str, Any],
    *,
    step_number: int,
    plugin_key: str,
) -> dict[str, Any]:
    transaction = initialize_transaction(operation)
    for checkpoint in transaction["checkpoints"]:
        if checkpoint["step"] == step_number:
            return checkpoint
    checkpoint = {
        "checkpointId": str(uuid4()),
        "step": step_number,
        "plugin": plugin_key,
        "status": "prepared",
        "preparedAt": utc_now(),
        "committedAt": None,
        "rolledBackAt": None,
    }
    transaction["checkpoints"].append(checkpoint)
    return checkpoint

def commit_checkpoint(
    operation: dict[str, Any],
    *,
    step_number: int,
) -> dict[str, Any]:
    transaction = initialize_transaction(operation)
    checkpoint = next(
        item for item in transaction["checkpoints"]
        if item["step"] == step_number
    )
    checkpoint["status"] = "committed"
    checkpoint["committedAt"] = utc_now()
    transaction["lastCommittedStep"] = max(
        int(transaction.get("lastCommittedStep", 0)),
        step_number,
    )
    return checkpoint

def build_rollback_plan(
    operation: dict[str, Any],
) -> list[dict[str, Any]]:
    transaction = initialize_transaction(operation)
    plan = [
        {
            "checkpointId": item["checkpointId"],
            "step": item["step"],
            "plugin": item["plugin"],
            "action": "rollback-simulated-step",
            "status": "planned",
        }
        for item in reversed(transaction["checkpoints"])
        if item["status"] == "committed"
    ]
    transaction["rollbackPlan"] = plan
    return plan

def mark_transaction_interrupted(
    operation: dict[str, Any],
    *,
    message: str,
) -> None:
    transaction = initialize_transaction(operation)
    transaction["status"] = "interrupted"
    transaction["interruptedAt"] = utc_now()
    transaction["message"] = message
    build_rollback_plan(operation)

def mark_transaction_completed(operation: dict[str, Any]) -> None:
    transaction = initialize_transaction(operation)
    transaction["status"] = "committed"
    transaction["completedAt"] = utc_now()
    build_rollback_plan(operation)
