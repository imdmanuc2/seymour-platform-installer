from __future__ import annotations

import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPI = ROOT / "bin" / "spi"


def run_json(*args: str) -> tuple[dict, int]:
    result = subprocess.run(
        [str(SPI), *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
    )
    if not result.stdout.strip():
        raise AssertionError(result.stderr or "No JSON output")
    return json.loads(result.stdout), result.returncode


run, code = run_json("run", "seymour-miningcore", "install")
assert code == 0
operation = run["operation"]
operation_id = operation["operationId"]

assert operation["schemaVersion"] == 1
assert operation["startedAt"]
assert operation["completedAt"]
assert operation["durationMilliseconds"] is not None
assert operation["outcome"]["success"] is True
assert operation["outcome"]["status"] == "simulated"
assert operation["outcome"]["changed"] is False

summary, code = run_json("operation", "summary", operation_id)
assert code == 0
assert summary["operationId"] == operation_id
assert summary["status"] == "simulated"
assert summary["stepCount"] == 11
assert summary["stepStatusCounts"]["simulated"] == 11

latest, code = run_json("operation", "latest", "seymour-miningcore")
assert code == 0
assert latest["operationId"] == operation_id

latest_any, code = run_json("operation", "latest")
assert code == 0
assert latest_any["operationId"] == operation_id

timeline, code = run_json("operation", "timeline", operation_id)
assert code == 0
assert timeline["operationId"] == operation_id
assert timeline["count"] >= 1
assert isinstance(timeline["events"], list)

print("SPI Package 006 operation engine verification: PASS")
