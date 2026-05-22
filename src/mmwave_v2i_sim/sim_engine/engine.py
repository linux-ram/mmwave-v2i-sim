"""Port of vehicleBinPackSimulation.m link/geometry and step engine."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from mmwave_v2i_sim.sim_engine.constants import DELTA_B, DELTA_T, LAMBDA_S, P_LOS_THRESH
from mmwave_v2i_sim.sim_engine.guillotine_packer import PackingResult
from mmwave_v2i_sim.sim_engine.loader import RouteData, load_routes, load_osm_routes
from mmwave_v2i_sim.sim_engine.packing import pack
from mmwave_v2i_sim.sim_engine.rsb import generate_rsb, resource_block_mru_units


@dataclass
class VehicleState:
    vehicle_id: int
    position: np.ndarray
    route_xy: np.ndarray
    link_state: bool
    theta: float
    phi: float
    theta_bs: float
    theta_ms: float
    rsb: tuple[int, int]


@dataclass
class StepSnapshot:
    i_num: int
    n_vehicle: int
    base_station_position: np.ndarray
    vehicles: list[VehicleState]
    packing: PackingResult
    rb: tuple[int, int]
    rsb_items: list[tuple[int, int]]
    packing_algorithm: str = "guillotine"


@dataclass
class _VehicleSetup:
    positions: np.ndarray
    route_xy: np.ndarray
    link_state: np.ndarray
    theta: np.ndarray
    phi: np.ndarray
    theta_bs: np.ndarray
    theta_ms: np.ndarray
    rsb: np.ndarray


def _default_route_data() -> RouteData:
    """Return OSM routes when available; otherwise bundled route file."""
    osm = load_osm_routes()
    return osm if osm is not None else load_routes()


@dataclass
class SimSession:
    route_data: RouteData = field(default_factory=_default_route_data)
    n_vehicle: int = 10
    seed: int = 12345
    packing_algorithm: str = "guillotine"
    p_los_thresh: float = P_LOS_THRESH
    current_i_num: int = field(default=0, init=False)
    rng: np.random.Generator = field(init=False)
    rb: tuple[int, int] = field(init=False)
    trim_history: list[float] = field(default_factory=list, init=False)
    vehicle_setups: list[_VehicleSetup] = field(default_factory=list, init=False)
    max_steps: int = field(default=0, init=False)

    def __post_init__(self) -> None:
        self.reset()

    def reset(self) -> StepSnapshot:
        self.current_i_num = 0
        self.trim_history = []
        self.rng = np.random.default_rng(self.seed)
        self.rb = resource_block_mru_units()
        self._build_vehicle_setups()
        self.max_steps = self._compute_max_steps()
        return self.step()  # type: ignore[return-value]

    def _compute_max_steps(self) -> int:
        """Route length, shortened when all vehicles lose LoS for the remainder."""
        n_min = self.route_data.n_min_samp_of_all_routes
        for step_idx in range(n_min):
            if any(setup.link_state[step_idx] for setup in self.vehicle_setups):
                continue
            if all(
                not setup.link_state[t]
                for setup in self.vehicle_setups
                for t in range(step_idx, n_min)
            ):
                return step_idx + 1
        return n_min

    def step(self) -> StepSnapshot | None:
        if self.current_i_num >= self.max_steps:
            return None
        snap = self._build_snapshot(self.current_i_num)
        self.trim_history.append(snap.packing.trim_loss)
        self.current_i_num += 1
        return snap

    def _build_vehicle_setups(self) -> None:
        bs = self.route_data.base_station_position
        n_min = self.route_data.n_min_samp_of_all_routes
        idx_min = self.route_data.index_veh_min_samples
        self.vehicle_setups = []

        n_routes_available = len(self.route_data.veh_positions)
        for i_veh in range(self.n_vehicle):
            # Cycle routes when n_vehicle exceeds available paths; randomize start offset.
            route_idx = i_veh % n_routes_available
            positions = self.route_data.veh_positions[route_idx].copy()
            if route_idx != idx_min:
                positions = positions[:n_min]
            if positions.shape[0] > 0:
                offset = int(self.rng.integers(0, positions.shape[0]))
                positions = np.roll(positions, offset, axis=0)
            route_xy = positions[:, :2].copy()
            dist = np.tile(bs, (positions.shape[0], 1)) - positions
            tx_rx_sep = np.sqrt(np.sum(dist**2, axis=1))
            p_los = (1.0 - np.exp(-4.0 * tx_rx_sep * LAMBDA_S)) / (4.0 * tx_rx_sep * LAMBDA_S)
            link_state = p_los > self.p_los_thresh
            theta = np.degrees(np.arctan2(dist[:, 1], dist[:, 0]))
            phi = np.degrees(
                np.arctan(dist[:, 2] / np.sqrt(np.sum(dist[:, [0, 1]] ** 2, axis=1)))
            )
            t_series, b_series = generate_rsb(n_min, self.rng)
            rsb = np.round(
                np.column_stack([t_series, b_series]) / np.array([DELTA_T, DELTA_B])
            ).astype(int)
            self.vehicle_setups.append(
                _VehicleSetup(
                    positions=positions,
                    route_xy=route_xy,
                    link_state=link_state,
                    theta=theta,
                    phi=phi,
                    theta_bs=180.0 + theta,
                    theta_ms=theta,
                    rsb=rsb,
                )
            )

    def _build_snapshot(self, step_idx: int) -> StepSnapshot:
        bs = self.route_data.base_station_position
        vehicles: list[VehicleState] = []
        rsb_list: list[tuple[int, int]] = []

        for i_veh, setup in enumerate(self.vehicle_setups):
            pos = setup.positions[step_idx]
            link = bool(setup.link_state[step_idx])
            rsb = veh_rsb_mru_units_from_row(setup.rsb[step_idx])
            vehicles.append(
                VehicleState(
                    vehicle_id=i_veh,
                    position=pos,
                    route_xy=setup.route_xy,
                    link_state=link,
                    theta=float(setup.theta[step_idx]),
                    phi=float(setup.phi[step_idx]),
                    theta_bs=float(setup.theta_bs[step_idx]),
                    theta_ms=float(setup.theta_ms[step_idx]),
                    rsb=rsb,
                )
            )
            if link:
                t_req, b_req = rsb
                t_req = 1 if np.isnan(t_req) or np.isinf(t_req) else max(int(t_req), 1)
                b_req = 1 if np.isnan(b_req) or np.isinf(b_req) else max(int(b_req), 1)
                rsb_list.append((t_req, b_req))

        result = pack(self.rb, rsb_list, self.packing_algorithm)

        return StepSnapshot(
            i_num=step_idx + 1,
            n_vehicle=self.n_vehicle,
            base_station_position=bs,
            vehicles=vehicles,
            packing=result,
            rb=self.rb,
            rsb_items=rsb_list,
            packing_algorithm=self.packing_algorithm,
        )


def veh_rsb_mru_units_from_row(row: np.ndarray) -> tuple[int, int]:
    t_req = int(row[0])
    b_req = int(row[1])
    return t_req, b_req
