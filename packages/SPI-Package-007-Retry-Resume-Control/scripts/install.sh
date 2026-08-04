#!/usr/bin/env bash
set -euo pipefail

REPO="${1:-/home/umbrel/seymour-platform-installer}"
PACKAGE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
BACKUP="$REPO/.spi-package-backups/package-007-$STAMP"

"$PACKAGE_ROOT/scripts/doctor.sh" "$REPO"
mkdir -p "$BACKUP"
for name in bin lib products docs tests; do
  [[ -e "$REPO/$name" ]] && cp -a "$REPO/$name" "$BACKUP/"
done

echo "Backup: $BACKUP"
cp -a "$PACKAGE_ROOT/payload/lib/." "$REPO/lib/"
cp -a "$PACKAGE_ROOT/payload/tests/." "$REPO/tests/"
cp -a "$PACKAGE_ROOT/payload/docs/." "$REPO/docs/"
python3 "$PACKAGE_ROOT/scripts/patch_executor.py" "$REPO"
python3 "$PACKAGE_ROOT/scripts/patch_cli.py" "$REPO"

python3 -m py_compile \
  "$REPO/bin/spi" \
  "$REPO/lib/lifecycle/executor.py" \
  "$REPO/lib/lifecycle/retry.py" \
  "$REPO/lib/lifecycle/failure_injection.py" \
  "$REPO/tests/test_package_007.py"

echo "SPI Package 007 install: PASS"
echo "No live host changes were performed."
