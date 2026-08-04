from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from plugins.result import PluginResult


class LifecyclePlugin(ABC):
    key: str
    name: str
    description: str
    supported_adapters: tuple[str, ...] = ()
    safe_in_dry_run: bool = True

    def metadata(self) -> dict[str, Any]:
        return {
            "key": self.key,
            "name": self.name,
            "description": self.description,
            "supportedAdapters": list(self.supported_adapters),
            "safeInDryRun": self.safe_in_dry_run,
        }

    def supports_adapter(self, adapter: str) -> bool:
        return (
            not self.supported_adapters
            or adapter in self.supported_adapters
        )

    @abstractmethod
    def execute(
        self,
        *,
        context: dict[str, Any],
        dry_run: bool,
    ) -> PluginResult:
        raise NotImplementedError
