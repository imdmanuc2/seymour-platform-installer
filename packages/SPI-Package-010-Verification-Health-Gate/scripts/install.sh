#!/usr/bin/env bash
set -euo pipefail
REPO="${1:-/home/umbrel/seymour-platform-installer}"
PKG="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
BACKUP="$REPO/.spi-package-backups/package-010-$STAMP"
"$PKG/scripts/doctor.sh" "$REPO"
mkdir -p "$BACKUP"
for name in bin lib products docs tests; do
  [[ -e "$REPO/$name" ]] && cp -a "$REPO/$name" "$BACKUP/"
done
echo "Backup: $BACKUP"
cp -a "$PKG/payload/lib/." "$REPO/lib/"
cp -a "$PKG/payload/tests/." "$REPO/tests/"
cp -a "$PKG/payload/docs/." "$REPO/docs/"
python3 "$PKG/scripts/patch_executor.py" "$REPO"
python3 -m py_compile \
  "$REPO/lib/lifecycle/health_gate.py" \
  "$REPO/lib/lifecycle/executor.py" \
  "$REPO/tests/test_package_010.py"
echo "SPI Package 010 install: PASS"
echo "No live host changes were performed."
