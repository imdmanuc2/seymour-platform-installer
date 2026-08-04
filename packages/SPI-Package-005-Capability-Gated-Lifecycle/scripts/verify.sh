#!/usr/bin/env bash
set -euo pipefail
REPO="${1:-/home/umbrel/seymour-platform-installer}"
cd "$REPO"
python3 tests/test_package_004.py
python3 tests/test_package_005.py
./bin/spi plan-check seymour-miningcore install >/tmp/spi-package-005-plan.json
./bin/spi run seymour-miningcore install >/tmp/spi-package-005-run.json
python3 - <<'PY'
import json
from pathlib import Path
plan=json.loads(Path('/tmp/spi-package-005-plan.json').read_text())
run=json.loads(Path('/tmp/spi-package-005-run.json').read_text())
assert plan['success'] is True
assert plan['safeMode'] is True
assert plan['changesApplied'] is False
assert plan['validation']['compatible'] is True
assert plan['validation']['blocked'] is False
assert run['success'] is True
assert run['changesApplied'] is False
assert run['operation']['status'] == 'simulated'
print('SPI Package 005 final verification: PASS')
PY
