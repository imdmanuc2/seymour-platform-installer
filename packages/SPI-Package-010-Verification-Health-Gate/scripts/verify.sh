#!/usr/bin/env bash
set -euo pipefail
REPO="${1:-/home/umbrel/seymour-platform-installer}"
cd "$REPO"
python3 tests/test_package_004.py
python3 tests/test_package_005.py
python3 tests/test_package_006.py
python3 tests/test_package_007.py
python3 tests/test_package_008.py
python3 tests/test_package_009.py
python3 tests/test_package_010.py
echo "SPI Package 010 final verification: PASS"
