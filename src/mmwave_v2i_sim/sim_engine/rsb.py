"""Port of generateRSB.m and MRU/RB sizing."""

from __future__ import annotations

import numpy as np

from mmwave_v2i_sim.sim_engine.constants import B_TOT, DELTA_B, DELTA_T, T_TOT


def resource_block_mru_units() -> tuple[int, int]:
    rb = np.round(np.array([T_TOT, B_TOT]) / np.array([DELTA_T, DELTA_B])).astype(int)
    return int(rb[0]), int(rb[1])


def generate_rsb(
    min_samp_all_routes: int,
    rng: np.random.Generator,
) -> tuple[np.ndarray, np.ndarray]:
    """Generate per-step RSB time/bandwidth series (randomized, not full-RB)."""
    t = np.zeros(min_samp_all_routes, dtype=float)
    b = np.zeros(min_samp_all_routes, dtype=float)
    for i in range(min_samp_all_routes):
        t[i] = 0.1 + 0.8 * rng.random()
        b[i] = 1e8 + (1e9 - 2e8) * rng.random()
    return t, b


def veh_rsb_mru_units(t: np.ndarray, b: np.ndarray, step_idx: int) -> tuple[int, int]:
    idx = min(step_idx, len(t) - 1)
    return int(np.round(t[idx] / DELTA_T)), int(np.round(b[idx] / DELTA_B))
