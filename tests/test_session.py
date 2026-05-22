from __future__ import annotations

from mmwave_v2i_sim.sim_engine.engine import SimSession


def test_sim_session_step_advances_i_num() -> None:
    session = SimSession(n_vehicle=10, seed=12345)
    s0 = session.reset()
    s1 = session.step()
    assert s0 is not None and s1 is not None
    assert s0.i_num == 1
    assert s1.i_num == 2
    assert len(session.trim_history) == 2


def test_sim_session_deterministic_replay() -> None:
    a = SimSession(n_vehicle=10, seed=12345)
    b = SimSession(n_vehicle=10, seed=12345)
    sa = a.reset()
    sb = b.reset()
    for _ in range(5):
        na = a.step()
        nb = b.step()
        assert na is not None and nb is not None
        assert na.packing.trim_loss == nb.packing.trim_loss
