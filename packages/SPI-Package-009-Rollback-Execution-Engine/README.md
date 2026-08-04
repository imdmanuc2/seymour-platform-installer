# SPI Package 009 — Rollback Execution Engine

Adds dry-run rollback execution for transaction rollback plans.

## Install

```bash
chmod +x scripts/*.sh
./scripts/doctor.sh
./scripts/install.sh
./scripts/verify.sh
```

## Adds

- Rollback execution records
- Per-checkpoint rollback state
- Rollback pause/resume
- Rollback timeline evidence
- Double-rollback prevention
- `spi operation rollback <operation-id>`
- `spi operation rollback-status <operation-id>`

Package 009 remains dry-run only and performs no live host changes.
