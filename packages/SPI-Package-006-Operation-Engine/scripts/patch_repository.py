from __future__ import annotations

from pathlib import Path
import sys


repo = Path(sys.argv[1]).resolve()

# Patch state/store.py to initialize schema fields on create and load.
store_path = repo / "lib/state/store.py"
text = store_path.read_text()

if "from lifecycle.operation import initialize_operation_record" not in text:
    text = text.replace(
        "from uuid import uuid4\n",
        "from uuid import uuid4\n\n"
        "from lifecycle.operation import initialize_operation_record\n",
    )

create_anchor = "        self.save_operation(operation)\n"
if "initialize_operation_record(operation)" not in text:
    if create_anchor not in text:
        raise SystemExit("Could not locate create_operation save anchor")
    text = text.replace(
        create_anchor,
        "        initialize_operation_record(operation)\n"
        + create_anchor,
        1,
    )

load_anchor = "        return json.loads(path.read_text())\n"
if "return initialize_operation_record" not in text:
    if load_anchor not in text:
        raise SystemExit("Could not locate load_operation return anchor")
    text = text.replace(
        load_anchor,
        "        return initialize_operation_record(\n"
        "            json.loads(path.read_text())\n"
        "        )\n",
        1,
    )

store_path.write_text(text)

# Replace executor with operation-aware implementation while preserving plugin behavior.
executor_path = repo / "lib/lifecycle/executor.py"
executor_path.write_text('''from __future__ import annotations

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
''')

# Patch CLI imports, commands, help, and dispatch.
spi_path = repo / "bin/spi"
text = spi_path.read_text()

if "from lifecycle.operation import summarize_operation" not in text:
    text = text.replace(
        "from lifecycle.preflight import validate_lifecycle_plan\n",
        "from lifecycle.preflight import validate_lifecycle_plan\n"
        "from lifecycle.operation import summarize_operation\n",
    )

functions = '''
def command_operation_summary(operation_id: str) -> None:
    store = StateStore(ROOT)
    try:
        operation = store.load_operation(operation_id)
    except FileNotFoundError as exc:
        output({"success": False, "error": str(exc)}, 1)
    output(summarize_operation(operation))


def command_operation_latest(
    product_id: str | None = None,
) -> None:
    store = StateStore(ROOT)
    operations = store.list_operations()

    if product_id is not None:
        operations = [
            operation
            for operation in operations
            if operation.get("product", {}).get("id") == product_id
        ]

    if not operations:
        output({
            "success": False,
            "error": "No matching operations found.",
        }, 1)

    output(summarize_operation(operations[0]))


def command_operation_timeline(operation_id: str) -> None:
    store = StateStore(ROOT)
    events = store.read_evidence(operation_id)
    output({
        "success": True,
        "operationId": operation_id,
        "count": len(events),
        "events": events,
    })


'''

marker = "\ndef command_doctor() -> None:\n"
if "def command_operation_summary(" not in text:
    if marker not in text:
        raise SystemExit("Could not locate command_doctor")
    text = text.replace(marker, "\n" + functions + "def command_doctor() -> None:\n")

if "spi operation summary" not in text:
    text = text.replace(
        "  spi operation resume <operation-id>\n",
        "  spi operation resume <operation-id>\n"
        "  spi operation summary <operation-id>\n"
        "  spi operation latest [product-id]\n"
        "  spi operation timeline <operation-id>\n",
    )

old_block = '''        if action == "show":
            command_operation_show(operation_id)
        elif action == "evidence":
            command_operation_evidence(operation_id)
        elif action == "resume":
            command_operation_resume(operation_id)
        else:
'''

new_block = '''        if action == "show":
            command_operation_show(operation_id)
        elif action == "evidence":
            command_operation_evidence(operation_id)
        elif action == "resume":
            command_operation_resume(operation_id)
        elif action == "summary":
            command_operation_summary(operation_id)
        elif action == "timeline":
            command_operation_timeline(operation_id)
        else:
'''

if 'elif action == "summary"' not in text:
    if old_block not in text:
        raise SystemExit("Could not locate operation action dispatch")
    text = text.replace(old_block, new_block)

# Latest has an optional product-id, so add dispatch before the generic operation block.
operation_dispatch = '    elif command == "operation" and len(args) >= 3:\n'
latest_dispatch = '''    elif command == "operation" and len(args) >= 2 and args[1] == "latest":
        command_operation_latest(
            args[2] if len(args) >= 3 else None
        )

'''

if 'args[1] == "latest"' not in text:
    if operation_dispatch not in text:
        raise SystemExit("Could not locate operation dispatch")
    text = text.replace(operation_dispatch, latest_dispatch + operation_dispatch)

spi_path.write_text(text)
