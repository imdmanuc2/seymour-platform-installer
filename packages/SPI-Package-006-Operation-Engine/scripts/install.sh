#!/usr/bin/env bash
set -euo pipefail

REPO="${1:-/home/umbrel/seymour-platform-installer}"
PACKAGE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
BACKUP="$REPO/.spi-package-backups/package-006-$STAMP"

"$PACKAGE_ROOT/scripts/doctor.sh" "$REPO"

mkdir -p "$BACKUP"
for name in bin lib products docs tests; do
  if [[ -e "$REPO/$name" ]]; then
    cp -a "$REPO/$name" "$BACKUP/"
  fi
done

echo "Backup: $BACKUP"

cp -a "$PACKAGE_ROOT/payload/lib/." "$REPO/lib/"
cp -a "$PACKAGE_ROOT/payload/tests/." "$REPO/tests/"
cp -a "$PACKAGE_ROOT/payload/docs/." "$REPO/docs/"

python3 "$PACKAGE_ROOT/scripts/patch_repository.py" "$REPO"

python3 -m py_compile \
  "$REPO/bin/spi" \
  "$REPO/lib/lifecycle/operation.py" \
  "$REPO/lib/lifecycle/executor.py" \
  "$REPO/lib/state/store.py" \
  "$REPO/tests/test_package_006.py"

echo "SPI Package 006 install: PASS"
echo "No live host changes were performed."
