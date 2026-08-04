#!/usr/bin/env bash
set -euo pipefail
REPO="${1:-/home/umbrel/seymour-platform-installer}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
BACKUP="$REPO/.spi-package-backups/package-005-$STAMP"
"$ROOT/scripts/doctor.sh" "$REPO"
mkdir -p "$BACKUP"
for name in bin lib products docs tests; do
  [[ -e "$REPO/$name" ]] && cp -a "$REPO/$name" "$BACKUP/"
done
echo "Backup: $BACKUP"
cp -a "$ROOT/payload/lib/." "$REPO/lib/"
cp -a "$ROOT/payload/tests/." "$REPO/tests/"
cp -a "$ROOT/payload/docs/." "$REPO/docs/"
python3 "$ROOT/scripts/patch_cli.py" "$REPO"
python3 -m py_compile \
  "$REPO/bin/spi" \
  "$REPO/lib/plugins/capabilities.py" \
  "$REPO/lib/lifecycle/preflight.py" \
  "$REPO/tests/test_package_005.py"
echo "SPI Package 005 install: PASS"
echo "No live host changes were performed."
