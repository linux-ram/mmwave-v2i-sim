"""Map-matched mobility provider based on route CSV files."""

from __future__ import annotations

from pathlib import Path

import numpy as np

from mmwave_v2i_sim.config.schema import ScenarioConfig
from mmwave_v2i_sim.mobility.base import VehicleState
from mmwave_v2i_sim.mobility.city_presets import resolve_city_preset


class MapMatchedMobilityProvider:
    """Uses precomputed route points in CSV format.

    CSV format (header required):
      vehicle_id,step,x_m,y_m,z_m,speed_mps
    """

    def __init__(self, config: ScenarioConfig) -> None:
        self._config = config
        self._city = resolve_city_preset(config.city.preset)
        self._states_by_step: dict[int, list[VehicleState]] = {}
        source = config.mobility.route_source
        if source is None:
            raise ValueError("map_matched mode requires mobility.route_source")
        self._load(Path(source))

    def _load(self, path: Path) -> None:
        raw = np.genfromtxt(path, delimiter=",", names=True)
        if raw.size == 0:
            return
        rows = np.atleast_1d(raw)
        for row in rows:
            step = int(row["step"])
            state = VehicleState(
                vehicle_id=int(row["vehicle_id"]),
                x_m=float(np.clip(row["x_m"], 0.0, self._city.length_m)),
                y_m=float(np.clip(row["y_m"], 0.0, self._city.width_m)),
                z_m=float(row["z_m"]),
                speed_mps=float(max(row["speed_mps"], 0.0)),
            )
            self._states_by_step.setdefault(step, []).append(state)

    def states_at_step(self, step: int) -> list[VehicleState]:
        return list(self._states_by_step.get(step, []))
