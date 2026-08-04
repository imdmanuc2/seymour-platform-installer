from dataclasses import dataclass, field
from typing import Any

@dataclass(frozen=True)
class Adapter:
    adapter_id: str
    name: str
    description: str
    capabilities: frozenset[str] = field(default_factory=frozenset)
    denied_capabilities: frozenset[str] = field(default_factory=frozenset)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.adapter_id,
            "name": self.name,
            "description": self.description,
            "capabilities": sorted(self.capabilities),
            "deniedCapabilities": sorted(self.denied_capabilities),
        }

    def validate(self, required: list[str]) -> dict[str, Any]:
        requested = sorted(set(required))
        missing = sorted(x for x in requested if x not in self.capabilities)
        denied = sorted(x for x in requested if x in self.denied_capabilities)
        return {
            "adapter": self.adapter_id,
            "compatible": not missing,
            "requiredCapabilities": requested,
            "availableCapabilities": sorted(self.capabilities),
            "missingCapabilities": missing,
            "explicitlyDeniedCapabilities": denied,
        }

ADAPTERS = {
    "umbrel": Adapter(
        "umbrel", "Umbrel", "Umbrel container application platform.",
        frozenset({
            "containers","docker","docker-compose","persistent-storage",
            "app-persistent-storage","postgresql","redis","secrets","identity",
            "app-proxy","reverse-proxy","container-network","healthcheck",
            "logging","metrics","backup","rollback"
        }),
        frozenset({"apt","system-packages","systemd","firewall","host-disk-management","host-reboot"}),
    ),
    "debian": Adapter(
        "debian", "Debian", "Native Debian host adapter.",
        frozenset({
            "containers","docker","docker-compose","system-packages","apt","systemd",
            "persistent-storage","postgresql","redis","secrets","identity",
            "container-network","host-network","healthcheck","logging","metrics",
            "backup","rollback","firewall","host-reboot"
        }),
        frozenset({"host-disk-management"}),
    ),
    "ubuntu": Adapter(
        "ubuntu", "Ubuntu", "Native Ubuntu host adapter.",
        frozenset({
            "containers","docker","docker-compose","system-packages","apt","systemd",
            "persistent-storage","postgresql","redis","secrets","identity",
            "container-network","host-network","healthcheck","logging","metrics",
            "backup","rollback","firewall","host-reboot"
        }),
        frozenset({"host-disk-management"}),
    ),
    "docker": Adapter(
        "docker", "Docker", "Container-only Docker adapter.",
        frozenset({
            "containers","docker","docker-compose","persistent-storage","postgresql",
            "redis","secrets","identity","container-network","healthcheck","logging",
            "metrics","backup","rollback"
        }),
        frozenset({"apt","system-packages","systemd","app-proxy","firewall","host-disk-management","host-reboot"}),
    ),
}

def list_adapters():
    return [ADAPTERS[key].to_dict() for key in sorted(ADAPTERS)]

def require_adapter(adapter_id: str) -> Adapter:
    try:
        return ADAPTERS[adapter_id]
    except KeyError as exc:
        raise KeyError(f"Unknown adapter: {adapter_id}") from exc
