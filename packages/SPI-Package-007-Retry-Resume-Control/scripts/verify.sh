#!/usr/bin/env bash
set -euo pipefail
REPO="${1:-/home/umbrel/seymour-platform-installer}"
cd "$REPO"
python3 tests/test_package_004.py
python3 tests/test_package_005.py
python3 tests/test_package_006.py
python3 tests/test_package_007.py
./bin/spi doctor >/tmp/spi-package-007-doctor.json
python3 - <<'PY'
import json
from pathlib import Path
result = json.loads(Path('/tmp/spi-package-007-doctor.json').read_text())
assert result['ready'] is True
assert result['safeMode'] is True
print('SPI Package 007 final verification: PASS')
PY
