# Retry, Failure Injection, and Resume Control

SPI records an attempt count for each lifecycle step and applies a retry policy before deciding whether an operation should continue, pause, or fail.

## Status transitions

- `running`
- `retrying`
- `paused`
- `failed`
- `simulated`

## Resume behavior

A resumed operation starts from the first step whose status is not `simulated` or `complete`. Previously completed steps are not executed again.

## Test-only failure injection

Package 007 supports controlled test failures through environment variables:

```bash
SPI_TEST_FAIL_PLUGIN=verify-health
SPI_TEST_FAIL_ATTEMPTS=1
```

These variables are intended for verification only.
