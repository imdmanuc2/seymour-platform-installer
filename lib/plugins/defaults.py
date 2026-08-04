from __future__ import annotations

from plugins.builtin.platform_detection import DetectPlatformPlugin
from plugins.builtin.requirements import ValidateRequirementsPlugin
from plugins.builtin.simulated import SimulatedLifecyclePlugin
from plugins.registry import PluginRegistry


SIMULATED_PLUGIN_KEYS = (
    "prepare-persistent-storage",
    "deploy-postgresql",
    "deploy-miningcore",
    "generate-identity",
    "generate-api-token",
    "configure-pool",
    "start-services",
    "verify-health",
    "register-with-nexus",
    "collect-diagnostics",
    "restore-last-known-good-config",
    "restart-unhealthy-components",
    "verify-recovery",
    "create-backup",
    "stage-release",
    "validate-release",
    "activate-release",
    "rollback-on-failure",
)


def build_default_registry() -> PluginRegistry:
    registry = PluginRegistry()

    registry.register(DetectPlatformPlugin())
    registry.register(ValidateRequirementsPlugin())

    for key in SIMULATED_PLUGIN_KEYS:
        registry.register(SimulatedLifecyclePlugin(key))

    return registry
