#!/usr/bin/env bash
set -euo pipefail
REPO="${1:-/home/umbrel/seymour-platform-installer}"
fail(){ echo "DOCTOR FAIL: $*" >&2; exit 1; }
[[ -d "$REPO/.git" ]] || fail "Not a Git repository: $REPO"
branch="$(git -C "$REPO" branch --show-current)"
[[ "$branch" == "develop" ]] || fail "Expected develop branch, found: $branch"
for relative in \
  bin/spi \
  lib/adapters/model.py \
  lib/core/compatibility.py \
  lib/plugins/base.py \
  lib/plugins/defaults.py \
  products/seymour-miningcore/product.json \
  tests/test_package_004.py; do
  [[ -f "$REPO/$relative" ]] || fail "Missing prerequisite: $REPO/$relative"
done
grep -q 'from adapters.model import' "$REPO/bin/spi" || fail "CLI is not using Package 004 adapter model"
python3 "$REPO/tests/test_package_004.py" >/tmp/spi-package-005-doctor.txt
echo "SPI Package 005 doctor: PASS"
