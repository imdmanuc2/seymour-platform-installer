#!/usr/bin/env bash
set -euo pipefail
REPO="${1:-/home/umbrel/seymour-platform-installer}"
fail(){ echo "DOCTOR FAIL: $*" >&2; exit 1; }
[[ -d "$REPO/.git" ]] || fail "Not a Git repository"
[[ "$(git -C "$REPO" branch --show-current)" == "develop" ]] || fail "Expected develop branch"
[[ "$(git -C "$REPO" rev-parse --short HEAD)" == "98f56da" ]] || fail "Expected verified Package 008 commit 98f56da"
for f in bin/spi lib/lifecycle/transaction.py lib/lifecycle/executor.py lib/state/store.py tests/test_package_008.py; do
  [[ -f "$REPO/$f" ]] || fail "Missing prerequisite: $f"
done
python3 "$REPO/tests/test_package_004.py" >/dev/null
python3 "$REPO/tests/test_package_005.py" >/dev/null
python3 "$REPO/tests/test_package_006.py" >/dev/null
python3 "$REPO/tests/test_package_007.py" >/dev/null
python3 "$REPO/tests/test_package_008.py" >/dev/null
echo "SPI Package 009 doctor: PASS"
