from __future__ import annotations

import platform
from typing import Any

from plugins.base import LifecyclePlugin
from plugins.result import PluginResult


class ValidateRequirementsPlugin(LifecyclePlugin):
    key = "validate-requirements"
    name = "Validate Requirements"
    description = "Validate adapter and architecture requirements."

    def execute(
        self,
        *,
        context: dict[str, Any],
        dry_run: bool,
    ) -> PluginResult:
        manifest = context["manifest"]
        adapter = context["adapter"]
        architecture = platform.machine()

        requirements = manifest.get("requirements", {})
        supported_adapters = requirements.get(
            "platformAdapters",
            [],
        )
        supported_architectures = requirements.get(
            "architectures",
            [],
        )

        adapter_valid = (
            not supported_adapters
            or adapter in supported_adapters
        )
        architecture_valid = (
            not supported_architectures
            or architecture in supported_architectures
        )

        success = adapter_valid and architecture_valid

        return PluginResult(
            success=success,
            status=(
                "simulated"
                if success and dry_run
                else "complete"
                if success
                else "failed"
            ),
            changed=False,
            message=(
                "Product requirements satisfied."
                if success
                else "Product requirements not satisfied."
            ),
            details={
                "adapter": adapter,
                "adapterValid": adapter_valid,
                "architecture": architecture,
                "architectureValid": architecture_valid,
                "supportedAdapters": supported_adapters,
                "supportedArchitectures": supported_architectures,
            },
            evidence=[
                {
                    "type": "requirements-validation",
                    "success": success,
                    "adapter": adapter,
                    "architecture": architecture,
                }
            ],
        )
