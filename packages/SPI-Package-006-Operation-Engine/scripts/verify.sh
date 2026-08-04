#!/usr/bin/env bash
set -euo pipefail

REPO="${1:-/home/umbrel/seymour-platform-installer}"
cd "$REPO"

python3 tests/test_package_004.py
python3 tests/test_package_005.py
python3 tests/test_package_006.py

./bin/spi doctor >/tmp/spi-package-006-doctor.json

echo "SPI Package 006 final verification: PASS"
