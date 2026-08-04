from __future__ import annotations
import os

def should_inject_crash(*, plugin_key: str) -> bool:
    return os.environ.get("SPI_TEST_CRASH_PLUGIN", "").strip() == plugin_key
