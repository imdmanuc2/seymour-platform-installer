# SPI Package 008 — Transaction Engine

Adds dry-run transaction IDs, per-step checkpoints, prepare/commit journal
events, rollback planning, and crash-interruption recovery metadata.

## Install

```bash
chmod +x scripts/*.sh
./scripts/doctor.sh
./scripts/install.sh
./scripts/verify.sh
```

No live host changes are performed.
