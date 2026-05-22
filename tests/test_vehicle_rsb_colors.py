from __future__ import annotations

from mmwave_v2i_sim.sim_engine.visualize import (
    _MAX_RSB_VEHICLE_COLORS,
    _VEHICLE_RSB_COLORS,
    _rsb_color_for_vehicle,
)


def test_fifty_unique_rsb_colors() -> None:
    assert len(_VEHICLE_RSB_COLORS) == _MAX_RSB_VEHICLE_COLORS
    assert len(set(_VEHICLE_RSB_COLORS)) == _MAX_RSB_VEHICLE_COLORS


def test_vehicle_id_maps_to_distinct_color_without_modulo_collision() -> None:
    c0 = _rsb_color_for_vehicle(0)
    c20 = _rsb_color_for_vehicle(20)
    c40 = _rsb_color_for_vehicle(40)
    assert len({c0, c20, c40}) == 3
    assert _rsb_color_for_vehicle(0) == _rsb_color_for_vehicle(0)
    assert _rsb_color_for_vehicle(20) != _rsb_color_for_vehicle(0)
