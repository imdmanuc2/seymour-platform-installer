from __future__ import annotations

from datetime import UTC, datetime
from typing import Any


OPERATION_SCHEMA_VERSION = 1


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


def parse_time(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value)


def duration_milliseconds(
    started_at: str | None,
    completed_at: str | None,
) -> int | None:
    started = parse_time(started_at)
    completed = parse_time(completed_at)
    if started is None or completed is None:
        return None
    return max(0, int((completed - started).total_seconds() * 1000))


def initialize_operation_record(
    operation: dict[str, Any],
) -> dict[str, Any]:
    operation.setdefault("schemaVersion", OPERATION_SCHEMA_VERSION)
    operation.setdefault("startedAt", None)
    operation.setdefault("completedAt", None)
    operation.setdefault("durationMilliseconds", None)
    operation.setdefault("outcome", None)
    return operation


def mark_operation_started(
    operation: dict[str, Any],
) -> dict[str, Any]:
    initialize_operation_record(operation)
    operation["startedAt"] = operation.get("startedAt") or utc_now()
    operation["status"] = "running"
    return operation


def mark_operation_completed(
    operation: dict[str, Any],
    *,
    status: str,
    success: bool,
    changed: bool,
    message: str,
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    initialize_operation_record(operation)
    operation["completedAt"] = utc_now()
    operation["durationMilliseconds"] = duration_milliseconds(
        operation.get("startedAt"),
        operation.get("completedAt"),
    )
    operation["status"] = status
    operation["outcome"] = {
        "success": success,
        "status": status,
        "changed": changed,
        "message": message,
        "details": details or {},
    }
    return operation


def summarize_operation(
    operation: dict[str, Any],
) -> dict[str, Any]:
    steps = operation.get("steps", [])
    counts: dict[str, int] = {}
    for step in steps:
        status = str(step.get("status", "unknown"))
        counts[status] = counts.get(status, 0) + 1

    return {
        "operationId": operation.get("operationId"),
        "schemaVersion": operation.get("schemaVersion"),
        "product": operation.get("product"),
        "action": operation.get("action"),
        "adapter": operation.get("adapter"),
        "dryRun": operation.get("dryRun"),
        "status": operation.get("status"),
        "createdAt": operation.get("createdAt"),
        "startedAt": operation.get("startedAt"),
        "completedAt": operation.get("completedAt"),
        "durationMilliseconds": operation.get("durationMilliseconds"),
        "currentStep": operation.get("currentStep"),
        "stepCount": len(steps),
        "stepStatusCounts": counts,
        "outcome": operation.get("outcome"),
    }
