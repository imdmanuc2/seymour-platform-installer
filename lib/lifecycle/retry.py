from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class RetryPolicy:
    max_attempts: int = 1
    backoff_seconds: float = 0.0
    retryable: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


DEFAULT_RETRY_POLICIES: dict[str, RetryPolicy] = {
    "detect-platform": RetryPolicy(max_attempts=1),
    "validate-requirements": RetryPolicy(max_attempts=1),
    "prepare-persistent-storage": RetryPolicy(max_attempts=2, retryable=True),
    "deploy-postgresql": RetryPolicy(max_attempts=3, backoff_seconds=2.0, retryable=True),
    "deploy-miningcore": RetryPolicy(max_attempts=3, backoff_seconds=2.0, retryable=True),
    "generate-identity": RetryPolicy(max_attempts=2, retryable=True),
    "generate-api-token": RetryPolicy(max_attempts=2, retryable=True),
    "configure-pool": RetryPolicy(max_attempts=2, retryable=True),
    "start-services": RetryPolicy(max_attempts=3, backoff_seconds=1.0, retryable=True),
    "verify-health": RetryPolicy(max_attempts=3, backoff_seconds=1.0, retryable=True),
    "register-with-nexus": RetryPolicy(max_attempts=3, backoff_seconds=2.0, retryable=True),
    "collect-diagnostics": RetryPolicy(max_attempts=1),
    "restore-last-known-good-config": RetryPolicy(max_attempts=2, retryable=True),
    "restart-unhealthy-components": RetryPolicy(max_attempts=3, backoff_seconds=1.0, retryable=True),
    "verify-recovery": RetryPolicy(max_attempts=3, backoff_seconds=1.0, retryable=True),
    "create-backup": RetryPolicy(max_attempts=2, retryable=True),
    "stage-release": RetryPolicy(max_attempts=2, retryable=True),
    "validate-release": RetryPolicy(max_attempts=2, retryable=True),
    "activate-release": RetryPolicy(max_attempts=2, retryable=True),
    "rollback-on-failure": RetryPolicy(max_attempts=2, retryable=True),
}


def retry_policy_for(plugin_key: str) -> RetryPolicy:
    return DEFAULT_RETRY_POLICIES.get(plugin_key, RetryPolicy())
