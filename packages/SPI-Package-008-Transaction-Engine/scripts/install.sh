#!/usr/bin/env bash
set -euo pipefail
REPO="${1:-/home/umbrel/seymour-platform-installer}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
BACKUP="$REPO/.spi-package-backups/package-008-$STAMP"

"$ROOT/scripts/doctor.sh" "$REPO"

mkdir -p "$BACKUP"
for name in bin lib products docs tests; do
  [[ -e "$REPO/$name" ]] && cp -a "$REPO/$name" "$BACKUP/"
done
echo "Backup: $BACKUP"

cp -a "$ROOT/payload/lib/." "$REPO/lib/"
cp -a "$ROOT/payload/tests/." "$REPO/tests/"
cp -a "$ROOT/payload/docs/." "$REPO/docs/"

python3 "$ROOT/scripts/patch_state.py" "$REPO"
python3 "$ROOT/scripts/patch_executor.py" "$REPO"

python3 -m py_compile \
  "$REPO/lib/lifecycle/transaction.py" \
  "$REPO/lib/lifecycle/crash_injection.py" \
  "$REPO/lib/lifecycle/executor.py" \
  "$REPO/lib/state/store.py" \
  "$REPO/tests/test_package_008.py"

echo "SPI Package 008 install: PASS"
echo "No live host changes were performed."
