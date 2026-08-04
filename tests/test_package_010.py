from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPI = ROOT / "bin" / "spi"


def run_json(*args: str, env=None):
    merged = os.environ.copy()
    if env:
        merged.update(env)
    result = subprocess.run(
        [str(SPI), *args], cwd=ROOT, env=merged,
        capture_output=True, text=True, check=False, timeout=30,
    )
    if not result.stdout.strip():
        raise AssertionError(result.stderr or "No JSON output")
    return json.loads(result.stdout), result.returncode


healthy, code = run_json("run", "seymour-miningcore", "install")
assert code == 0
operation = healthy["operation"]
assert operation["status"] == "simulated"
assert operation["healthGate"]["healthy"] is True
assert operation["transaction"]["status"] == "committed"

failed, code = run_json(
    "run", "seymour-miningcore", "install",
    env={"SPI_TEST_HEALTH_FAIL_CHECK": "all-checkpoints-committed"},
)
assert code == 1
operation = failed["operation"]
operation_id = operation["operationId"]
assert operation["status"] == "failed"
assert operation["healthGate"]["healthy"] is False
assert "all-checkpoints-committed" in operation["healthGate"]["failedChecks"]
assert operation["transaction"]["status"] == "verification-failed"
assert len(operation["transaction"]["rollbackPlan"]) == 11

timeline, code = run_json("operation", "timeline", operation_id)
assert code == 0
events = {event["eventType"] for event in timeline["events"]}
assert "health-gate-started" in events
assert "health-gate-failed" in events

print("SPI Package 010 verification and health gate verification: PASS")
