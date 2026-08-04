#!/usr/bin/env bash
set -euo pipefail
REPO="${1:-/home/umbrel/seymour-platform-installer}"
fail(){ echo "DOCTOR FAIL: $*" >&2; exit 1; }

[[ -d "$REPO/.git" ]] || fail "Not a Git repository"
[[ "$(git -C "$REPO" branch --show-current)" == "develop" ]] || fail "Expected develop branch"
[[ "$(git -C "$REPO" rev-parse --short HEAD)" == "c85b9bd" ]] || fail "Expected verified Package 007 commit c85b9bd"

for file in \
  bin/spi \
  lib/lifecycle/executor.py \
  lib/lifecycle/operation.py \
  lib/lifecycle/retry.py \
  lib/lifecycle/failure_injection.py \
  lib/state/store.py \
  tests/test_package_007.py
do
  [[ -f "$REPO/$file" ]] || fail "Missing prerequisite: $file"
done

python3 "$REPO/tests/test_package_004.py" >/dev/null
python3 "$REPO/tests/test_package_005.py" >/dev/null
python3 "$REPO/tests/test_package_006.py" >/dev/null
python3 "$REPO/tests/test_package_007.py" >/dev/null

echo "SPI Package 008 doctor: PASS"
