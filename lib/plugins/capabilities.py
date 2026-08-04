from __future__ import annotations

PLUGIN_CAPABILITY_REQUIREMENTS: dict[str, tuple[str, ...]] = {
    "detect-platform": (),
    "validate-requirements": (),
    "prepare-persistent-storage": ("persistent-storage",),
    "deploy-postgresql": ("postgresql", "persistent-storage"),
    "deploy-miningcore": (
        "containers", "docker", "docker-compose",
        "persistent-storage", "container-network",
    ),
    "generate-identity": ("identity", "secrets"),
    "generate-api-token": ("secrets",),
    "configure-pool": ("persistent-storage", "secrets"),
    "start-services": ("containers", "docker"),
    "verify-health": ("healthcheck", "logging"),
    "register-with-nexus": ("container-network", "identity", "secrets"),
    "collect-diagnostics": ("logging", "healthcheck"),
    "restore-last-known-good-config": ("backup", "rollback", "persistent-storage"),
    "restart-unhealthy-components": ("containers", "docker", "healthcheck"),
    "verify-recovery": ("healthcheck", "logging"),
    "create-backup": ("backup", "persistent-storage"),
    "stage-release": ("persistent-storage",),
    "validate-release": ("healthcheck",),
    "activate-release": ("containers", "docker"),
    "rollback-on-failure": ("rollback", "backup", "persistent-storage"),
}


def plugin_required_capabilities(plugin_key: str) -> list[str]:
    return list(PLUGIN_CAPABILITY_REQUIREMENTS.get(plugin_key, ()))
