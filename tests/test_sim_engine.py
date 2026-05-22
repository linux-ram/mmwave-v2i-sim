from __future__ import annotations

import numpy as np

from mmwave_v2i_sim.sim_engine.engine import SimSession


def test_n50_vehicles_have_distinct_start_positions() -> None:
    session = SimSession(n_vehicle=50, seed=999)
    session.reset()
    starts = [setup.positions[0, :2].copy() for setup in session.vehicle_setups]
    uniq = {tuple(s) for s in starts}
    assert len(uniq) >= 40, f"Expected diverse starts, got {len(uniq)} unique positions"


def test_sim_ends_when_all_vehicles_los_for_remainder() -> None:
    session = SimSession(n_vehicle=10, seed=42)
    session.reset()
    assert session.max_steps <= session.route_data.n_min_samp_of_all_routes
    steps = 0
    while session.step() is not None:
        steps += 1
    assert steps == session.max_steps - 1


def test_each_run_randomizes_route_start() -> None:
    a = SimSession(n_vehicle=5, seed=100)
    a.reset()
    starts_a = [s.positions[0, :2].copy() for s in a.vehicle_setups]
    b = SimSession(n_vehicle=5, seed=101)
    b.reset()
    starts_b = [s.positions[0, :2].copy() for s in b.vehicle_setups]
    assert not all(
        np.allclose(sa, sb) for sa, sb in zip(starts_a, starts_b, strict=True)
    )


def test_session_restart_resets_trim_history() -> None:
    """reset() clears trim_history; new session starts fresh."""
    session = SimSession(n_vehicle=5, seed=42)
    session.reset()  # reset calls step() once internally
    for _ in range(5):
        nxt = session.step()
        if nxt is None:
            break
    assert len(session.trim_history) > 1
    history_before = len(session.trim_history)
    session.reset()  # calling reset again should clear trim_history and add 1
    assert len(session.trim_history) == 1, (
        f"After reset, trim_history should have 1 entry (from reset's initial step), "
        f"but had {len(session.trim_history)}. Before reset: {history_before}"
    )
