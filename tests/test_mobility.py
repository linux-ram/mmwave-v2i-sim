from __future__ import annotations

from pathlib import Path

from mmwave_v2i_sim.config.schema import load_scenario_config
from mmwave_v2i_sim.mobility.factory import build_mobility_provider


def test_synthetic_mobility_is_deterministic() -> None:
    config = load_scenario_config(Path("configs/scenario_legacy_research.yaml"))
    provider_a = build_mobility_provider(config)
    provider_b = build_mobility_provider(config)

    states_a = provider_a.states_at_step(3)
    states_b = provider_b.states_at_step(3)
    assert states_a == states_b
    assert len(states_a) == config.scale.max_vehicles


def test_map_matched_provider_loads_csv() -> None:
    config = load_scenario_config(Path("configs/scenario_legacy_research.yaml"))
    config.mobility.mode = "map_matched"
    config.mobility.route_source = "configs/routes_example_mapmatched.csv"

    provider = build_mobility_provider(config)
    step0 = provider.states_at_step(0)
    step2 = provider.states_at_step(2)

    assert len(step0) == 2
    assert len(step2) == 2
    assert step0[0].vehicle_id == 0
    assert step2[1].x_m == 150.0
