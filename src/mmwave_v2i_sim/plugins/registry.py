"""Plugin registry to support researcher plug-and-play experiments."""

from __future__ import annotations

from mmwave_v2i_sim.plugins.base import SchedulerPackingPlugin


class PluginRegistry:
    def __init__(self) -> None:
        self._plugins: dict[str, SchedulerPackingPlugin] = {}

    def register(self, plugin: SchedulerPackingPlugin) -> None:
        name = plugin.plugin_name
        if name in self._plugins:
            raise ValueError(f"Plugin already registered: {name}")
        self._plugins[name] = plugin

    def resolve(self, name: str) -> SchedulerPackingPlugin:
        try:
            return self._plugins[name]
        except KeyError as exc:
            available = ", ".join(sorted(self._plugins))
            raise KeyError(f"Unknown plugin '{name}'. Available: {available}") from exc

    def names(self) -> list[str]:
        return sorted(self._plugins)
