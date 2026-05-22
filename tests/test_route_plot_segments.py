from __future__ import annotations

import numpy as np

from mmwave_v2i_sim.sim_engine.visualize import _route_xy_plot_segments


def test_route_segments_break_long_jumps() -> None:
    xy = np.array([[0.0, 0.0], [10.0, 0.0], [500.0, 400.0], [510.0, 400.0]])
    seg = _route_xy_plot_segments(xy)
    assert np.isnan(seg[2, 0])
    assert seg[1, 0] == 10.0
    assert seg[3, 0] == 500.0
