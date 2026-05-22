from __future__ import annotations

import numpy as np

from mmwave_v2i_sim.sim_engine.engine import StepSnapshot, VehicleState
from mmwave_v2i_sim.sim_engine.guillotine_packer import PackingResult
from mmwave_v2i_sim.sim_engine.visualize import _unpacked_vehicle_numbers


def test_rsb_1based_index_50_maps_to_vehicle_50_not_51() -> None:
    """Packer emits 1-based RSB indices; stats must show vehicle numbers."""
    vehicles = [
        VehicleState(
            vehicle_id=i,
            position=np.zeros(3),
            route_xy=np.zeros((2, 2)),
            link_state=True,
            theta=0.0,
            phi=0.0,
            theta_bs=0.0,
            theta_ms=0.0,
            rsb=(1, 1),
        )
        for i in range(50)
    ]
    snap = StepSnapshot(
        i_num=1,
        n_vehicle=50,
        base_station_position=np.zeros(3),
        vehicles=vehicles,
        packing=PackingResult(
            data=np.zeros((0, 4)),
            n_rsb_left_unpacked=1,
            ind_rsb_left_unpacked=[50],
            trim_loss=0.5,
        ),
        rb=(100, 100),
        rsb_items=[(1, 1)] * 50,
    )
    assert _unpacked_vehicle_numbers(snap) == [50]
    assert 51 not in _unpacked_vehicle_numbers(snap)
