from __future__ import annotations

import os


def requested_failure_plugin() -> str | None:
    value = os.environ.get("SPI_TEST_FAIL_PLUGIN", "").strip()
    return value or None


def requested_failure_attempts() -> int:
    value = os.environ.get("SPI_TEST_FAIL_ATTEMPTS", "1").strip()
    try:
        attempts = int(value)
    except ValueError:
        return 1
    return max(1, attempts)


def should_inject_failure(
    *,
    plugin_key: str,
    attempt: int,
) -> bool:
    target = requested_failure_plugin()
    if target != plugin_key:
        return False
    return attempt <= requested_failure_attempts()
