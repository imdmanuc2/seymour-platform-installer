from pathlib import Path
import sys

repo = Path(sys.argv[1])
path = repo / "bin/spi"
text = path.read_text()

if "from lifecycle.rollback import" not in text:
    text = text.replace(
        "from lifecycle.preflight import validate_lifecycle_plan\n",
        "from lifecycle.preflight import validate_lifecycle_plan\n"
        "from lifecycle.rollback import (\n"
        "    execute_rollback_dry_run,\n"
        "    rollback_status,\n"
        ")\n",
    )

function = '''\ndef command_operation_rollback(operation_id: str) -> None:\n    store = StateStore(ROOT)\n    try:\n        operation = store.load_operation(operation_id)\n    except FileNotFoundError as exc:\n        output({"success": False, "error": str(exc)}, 1)\n\n    result = execute_rollback_dry_run(\n        operation=operation,\n        store=store,\n    )\n    completed = result["rollback"]["status"] == "completed"\n    output({\n        "success": completed,\n        "safeMode": True,\n        "changesApplied": False,\n        "operation": result,\n    }, 0 if completed else 1)\n\n\ndef command_operation_rollback_status(operation_id: str) -> None:\n    store = StateStore(ROOT)\n    try:\n        operation = store.load_operation(operation_id)\n    except FileNotFoundError as exc:\n        output({"success": False, "error": str(exc)}, 1)\n    output(rollback_status(operation))\n\n'''

marker = "\ndef command_operation_summary(operation_id: str) -> None:\n"
if "def command_operation_rollback(" not in text:
    if marker not in text:
        raise SystemExit("Could not find operation summary marker")
    text = text.replace(marker, function + marker)

if "spi operation rollback <operation-id>" not in text:
    text = text.replace(
        "  spi operation resume <operation-id>\n",
        "  spi operation resume <operation-id>\n"
        "  spi operation rollback <operation-id>\n"
        "  spi operation rollback-status <operation-id>\n",
    )

if 'elif action == "rollback":' not in text:
    text = text.replace(
        '        elif action == "summary":\n            command_operation_summary(operation_id)\n',
        '        elif action == "rollback":\n            command_operation_rollback(operation_id)\n'
        '        elif action == "rollback-status":\n            command_operation_rollback_status(operation_id)\n'
        '        elif action == "summary":\n            command_operation_summary(operation_id)\n',
    )

path.write_text(text)
