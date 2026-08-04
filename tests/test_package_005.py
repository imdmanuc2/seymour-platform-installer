from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPI = ROOT / "bin" / "spi"
MANIFEST = ROOT / "products" / "seymour-miningcore" / "product.json"


def run_json(*args: str) -> tuple[dict, int]:
    result = subprocess.run(
        [str(SPI), *args], cwd=ROOT,
        capture_output=True, text=True,
        check=False, timeout=30,
    )
    if not result.stdout.strip():
        raise AssertionError(result.stderr or "No JSON output")
    return json.loads(result.stdout), result.returncode


plan, code = run_json("plan-check", "seymour-miningcore", "install")
assert code == 0
assert plan["success"] is True
assert plan["safeMode"] is True
assert plan["changesApplied"] is False
assert plan["validation"]["compatible"] is True
assert plan["validation"]["blocked"] is False

operation, code = run_json("run", "seymour-miningcore", "install")
assert code == 0
assert operation["success"] is True
assert operation["changesApplied"] is False
assert operation["operation"]["status"] == "simulated"

original = MANIFEST.read_text()
try:
    manifest = json.loads(original)
    capabilities = manifest.setdefault("requirements", {}).setdefault("capabilities", [])
    if "systemd" not in capabilities:
        capabilities.append("systemd")
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n")

    blocked, code = run_json("plan-check", "seymour-miningcore", "install")
    assert code == 1
    assert blocked["success"] is False
    assert blocked["validation"]["blocked"] is True
    assert "systemd" in blocked["validation"]["explicitlyDeniedCapabilities"]

    blocked_run, code = run_json("run", "seymour-miningcore", "install")
    assert code == 1
    assert blocked_run["blocked"] is True
    assert blocked_run["changesApplied"] is False
finally:
    MANIFEST.write_text(original)

print("SPI Package 005 capability-gated lifecycle verification: PASS")
