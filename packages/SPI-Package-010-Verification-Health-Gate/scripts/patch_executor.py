from pathlib import Path
import sys

repo = Path(sys.argv[1]).resolve()
path = repo / "lib/lifecycle/executor.py"
text = path.read_text()

anchor = "from lifecycle.failure_injection import should_inject_failure\n"
imports = (
    "from lifecycle.health_gate import (\n"
    "    evaluate_health_gate,\n"
    "    mark_verification_failed,\n"
    ")\n"
)
if "from lifecycle.health_gate import" not in text:
    if anchor not in text:
        raise SystemExit("Could not locate executor import anchor")
    text = text.replace(anchor, anchor + imports)

marker = "        if failure_message is not None:\n"
gate = '''        if failure_message is None:
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

'''
if 'event_type="health-gate-started"' not in text:
    if marker not in text:
        raise SystemExit("Could not locate failure completion block")
    text = text.replace(marker, gate + marker, 1)

path.write_text(text)
