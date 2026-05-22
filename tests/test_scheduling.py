from __future__ import annotations

from pathlib import Path

from mmwave_v2i_sim.config.schema import load_scenario_config
from mmwave_v2i_sim.core.engine import SimulationEngine
from mmwave_v2i_sim.plugins.registry import PluginRegistry
from mmwave_v2i_sim.scheduling import register_builtin_strategies


def test_builtin_strategies_are_registered() -> None:
    registry = PluginRegistry()
    register_builtin_strategies(registry)
    assert registry.names() == ["latency_aware", "max_cqi", "proportional_fair"]


def test_strategy_switch_changes_outcome() -> None:
    cfg = load_scenario_config(Path("configs/scenario_legacy_research.yaml"))

    cfg.run.scheduler_strategy = "max_cqi"
    max_cqi = SimulationEngine(cfg).run().to_dict()

    cfg.run.scheduler_strategy = "latency_aware"
    latency = SimulationEngine(cfg).run().to_dict()

    assert max_cqi["scheduler_strategy"] == "max_cqi"
    assert latency["scheduler_strategy"] == "latency_aware"
    assert max_cqi["mean_utilization"] != latency["mean_utilization"]
