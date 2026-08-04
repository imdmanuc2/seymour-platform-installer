#!/usr/bin/env bash
set -euo pipefail

REPO="${1:-/home/umbrel/seymour-platform-installer}"
fail() { echo "DOCTOR FAIL: $*" >&2; exit 1; }

[[ -d "$REPO/.git" ]] || fail "Not a Git repository: $REPO"
branch="$(git -C "$REPO" branch --show-current)"
[[ "$branch" == "develop" ]] || fail "Expected develop branch, found: $branch"

required=(
  "bin/spi"
  "lib/lifecycle/executor.py"
  "lib/lifecycle/preflight.py"
  "lib/plugins/registry.py"
  "lib/state/store.py"
  "tests/test_package_006.py"
)
for relative in "${required[@]}"; do
  [[ -f "$REPO/$relative" ]] || fail "Missing prerequisite: $REPO/$relative"
done

python3 "$REPO/tests/test_package_006.py" >/tmp/spi-package-007-doctor-package-006.txt

echo "SPI Package 007 doctor: PASS"
