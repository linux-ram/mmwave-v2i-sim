"""Scale and endurance benchmarks for interactive simulation."""

from __future__ import annotations

import time
from pathlib import Path

from mmwave_v2i_sim.config.schema import load_scenario_config
from mmwave_v2i_sim.core.session import SimulationSession


def bench_steps(config_path: Path, n_steps: int, *, max_vehicles: int | None = None) -> float:
    cfg = load_scenario_config(config_path)
    cfg.run.steps = n_steps
    if max_vehicles is not None:
        cfg.scale.max_vehicles = max_vehicles
    session = SimulationSession(cfg)
    session.reset()
    t0 = time.perf_counter()
    for _ in range(n_steps - 1):
        if session.step() is None:
            break
    return time.perf_counter() - t0


if __name__ == "__main__":
    legacy = Path("configs/scenario_legacy_research.yaml")
    scale = Path("configs/scenario_scale_200.yaml")
    profiles = [
        ("50v-legacy-headless", legacy, 50, 50),
        ("200v-legacy-headless", scale, 50, None),
    ]
    for label, path, steps, n_veh in profiles:
        elapsed = bench_steps(path, steps, max_vehicles=n_veh)
        veh = n_veh if n_veh is not None else load_scenario_config(path).scale.max_vehicles
        print(
            f"{label} ({veh} vehicles): {steps} steps in {elapsed:.2f}s "
            f"({elapsed / steps * 1000:.1f} ms/step)"
        )
