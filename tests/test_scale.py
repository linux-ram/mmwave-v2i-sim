from __future__ import annotations

import time
from pathlib import Path

from mmwave_v2i_sim.config.schema import load_scenario_config
from mmwave_v2i_sim.core.session import SimulationSession


def test_scale_200_profile_completes_under_budget() -> None:
    cfg = load_scenario_config(Path("configs/scenario_legacy_research.yaml"))
    cfg.run.steps = 30
    session = SimulationSession(cfg)
    session.reset()
    t0 = time.perf_counter()
    for _ in range(29):
        assert session.step() is not None
    elapsed = time.perf_counter() - t0
    assert elapsed < 30.0


def test_route_history_is_capped() -> None:
    cfg = load_scenario_config(Path("configs/scenario_legacy_research.yaml"))
    cfg.run.steps = 200
    cfg.render.max_route_points = 50
    session = SimulationSession(cfg)
    session.reset()
    for _ in range(100):
        session.step()
    for route in session.route_history.values():
        assert len(route) <= 50
