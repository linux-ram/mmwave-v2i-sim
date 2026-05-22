from __future__ import annotations

from pathlib import Path

from mmwave_v2i_sim.channel import SimpleChannelModel
from mmwave_v2i_sim.config.schema import load_scenario_config
from mmwave_v2i_sim.mobility import build_mobility_provider


def test_channel_returns_dual_band_metrics() -> None:
    config = load_scenario_config(Path("configs/scenario_legacy_research.yaml"))
    mobility = build_mobility_provider(config)
    channel = SimpleChannelModel(config)

    states = mobility.states_at_step(0)
    snapshots = channel.evaluate_step(states)

    assert len(snapshots) == config.scale.max_vehicles
    bands = set(config.radio.enabled_bands_ghz)
    first = snapshots[0]
    assert set(first.pathloss_db_by_band.keys()) == bands
    assert set(first.sinr_db_by_band.keys()) == bands


def test_channel_is_deterministic_for_same_seed() -> None:
    config = load_scenario_config(Path("configs/scenario_legacy_research.yaml"))
    states = build_mobility_provider(config).states_at_step(1)

    first = SimpleChannelModel(config).evaluate_step(states)
    second = SimpleChannelModel(config).evaluate_step(states)
    assert first == second
