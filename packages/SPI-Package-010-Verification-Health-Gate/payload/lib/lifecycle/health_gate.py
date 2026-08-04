from __future__ import annotations

import os
from datetime import UTC, datetime
from typing import Any

from lifecycle.transaction import build_rollback_plan


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


def requested_failed_check() -> str | None:
    value = os.environ.get("SPI_TEST_HEALTH_FAIL_CHECK", "").strip()
    return value or None


def _check(*, key: str, healthy: bool, message: str, details: dict[str, Any] | None = None) -> dict[str, Any]:
    forced = requested_failed_check() == key
    return {
        "key": key,
        "healthy": healthy and not forced,
        "forcedFailure": forced,
        "message": f"Forced failure: {message}" if forced else message,
        "details": details or {},
    }


def evaluate_health_gate(operation: dict[str, Any]) -> dict[str, Any]:
    steps = operation.get("steps", [])
    transaction = operation.get("transaction", {})
    checkpoints = transaction.get("checkpoints", [])
    complete = {"simulated", "complete"}

    incomplete_steps = [step.get("key") for step in steps if step.get("status") not in complete]
    failed_plugins = [
        step.get("key")
        for step in steps
        if isinstance(step.get("pluginResult"), dict)
        and not step["pluginResult"].get("success", False)
    ]
    uncommitted = [cp.get("step") for cp in checkpoints if cp.get("status") != "committed"]

    checks = [
        _check(
            key="all-lifecycle-steps-complete",
            healthy=not incomplete_steps,
            message="All lifecycle steps completed.",
            details={"incompleteSteps": incomplete_steps},
        ),
        _check(
            key="all-plugin-results-successful",
            healthy=not failed_plugins,
            message="All plugin results succeeded.",
            details={"failedPlugins": failed_plugins},
        ),
        _check(
            key="all-checkpoints-committed",
            healthy=len(checkpoints) == len(steps) and not uncommitted,
            message="All transaction checkpoints committed.",
            details={
                "checkpointCount": len(checkpoints),
                "stepCount": len(steps),
                "uncommittedCheckpoints": uncommitted,
            },
        ),
        _check(
            key="no-live-changes-applied",
            healthy=operation.get("dryRun") is True,
            message="Operation remained in dry-run mode.",
            details={"dryRun": operation.get("dryRun")},
        ),
    ]

    healthy = all(item["healthy"] for item in checks)
    result = {
        "schemaVersion": 1,
        "evaluatedAt": utc_now(),
        "healthy": healthy,
        "status": "passed" if healthy else "failed",
        "checks": checks,
        "failedChecks": [item["key"] for item in checks if not item["healthy"]],
    }
    operation["healthGate"] = result
    return result


def mark_verification_failed(operation: dict[str, Any], *, health_gate: dict[str, Any]) -> None:
    transaction = operation.get("transaction")
    if isinstance(transaction, dict):
        transaction["status"] = "verification-failed"
        transaction["verificationFailedAt"] = utc_now()
        transaction["verification"] = health_gate
        build_rollback_plan(operation)
