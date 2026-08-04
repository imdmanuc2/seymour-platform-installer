#!/usr/bin/env bash
set -euo pipefail

REPO="${1:-/home/umbrel/seymour-platform-installer}"

fail() {
  echo "DOCTOR FAIL: $*" >&2
  exit 1
}

[[ -d "$REPO/.git" ]] || fail "Not a Git repository: $REPO"
branch="$(git -C "$REPO" branch --show-current)"
[[ "$branch" == "develop" ]] || fail "Expected develop branch, found: $branch"

required=(
  "bin/spi"
  "lib/state/store.py"
  "lib/lifecycle/executor.py"
  "lib/lifecycle/preflight.py"
  "lib/plugins/defaults.py"
  "tests/test_package_005.py"
)

for relative in "${required[@]}"; do
  [[ -f "$REPO/$relative" ]] || fail "Missing prerequisite: $REPO/$relative"
done

python3 "$REPO/tests/test_package_005.py" >/tmp/spi-package-006-doctor-package-005.txt

echo "SPI Package 006 doctor: PASS"
