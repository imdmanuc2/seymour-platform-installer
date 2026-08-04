from __future__ import annotations

from typing import Any

from core.platform import detect_platform
from plugins.base import LifecyclePlugin
from plugins.result import PluginResult


class DetectPlatformPlugin(LifecyclePlugin):
    key = "detect-platform"
    name = "Detect Platform"
    description = "Detect the current operating platform and adapter."
    supported_adapters = (
        "umbrel",
        "debian",
        "ubuntu",
        "docker",
    )

    def execute(
        self,
        *,
        context: dict[str, Any],
        dry_run: bool,
    ) -> PluginResult:
        platform_data = detect_platform()["platform"]

        return PluginResult(
            success=True,
            status="simulated" if dry_run else "complete",
            changed=False,
            message=(
                f"Detected {platform_data['adapter']} platform "
                f"on {platform_data['architecture']}"
            ),
            details={
                "platform": platform_data,
                "dryRun": dry_run,
            },
            evidence=[
                {
                    "type": "platform-detection",
                    "adapter": platform_data["adapter"],
                    "architecture": platform_data["architecture"],
                }
            ],
        )
