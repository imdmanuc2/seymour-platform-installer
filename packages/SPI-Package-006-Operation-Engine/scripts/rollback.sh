#!/usr/bin/env bash
set -euo pipefail

REPO="${1:-/home/umbrel/seymour-platform-installer}"
BACKUP="${2:-}"

if [[ -z "$BACKUP" ]]; then
  echo "Usage: $0 <repo> <backup-directory>" >&2
  exit 1
fi
[[ -d "$BACKUP" ]] || { echo "Backup not found: $BACKUP" >&2; exit 1; }

for name in bin lib products docs tests; do
  rm -rf "$REPO/$name"
  if [[ -e "$BACKUP/$name" ]]; then
    cp -a "$BACKUP/$name" "$REPO/"
  fi
done

echo "SPI Package 006 rollback: PASS"
