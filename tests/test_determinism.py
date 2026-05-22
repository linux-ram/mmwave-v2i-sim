from __future__ import annotations

from pathlib import Path

from mmwave_v2i_sim.config.schema import load_scenario_config
from mmwave_v2i_sim.core.engine import SimulationEngine


def test_engine_is_deterministic_for_same_seed() -> None:
    config_path = Path("configs/scenario_legacy_research.yaml")
    config = load_scenario_config(config_path)

    first = SimulationEngine(config).run().to_dict()
    second = SimulationEngine(config).run().to_dict()

    assert first == second
    assert first["phase_order_valid"] is True
    assert len(first["events"]) == config.run.steps * len(config.run.frame_phases)


def test_seed_change_changes_artifact() -> None:
    config = load_scenario_config(Path("configs/scenario_legacy_research.yaml"))
    baseline = SimulationEngine(config).run().to_dict()

    config.run.seed = 54321
    changed = SimulationEngine(config).run().to_dict()

    assert baseline != changed


def test_phase_sequence_is_ordered_per_step() -> None:
    config = load_scenario_config(Path("configs/scenario_legacy_research.yaml"))
    result = SimulationEngine(config).run().to_dict()
    phases = config.run.frame_phases

    for step in range(config.run.steps):
        step_phases = [e["phase"] for e in result["events"] if e["step"] == step]
        assert step_phases == phases


def test_channel_aggregate_fields_present() -> None:
    config = load_scenario_config(Path("configs/scenario_legacy_research.yaml"))
    result = SimulationEngine(config).run().to_dict()
    bands = {float(b) for b in config.radio.enabled_bands_ghz}

    assert 0.0 <= result["mean_los_ratio"] <= 1.0
    assert set(float(k) for k in result["mean_pathloss_db_by_band"].keys()) == bands
    assert set(float(k) for k in result["mean_sinr_db_by_band"].keys()) == bands
    assert result["scheduler_strategy"] == config.run.scheduler_strategy
    assert result["scheduler_objective"] == config.run.scheduler_objective
