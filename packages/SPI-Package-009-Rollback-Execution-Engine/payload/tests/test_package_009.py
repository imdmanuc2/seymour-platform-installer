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


created, code = run_json("run", "seymour-miningcore", "install")
assert code == 0
operation_id = created["operation"]["operationId"]
assert len(created["operation"]["transaction"]["rollbackPlan"]) == 11

paused, code = run_json(
    "operation", "rollback", operation_id,
    env={"SPI_TEST_ROLLBACK_INTERRUPT_STEP": "8"},
)
assert code == 1
rollback = paused["operation"]["rollback"]
assert rollback["status"] == "paused"
assert rollback["rolledBackCount"] == 3

resumed, code = run_json("operation", "rollback", operation_id)
assert code == 0
rollback = resumed["operation"]["rollback"]
assert rollback["status"] == "completed"
assert rollback["rolledBackCount"] == 11
assert rollback["outcome"]["success"] is True

again, code = run_json("operation", "rollback", operation_id)
assert code == 0
assert again["operation"]["rollback"]["rolledBackCount"] == 11

status, code = run_json("operation", "rollback-status", operation_id)
assert code == 0
assert status["status"] == "completed"
assert status["planCount"] == 11
assert status["rolledBackCount"] == 11

timeline, code = run_json("operation", "timeline", operation_id)
assert code == 0
events = {item["eventType"] for item in timeline["events"]}
assert "rollback-started" in events
assert "rollback-paused" in events
assert "rollback-step-completed" in events
assert "rollback-completed" in events

print("SPI Package 009 rollback execution verification: PASS")
