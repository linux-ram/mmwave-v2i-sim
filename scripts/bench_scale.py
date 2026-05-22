"""Scale and endurance benchmarks for interactive simulation."""

from __future__ import annotations

import time
from pathlib import Path

from mmwave_v2i_sim.config.schema import load_scenario_config
from mmwave_v2i_sim.core.session import SimulationSession


def bench_steps(config_path: Path, n_steps: int) -> float:
    cfg = load_scenario_config(config_path)
    cfg.run.steps = n_steps
    session = SimulationSession(cfg)
    session.reset()
    t0 = time.perf_counter()
    for _ in range(n_steps - 1):
        if session.step() is None:
            break
    return time.perf_counter() - t0


if __name__ == "__main__":
    base = Path("configs/scenario_minimal.yaml")
    scale = Path("configs/scenario_scale_200.yaml")
    for label, path, steps in [("50v", base, 50), ("200v", scale, 50)]:
        elapsed = bench_steps(path, steps)
        print(f"{label}: {steps} steps in {elapsed:.2f}s ({elapsed / steps * 1000:.1f} ms/step)")
