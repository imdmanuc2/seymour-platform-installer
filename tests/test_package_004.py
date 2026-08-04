import json, subprocess
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
SPI = ROOT / "bin" / "spi"
def run(*args):
    return json.loads(subprocess.run([str(SPI), *args], cwd=ROOT, capture_output=True, text=True, check=True).stdout)
assert run("adapters")["count"] == 4
umbrel = run("adapter", "show", "umbrel")
assert "docker" in umbrel["capabilities"]
assert "systemd" in umbrel["deniedCapabilities"]
assert "host-disk-management" in umbrel["deniedCapabilities"]
assert "persistent-storage" in run("capabilities")["capabilities"]
validation = run("validate", "seymour-miningcore")
assert validation["success"] is True
assert validation["safeMode"] is True
assert validation["changesApplied"] is False
assert validation["validation"]["compatible"] is True
assert validation["validation"]["adapter"]["id"] == "umbrel"
print("SPI Package 004 adapter capability verification: PASS")
