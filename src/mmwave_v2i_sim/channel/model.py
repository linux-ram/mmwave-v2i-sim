"""Deterministic dual-band channel abstraction with geometric LOS checks."""

from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np

from mmwave_v2i_sim.channel.beam_modes import adjust_sinr_db
from mmwave_v2i_sim.config.schema import ScenarioConfig
from mmwave_v2i_sim.mobility.base import VehicleState


@dataclass(frozen=True)
class ChannelSnapshot:
    vehicle_id: int
    base_station_id: int
    distance_m: float
    is_los: bool
    blockage_ratio: float
    pathloss_db_by_band: dict[float, float]
    sinr_db_by_band: dict[float, float]


class SimpleChannelModel:
    """3D LOS and path-loss abstraction inspired by 3GPP-style system simulations."""

    def __init__(self, config: ScenarioConfig) -> None:
        self._config = config
        self._rng = np.random.default_rng(config.run.seed + 202)
        self._buildings = self._generate_building_blocks()
        self._bs_positions = self._generate_base_stations()

    @property
    def base_station_positions(self) -> list[tuple[float, float, float]]:
        return list(self._bs_positions)

    def _generate_base_stations(self) -> list[tuple[float, float, float]]:
        n_bs = self._config.scale.max_base_stations
        length = self._config.city.length_m
        width = self._config.city.width_m
        positions: list[tuple[float, float, float]] = []
        for idx in range(n_bs):
            frac = (idx + 1) / (n_bs + 1)
            x = frac * length
            y = (1.0 - frac) * width
            z = 8.0
            positions.append((x, y, z))
        return positions

    def _generate_building_blocks(self) -> list[tuple[float, float, float, float, float]]:
        length = self._config.city.length_m
        width = self._config.city.width_m
        n_blocks = 16
        blocks: list[tuple[float, float, float, float, float]] = []
        for _ in range(n_blocks):
            w = float(self._rng.uniform(20.0, 80.0))
            h = float(self._rng.uniform(20.0, 80.0))
            x = float(self._rng.uniform(0.0, max(length - w, 1.0)))
            y = float(self._rng.uniform(0.0, max(width - h, 1.0)))
            z_top = float(self._rng.uniform(12.0, 45.0))
            blocks.append((x, y, x + w, y + h, z_top))
        return blocks

    @staticmethod
    def _distance_3d(a: tuple[float, float, float], b: tuple[float, float, float]) -> float:
        return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2)

    def _is_los(self, bs: tuple[float, float, float], veh: tuple[float, float, float]) -> bool:
        # Coarse segment sampling intersection against axis-aligned building blocks.
        sx, sy, sz = bs
        ex, ey, ez = veh
        samples = 20
        for i in range(1, samples):
            t = i / samples
            x = sx + (ex - sx) * t
            y = sy + (ey - sy) * t
            z = sz + (ez - sz) * t
            for bx0, by0, bx1, by1, bz in self._buildings:
                if bx0 <= x <= bx1 and by0 <= y <= by1 and z <= bz:
                    return False
        return True

    @staticmethod
    def _pathloss_db(distance_m: float, band_ghz: float, is_los: bool) -> float:
        d = max(distance_m, 1.0)
        base = 32.4 + 20.0 * math.log10(d) + 20.0 * math.log10(band_ghz)
        nlos_penalty = 20.0 if not is_los else 0.0
        return base + nlos_penalty

    @staticmethod
    def _sinr_db(pathloss_db: float, is_los: bool) -> float:
        # Simplified deterministic abstraction: higher path-loss => lower SINR.
        rx_margin = 95.0 - pathloss_db
        link_bonus = 6.0 if is_los else -4.0
        return rx_margin + link_bonus

    def evaluate_step(
        self, states: list[VehicleState], *, step: int = 0
    ) -> list[ChannelSnapshot]:
        snapshots: list[ChannelSnapshot] = []
        if not states:
            return snapshots

        for vehicle in states:
            veh_pos = (vehicle.x_m, vehicle.y_m, vehicle.z_m)
            distances = [self._distance_3d(veh_pos, bs_pos) for bs_pos in self._bs_positions]
            best_bs_id = int(np.argmin(distances))
            bs_pos = self._bs_positions[best_bs_id]
            distance = distances[best_bs_id]
            los = self._is_los(bs_pos, veh_pos)
            blockage_ratio = 0.0 if los else 1.0

            pathloss_by_band: dict[float, float] = {}
            sinr_by_band: dict[float, float] = {}
            beam_mode = self._config.radio.beam_mode
            for band in self._config.radio.enabled_bands_ghz:
                pl = self._pathloss_db(distance, band, los)
                pathloss_by_band[band] = pl
                base_sinr = self._sinr_db(pl, los)
                sinr_by_band[band] = adjust_sinr_db(
                    base_sinr,
                    mode=beam_mode,
                    vehicle_id=vehicle.vehicle_id,
                    step=step,
                )

            snapshots.append(
                ChannelSnapshot(
                    vehicle_id=vehicle.vehicle_id,
                    base_station_id=best_bs_id,
                    distance_m=float(distance),
                    is_los=los,
                    blockage_ratio=float(blockage_ratio),
                    pathloss_db_by_band=pathloss_by_band,
                    sinr_db_by_band=sinr_by_band,
                )
            )
        return snapshots
