#!/usr/bin/env bash
set -euo pipefail
REPO="${1:-/home/umbrel/seymour-platform-installer}"
BACKUP="${2:-}"
[[ -n "$BACKUP" ]] || { echo "Usage: $0 <repo> <backup-directory>" >&2; exit 1; }
[[ -d "$BACKUP" ]] || { echo "Backup not found: $BACKUP" >&2; exit 1; }
for name in bin lib products docs tests; do
  rm -rf "$REPO/$name"
  [[ -e "$BACKUP/$name" ]] && cp -a "$BACKUP/$name" "$REPO/"
done
echo "SPI Package 007 rollback: PASS"
