#!/usr/bin/env bash
set -euo pipefail
REPO="${1:-/home/umbrel/seymour-platform-installer}"
fail(){ echo "DOCTOR FAIL: $*" >&2; exit 1; }
[[ -d "$REPO/.git" ]] || fail "Not a Git repository"
[[ "$(git -C "$REPO" branch --show-current)" == "develop" ]] || fail "Expected develop branch"
for file in \
  bin/spi \
  lib/lifecycle/executor.py \
  lib/lifecycle/transaction.py \
  lib/lifecycle/rollback.py \
  tests/test_package_009.py
do
  [[ -f "$REPO/$file" ]] || fail "Missing Package 009 prerequisite: $file"
done
python3 "$REPO/tests/test_package_004.py" >/dev/null
python3 "$REPO/tests/test_package_005.py" >/dev/null
python3 "$REPO/tests/test_package_006.py" >/dev/null
python3 "$REPO/tests/test_package_007.py" >/dev/null
python3 "$REPO/tests/test_package_008.py" >/dev/null
python3 "$REPO/tests/test_package_009.py" >/dev/null
echo "SPI Package 010 doctor: PASS"
