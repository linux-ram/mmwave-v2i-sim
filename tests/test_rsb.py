from __future__ import annotations

import numpy as np

from mmwave_v2i_sim.sim_engine.constants import B_TOT, DELTA_B, DELTA_T, T_TOT
from mmwave_v2i_sim.sim_engine.engine import SimSession
from mmwave_v2i_sim.sim_engine.rsb import generate_rsb, resource_block_mru_units


def test_low_vehicle_count_does_not_force_full_rsb() -> None:
    rng = np.random.default_rng(42)
    t, b = generate_rsb(min_samp_all_routes=20, rng=rng)
    rb_t, rb_b = resource_block_mru_units()
    full_t = int(np.round(T_TOT / DELTA_T))
    full_b = int(np.round(B_TOT / DELTA_B))
    assert not (np.all(t == T_TOT) and np.all(b == B_TOT))
    assert not (np.all(np.round(t / DELTA_T) == full_t) and np.all(np.round(b / DELTA_B) == full_b))


def test_n1_vehicle_trim_loss_not_always_zero() -> None:
    session = SimSession(n_vehicle=1, seed=99)
    session.reset()
    losses: list[float] = []
    while True:
        nxt = session.step()
        if nxt is None:
            break
        losses.append(nxt.packing.trim_loss)
    assert len(losses) > 0
    assert max(losses) > 0.0 or min(losses) < 1.0
    assert not all(loss == 0.0 for loss in losses)
