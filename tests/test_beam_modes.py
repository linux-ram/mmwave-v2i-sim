from __future__ import annotations

from mmwave_v2i_sim.channel.beam_modes import adjust_sinr_db
from mmwave_v2i_sim.config.schema import ScenarioConfig
from mmwave_v2i_sim.channel.model import SimpleChannelModel
from mmwave_v2i_sim.mobility.base import VehicleState


def test_ideal_beam_beats_codebook_on_average() -> None:
    cfg_code = ScenarioConfig.model_validate(
        {"radio": {"beam_mode": "codebook"}, "scale": {"max_vehicles": 5}}
    )
    cfg_ideal = ScenarioConfig.model_validate(
        {"radio": {"beam_mode": "ideal"}, "scale": {"max_vehicles": 5}}
    )
    states = [
        VehicleState(vehicle_id=i, x_m=100.0 + i * 10, y_m=200.0, z_m=1.5, speed_mps=10.0)
        for i in range(5)
    ]
    sinr_code = [
        s.sinr_db_by_band[28.0]
        for s in SimpleChannelModel(cfg_code).evaluate_step(states, step=3)
    ]
    sinr_ideal = [
        s.sinr_db_by_band[28.0]
        for s in SimpleChannelModel(cfg_ideal).evaluate_step(states, step=3)
    ]
    assert sum(sinr_ideal) / len(sinr_ideal) > sum(sinr_code) / len(sinr_code)


def test_codebook_penalty_varies_with_vehicle() -> None:
    a = adjust_sinr_db(10.0, mode="codebook", vehicle_id=0, step=0)
    b = adjust_sinr_db(10.0, mode="codebook", vehicle_id=5, step=0)
    assert a != b
