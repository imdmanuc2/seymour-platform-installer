# SPI Package 006 — Operation Engine

Package 006 formalizes SPI operations as first-class lifecycle records.

## Adds

- Operation schema versioning
- Started/completed timestamps
- Duration tracking
- Structured final outcomes
- Operation summaries
- Latest-operation lookup
- Timeline view
- Failure-safe completion records
- Verification tests

## Install

```bash
chmod +x scripts/*.sh
./scripts/doctor.sh
./scripts/install.sh
./scripts/verify.sh
```

## Safety

Package 006 remains dry-run only. It does not install packages, start services,
modify containers, alter networking or firewalls, reboot the host, or touch
host disks.
