"""Deterministic synthetic mobility provider."""

from __future__ import annotations

import math

import numpy as np

from mmwave_v2i_sim.config.schema import ScenarioConfig
from mmwave_v2i_sim.mobility.base import VehicleState
from mmwave_v2i_sim.mobility.city_presets import resolve_city_preset


class SyntheticMobilityProvider:
    def __init__(self, config: ScenarioConfig) -> None:
        self._config = config
        self._rng = np.random.default_rng(config.run.seed + 101)
        self._n_vehicles = config.scale.max_vehicles
        self._city = resolve_city_preset(config.city.preset)

        self._initial_x = self._rng.uniform(0.0, self._city.length_m, size=self._n_vehicles)
        self._lane_y = self._rng.uniform(0.0, self._city.width_m, size=self._n_vehicles)
        self._speed = np.clip(
            self._rng.normal(
                loc=config.mobility.speed_mps_mean,
                scale=config.mobility.speed_mps_std,
                size=self._n_vehicles,
            ),
            a_min=1.0,
            a_max=35.0,
        )

    def states_at_step(self, step: int) -> list[VehicleState]:
        t_s = step * self._config.run.timestep_s
        states: list[VehicleState] = []
        for i in range(self._n_vehicles):
            x = (self._initial_x[i] + self._speed[i] * t_s) % self._city.length_m
            y = self._lane_y[i] + 3.0 * math.sin(0.1 * t_s + (i * 0.3))
            y = float(np.clip(y, 0.0, self._city.width_m))
            states.append(
                VehicleState(
                    vehicle_id=i,
                    x_m=float(x),
                    y_m=y,
                    z_m=1.5,
                    speed_mps=float(self._speed[i]),
                )
            )
        return states
