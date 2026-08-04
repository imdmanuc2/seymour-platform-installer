from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class PluginResult:
    success: bool
    status: str
    changed: bool = False
    message: str = ""
    details: dict[str, Any] = field(default_factory=dict)
    evidence: list[dict[str, Any]] = field(default_factory=list)
    retryable: bool = False
    rollback_available: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
