from __future__ import annotations

import numpy as np

from mmwave_v2i_sim.sim_engine.loader import load_routes


def test_route_loader_has_fifty_routes() -> None:
    data = load_routes()
    assert len(data.veh_positions) == 50
    assert data.n_min_samp_of_all_routes == 119
    assert data.index_veh_min_samples == 4


def test_route_loader_base_station_matches_reference() -> None:
    data = load_routes()
    np.testing.assert_allclose(
        data.base_station_position, [829.78, 425.73, 25.97], rtol=0, atol=0.01
    )


def test_route_loader_first_vehicle_matches_mat_reference() -> None:
    data = load_routes()
    pos0 = data.veh_positions[0][0]
    np.testing.assert_allclose(pos0, [1025.97, 342.231, 2.0], rtol=0, atol=0.01)
