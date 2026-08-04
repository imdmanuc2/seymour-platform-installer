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

normal, code = run_json("run", "seymour-miningcore", "install")
assert code == 0
operation = normal["operation"]
transaction = operation["transaction"]
assert transaction["schemaVersion"] == 1
assert transaction["transactionId"]
assert transaction["status"] == "committed"
assert transaction["lastCommittedStep"] == 11
assert len(transaction["checkpoints"]) == 11
assert all(x["status"] == "committed" for x in transaction["checkpoints"])
assert len(transaction["rollbackPlan"]) == 11

crashed, code = run_json(
    "run", "seymour-miningcore", "install",
    env={"SPI_TEST_CRASH_PLUGIN": "verify-health"},
)
assert code == 1
operation = crashed["operation"]
transaction = operation["transaction"]
operation_id = operation["operationId"]
assert operation["status"] == "paused"
assert transaction["status"] == "interrupted"
assert transaction["lastCommittedStep"] == 9
assert len(transaction["rollbackPlan"]) == 9

resumed, code = run_json("operation", "resume", operation_id)
assert code == 0
operation = resumed["operation"]
transaction = operation["transaction"]
assert operation["status"] == "simulated"
assert transaction["status"] == "committed"
assert transaction["lastCommittedStep"] == 11
assert len(transaction["checkpoints"]) == 11

timeline, code = run_json("operation", "timeline", operation_id)
assert code == 0
event_types = {event["eventType"] for event in timeline["events"]}
for required in {
    "transaction-started",
    "checkpoint-prepared",
    "checkpoint-committed",
    "transaction-interrupted",
    "transaction-resumed",
    "transaction-committed",
}:
    assert required in event_types

print("SPI Package 008 transaction engine verification: PASS")
