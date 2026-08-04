from __future__ import annotations

from typing import Any

from plugins.base import LifecyclePlugin


class PluginRegistry:
    def __init__(self) -> None:
        self._plugins: dict[str, LifecyclePlugin] = {}

    def register(self, plugin: LifecyclePlugin) -> None:
        if plugin.key in self._plugins:
            raise ValueError(
                f"Plugin already registered: {plugin.key}"
            )

        self._plugins[plugin.key] = plugin

    def get(self, key: str) -> LifecyclePlugin | None:
        return self._plugins.get(key)

    def require(self, key: str) -> LifecyclePlugin:
        plugin = self.get(key)

        if plugin is None:
            raise KeyError(f"Unknown lifecycle plugin: {key}")

        return plugin

    def list_metadata(self) -> list[dict[str, Any]]:
        return [
            self._plugins[key].metadata()
            for key in sorted(self._plugins)
        ]
