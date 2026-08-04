#!/usr/bin/env bash
set -euo pipefail
REPO="${1:-/home/umbrel/seymour-platform-installer}"
BACKUP="${2:-}"
[[ -d "$BACKUP" ]] || { echo "Backup not found: $BACKUP" >&2; exit 1; }
for name in bin lib products docs tests; do
  rm -rf "$REPO/$name"
  [[ -e "$BACKUP/$name" ]] && cp -a "$BACKUP/$name" "$REPO/"
done
echo "SPI Package 009 rollback: PASS"
