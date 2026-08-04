from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPI = ROOT / "bin" / "spi"


def run_json(*args: str, env: dict[str, str] | None = None) -> tuple[dict, int]:
    merged = os.environ.copy()
    if env:
        merged.update(env)
    result = subprocess.run(
        [str(SPI), *args],
        cwd=ROOT,
        env=merged,
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
    )
    if not result.stdout.strip():
        raise AssertionError(result.stderr or "No JSON output")
    return json.loads(result.stdout), result.returncode


# Force verify-health to fail once. The operation must pause rather than
# duplicate completed steps or claim success.
failed, code = run_json(
    "run",
    "seymour-miningcore",
    "install",
    env={
        "SPI_TEST_FAIL_PLUGIN": "verify-health",
        "SPI_TEST_FAIL_ATTEMPTS": "1",
    },
)

assert code == 1
assert failed["success"] is False
operation = failed["operation"]
assert operation["status"] == "paused"
assert operation["startedAt"]
assert operation["completedAt"] is None
assert operation["durationMilliseconds"] is None
assert operation["outcome"]["status"] == "paused"
operation_id = operation["operationId"]

verify_step = next(
    step for step in operation["steps"]
    if step["key"] == "verify-health"
)
assert verify_step["status"] == "paused"
assert verify_step["attempts"] == 1

completed_before = {
    step["key"]: step.get("attempts", 0)
    for step in operation["steps"]
    if step["status"] == "simulated"
}

# Resume without failure injection. Completed steps must keep their original
# attempt counts and the paused step must continue.
resumed, code = run_json(
    "operation",
    "resume",
    operation_id,
)

assert code == 0
assert resumed["success"] is True
resumed_operation = resumed["operation"]
assert resumed_operation["status"] == "simulated"
assert resumed_operation["completedAt"]
assert resumed_operation["durationMilliseconds"] is not None
assert resumed_operation["outcome"]["success"] is True

for step in resumed_operation["steps"]:
    if step["key"] in completed_before:
        assert step.get("attempts", 0) == completed_before[step["key"]]

resumed_verify = next(
    step for step in resumed_operation["steps"]
    if step["key"] == "verify-health"
)
assert resumed_verify["status"] == "simulated"
assert resumed_verify["attempts"] == 2

# Timeline must contain pause, resume, and retry evidence.
timeline, code = run_json(
    "operation",
    "timeline",
    operation_id,
)
assert code == 0
event_types = {
    event["eventType"]
    for event in timeline.get("events", [])
}
assert "operation-paused" in event_types
assert "operation-resumed" in event_types
assert "plugin-retry" in event_types

print("SPI Package 007 retry and resume verification: PASS")
