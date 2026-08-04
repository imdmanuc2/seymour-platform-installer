from pathlib import Path
import sys

repo = Path(sys.argv[1])
path = repo / "lib/lifecycle/executor.py"
text = path.read_text()

imports = (
    "from lifecycle.crash_injection import should_inject_crash\n"
    "from lifecycle.transaction import (\n"
    "    commit_checkpoint,\n"
    "    create_checkpoint,\n"
    "    mark_transaction_completed,\n"
    "    mark_transaction_interrupted,\n"
    "    mark_transaction_started,\n"
    ")\n"
)
if "from lifecycle.transaction import" not in text:
    text = text.replace(
        "from lifecycle.failure_injection import should_inject_failure\n",
        "from lifecycle.failure_injection import should_inject_failure\n"
        + imports,
    )

if "mark_transaction_started(operation)" not in text:
    text = text.replace(
        "        mark_operation_started(operation)\n"
        "        self.store.save_operation(operation)\n",
        "        mark_operation_started(operation)\n"
        "        mark_transaction_started(operation)\n"
        "        self.store.save_operation(operation)\n",
    )

if 'event_type=("transaction-resumed"' not in text:
    anchor = (
        "        self.store.append_evidence(\n"
        '            operation["operationId"],\n'
        '            event_type=("operation-resumed" if resumed else "operation-started"),\n'
    )
    insert = (
        "        self.store.append_evidence(\n"
        '            operation["operationId"],\n'
        '            event_type=("transaction-resumed" if resumed else "transaction-started"),\n'
        "            message=(\n"
        '                "Dry-run transaction resumed"\n'
        "                if resumed\n"
        '                else "Dry-run transaction started"\n'
        "            ),\n"
        "            details={\n"
        '                "transactionId": operation["transaction"]["transactionId"],\n'
        "            },\n"
        "        )\n\n"
    )
    text = text.replace(anchor, insert + anchor)

if 'event_type="checkpoint-prepared"' not in text:
    anchor = (
        '            operation["currentStep"] = step_number\n'
        '            step["status"] = "running"\n'
        "            self.store.save_operation(operation)\n"
    )
    repl = (
        '            operation["currentStep"] = step_number\n'
        "            checkpoint = create_checkpoint(\n"
        "                operation,\n"
        "                step_number=step_number,\n"
        "                plugin_key=step_key,\n"
        "            )\n"
        '            step["checkpointId"] = checkpoint["checkpointId"]\n'
        '            step["status"] = "running"\n'
        "            self.store.save_operation(operation)\n\n"
        "            self.store.append_evidence(\n"
        '                operation["operationId"],\n'
        '                event_type="checkpoint-prepared",\n'
        '                message=f"Prepared checkpoint for {step_key}.",\n'
        "                details={\n"
        '                    "step": step_number,\n'
        '                    "plugin": step_key,\n'
        '                    "checkpointId": checkpoint["checkpointId"],\n'
        "                },\n"
        "            )\n"
    )
    text = text.replace(anchor, repl)

if "should_inject_crash(plugin_key=step_key)" not in text:
    anchor = (
        "            plugin = self.registry.require(step_key)\n\n"
        "            if should_inject_failure(\n"
    )
    repl = (
        "            plugin = self.registry.require(step_key)\n\n"
        "            if should_inject_crash(plugin_key=step_key):\n"
        '                message = f"Injected transaction interruption for {step_key}."\n'
        '                step["status"] = "paused"\n'
        '                step["message"] = message\n'
        '                operation["status"] = "paused"\n'
        '                operation["completedAt"] = None\n'
        '                operation["durationMilliseconds"] = None\n'
        '                operation["outcome"] = {\n'
        '                    "success": False,\n'
        '                    "status": "paused",\n'
        '                    "changed": False,\n'
        '                    "message": message,\n'
        '                    "details": {\n'
        '                        "changesApplied": False,\n'
        '                        "interruptedStep": step_number,\n'
        "                    },\n"
        "                }\n"
        "                mark_transaction_interrupted(operation, message=message)\n"
        "                self.store.save_operation(operation)\n"
        "                self.store.append_evidence(\n"
        '                    operation["operationId"],\n'
        '                    event_type="transaction-interrupted",\n'
        "                    message=message,\n"
        "                    details={\n"
        '                        "step": step_number,\n'
        '                        "plugin": step_key,\n'
        '                        "transactionId": operation["transaction"]["transactionId"],\n'
        '                        "lastCommittedStep": operation["transaction"]["lastCommittedStep"],\n'
        "                    },\n"
        "                )\n"
        "                return operation\n\n"
        "            if should_inject_failure(\n"
    )
    text = text.replace(anchor, repl)

if 'event_type="checkpoint-committed"' not in text:
    anchor = (
        "            self.store.append_evidence(\n"
        '                operation["operationId"],\n'
        '                event_type="plugin-result",\n'
    )
    insert = (
        "            checkpoint = commit_checkpoint(\n"
        "                operation,\n"
        "                step_number=step_number,\n"
        "            )\n"
        "            self.store.save_operation(operation)\n"
        "            self.store.append_evidence(\n"
        '                operation["operationId"],\n'
        '                event_type="checkpoint-committed",\n'
        '                message=f"Committed checkpoint for {step_key}.",\n'
        "                details={\n"
        '                    "step": step_number,\n'
        '                    "plugin": step_key,\n'
        '                    "checkpointId": checkpoint["checkpointId"],\n'
        "                },\n"
        "            )\n\n"
    )
    text = text.replace(anchor, insert + anchor)

if 'event_type="transaction-committed"' not in text:
    anchor = (
        "        self.store.save_operation(operation)\n\n"
        "        self.store.append_evidence(\n"
        '            operation["operationId"],\n'
        '            event_type="operation-completed",\n'
    )
    repl = (
        '        if operation["status"] == "simulated":\n'
        "            mark_transaction_completed(operation)\n\n"
        "        self.store.save_operation(operation)\n\n"
        '        if operation["status"] == "simulated":\n'
        "            self.store.append_evidence(\n"
        '                operation["operationId"],\n'
        '                event_type="transaction-committed",\n'
        '                message="Dry-run transaction committed.",\n'
        "                details={\n"
        '                    "transactionId": operation["transaction"]["transactionId"],\n'
        '                    "lastCommittedStep": operation["transaction"]["lastCommittedStep"],\n'
        "                },\n"
        "            )\n\n"
        "        self.store.append_evidence(\n"
        '            operation["operationId"],\n'
        '            event_type="operation-completed",\n'
    )
    text = text.replace(anchor, repl)

path.write_text(text)
