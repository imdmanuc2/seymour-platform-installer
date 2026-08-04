from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from lifecycle.operation import initialize_operation_record


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


class StateStore:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.operations_dir = root / "state" / "operations"
        self.evidence_dir = root / "state" / "evidence"

        self.operations_dir.mkdir(parents=True, exist_ok=True)
        self.evidence_dir.mkdir(parents=True, exist_ok=True)

    def operation_path(self, operation_id: str) -> Path:
        return self.operations_dir / f"{operation_id}.json"

    def evidence_path(self, operation_id: str) -> Path:
        return self.evidence_dir / f"{operation_id}.jsonl"

    def create_operation(
        self,
        *,
        product: dict[str, Any],
        action: str,
        adapter: str,
        steps: list[dict[str, Any]],
        dry_run: bool,
    ) -> dict[str, Any]:
        operation_id = str(uuid4())
        now = utc_now()

        operation = {
            "operationId": operation_id,
            "product": product,
            "action": action,
            "adapter": adapter,
            "dryRun": dry_run,
            "status": "planned",
            "createdAt": now,
            "updatedAt": now,
            "currentStep": 0,
            "steps": steps,
        }

        initialize_operation_record(operation)
        self.save_operation(operation)
        self.append_evidence(
            operation_id,
            event_type="operation-created",
            message=f"Created {action} operation for {product['id']}",
            details={
                "adapter": adapter,
                "dryRun": dry_run,
            },
        )

        return operation

    def save_operation(self, operation: dict[str, Any]) -> None:
        operation["updatedAt"] = utc_now()

        target = self.operation_path(operation["operationId"])
        temporary = target.with_suffix(".tmp")

        temporary.write_text(json.dumps(operation, indent=2) + "\n")
        temporary.replace(target)

    def load_operation(self, operation_id: str) -> dict[str, Any]:
        path = self.operation_path(operation_id)

        if not path.exists():
            raise FileNotFoundError(f"Unknown operation: {operation_id}")

        return initialize_operation_record(
            json.loads(path.read_text())
        )

    def list_operations(self) -> list[dict[str, Any]]:
        operations = []

        for path in sorted(
            self.operations_dir.glob("*.json"),
            key=lambda item: item.stat().st_mtime,
            reverse=True,
        ):
            operations.append(json.loads(path.read_text()))

        return operations

    def append_evidence(
        self,
        operation_id: str,
        *,
        event_type: str,
        message: str,
        details: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        event = {
            "eventId": str(uuid4()),
            "operationId": operation_id,
            "eventType": event_type,
            "timestamp": utc_now(),
            "message": message,
            "details": details or {},
        }

        with self.evidence_path(operation_id).open("a") as handle:
            handle.write(json.dumps(event) + "\n")

        return event

    def read_evidence(self, operation_id: str) -> list[dict[str, Any]]:
        path = self.evidence_path(operation_id)

        if not path.exists():
            return []

        return [
            json.loads(line)
            for line in path.read_text().splitlines()
            if line.strip()
        ]
