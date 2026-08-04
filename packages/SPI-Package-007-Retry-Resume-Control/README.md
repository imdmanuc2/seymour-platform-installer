# SPI Package 007 — Retry, Failure Injection, and Resume Control

Package 007 adds controlled retries, failure injection, paused operations, and safe resume from the failed step.

## Adds

- Retry policy model
- Retry counters and attempt metadata
- Controlled failure injection for tests
- Paused and retrying operation states
- Resume from the first incomplete step
- No duplicate execution of completed steps
- Retry evidence events
- Terminal versus retryable failures

## Install

```bash
chmod +x scripts/*.sh
./scripts/doctor.sh
./scripts/install.sh
./scripts/verify.sh
```

## Safety

Package 007 remains dry-run only. It does not install packages, start services, modify containers, alter networking or firewalls, reboot the host, or touch host disks.
