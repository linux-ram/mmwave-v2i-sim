from __future__ import annotations

import pytest

from mmwave_v2i_sim.plugins.base import AllocationInput, AllocationResult, SchedulerPackingPlugin
from mmwave_v2i_sim.plugins.registry import PluginRegistry


class DummyPlugin(SchedulerPackingPlugin):
    @property
    def plugin_name(self) -> str:
        return "dummy"

    def allocate(self, data: AllocationInput) -> AllocationResult:
        return AllocationResult(
            accepted_requests=len(data.requests),
            rejected_requests=0,
            utilization=1.0,
        )


def test_registry_register_and_resolve() -> None:
    registry = PluginRegistry()
    plugin = DummyPlugin()
    registry.register(plugin)

    assert registry.names() == ["dummy"]
    assert registry.resolve("dummy") is plugin


def test_registry_rejects_duplicate_names() -> None:
    registry = PluginRegistry()
    registry.register(DummyPlugin())
    with pytest.raises(ValueError):
        registry.register(DummyPlugin())
