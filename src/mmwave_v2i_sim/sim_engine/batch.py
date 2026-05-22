"""Headless batch sweep matching vehicleBinPackSimulation.m Figure 3."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from mmwave_v2i_sim.sim_engine.constants import N_VEHICLE_OPTIONS
from mmwave_v2i_sim.sim_engine.engine import SimSession


@dataclass
class BatchTrialResult:
    n_vehicle: list[int]
    mean_trim_loss: list[float]
    std_trim_loss: list[float]
    all_trim: np.ndarray


def run_density_sweep(num_trials: int = 5, seed: int = 12345) -> BatchTrialResult:
    all_trim = np.zeros((num_trials, len(N_VEHICLE_OPTIONS)))
    for trial in range(num_trials):
        trial_seed = seed + trial
        for expt, n_veh in enumerate(N_VEHICLE_OPTIONS):
            session = SimSession(n_vehicle=n_veh, seed=trial_seed)
            snap = session.reset()
            losses: list[float] = [snap.packing.trim_loss]
            while True:
                nxt = session.step()
                if nxt is None:
                    break
                losses.append(nxt.packing.trim_loss)
            all_trim[trial, expt] = float(np.mean(losses)) if losses else 0.0

    mean = all_trim.mean(axis=0)
    std = all_trim.std(axis=0)
    return BatchTrialResult(
        n_vehicle=list(N_VEHICLE_OPTIONS),
        mean_trim_loss=mean.tolist(),
        std_trim_loss=std.tolist(),
        all_trim=all_trim,
    )
