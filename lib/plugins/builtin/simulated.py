from __future__ import annotations

from typing import Any

from plugins.base import LifecyclePlugin
from plugins.result import PluginResult


class SimulatedLifecyclePlugin(LifecyclePlugin):
    def __init__(self, key: str) -> None:
        self.key = key
        self.name = key.replace("-", " ").title()
        self.description = (
            "Dry-run placeholder for a lifecycle plugin "
            "that has not yet received a live implementation."
        )

    def execute(
        self,
        *,
        context: dict[str, Any],
        dry_run: bool,
    ) -> PluginResult:
        if not dry_run:
            return PluginResult(
                success=False,
                status="blocked",
                changed=False,
                message=(
                    f"Plugin {self.key} has no live implementation."
                ),
                retryable=False,
            )

        return PluginResult(
            success=True,
            status="simulated",
            changed=False,
            message=f"Simulated lifecycle step: {self.key}",
            details={
                "plugin": self.key,
                "changesApplied": False,
            },
            evidence=[
                {
                    "type": "plugin-simulation",
                    "plugin": self.key,
                    "changesApplied": False,
                }
            ],
        )
