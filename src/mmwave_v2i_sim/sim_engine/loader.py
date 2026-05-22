"""Port of loadVehRouteData.m — plus optional OSM road-snapped routes."""

from __future__ import annotations

from dataclasses import dataclass
import json
import logging
from pathlib import Path

import numpy as np
import scipy.io as sio

ASSETS = Path(__file__).resolve().parents[3] / "assets"
_log = logging.getLogger(__name__)


@dataclass
class RouteData:
    base_station_position: np.ndarray
    veh_positions: list[np.ndarray]
    n_min_samp_of_all_routes: int
    index_veh_min_samples: int

    def vehicle_route_xy(self, veh_idx: int) -> np.ndarray:
        return self.veh_positions[veh_idx][:, :2]

    def position_at(self, veh_idx: int, step_idx: int) -> np.ndarray:
        route = self.veh_positions[veh_idx]
        idx = min(step_idx, route.shape[0] - 1)
        return route[idx]


def _col_xyz(path: np.ndarray) -> np.ndarray:
    return path[:, [1, 2, 3]]


def _flip(path: np.ndarray) -> np.ndarray:
    return np.flipud(_col_xyz(path))


def _noflip(path: np.ndarray) -> np.ndarray:
    return _col_xyz(path)


def load_routes() -> RouteData:
    npz_path = ASSETS / "vehicular_routes.npz"
    mat_path = ASSETS / "vehicularRoutes.mat"
    bs_path = ASSETS / "base_station.json"

    if npz_path.is_file() and bs_path.is_file():
        npz = np.load(npz_path)
        p = {i: npz[f"path{i}"] for i in range(1, 11)}
        bs = np.array(json.loads(bs_path.read_text(encoding="utf-8"))["BS_pos"], dtype=float)
    elif mat_path.is_file():
        data = sio.loadmat(mat_path)
        bs = data["BS_pos"].reshape(3)
        p = {i: data[f"path{i}"] for i in range(1, 11)}
    else:
        raise FileNotFoundError(f"Missing route assets under {ASSETS}")

    plus = np.array([5.0, 5.0, 0.0])
    minus = np.array([-5.0, -5.0, 0.0])

    veh_positions: list[np.ndarray] = [
        _flip(p[1]),
        _noflip(p[2]),
        _flip(p[3]),
        _flip(p[4]),
        _noflip(p[5]),
        _flip(p[6]),
        _flip(p[7]),
        _noflip(p[8]),
        _noflip(p[9]),
        _flip(p[10]),
        _noflip(p[1]),
        _flip(p[2]),
        _noflip(p[3]),
        _noflip(p[4]),
        _flip(p[5]),
        _noflip(p[6]),
        _noflip(p[7]),
        _flip(p[8]),
        _flip(p[9]),
        _noflip(p[10]),
        _noflip(p[1]) + plus,
        _flip(p[2]) + plus,
        _noflip(p[3]) + plus,
        _noflip(p[4]) + plus,
        _flip(p[5]) + plus,
        _noflip(p[6]) + plus,
        _noflip(p[7]) + plus,
        _flip(p[8]) + plus,
        _flip(p[9]) + plus,
        _flip(p[10]) + plus,
        _flip(p[1]) + plus,
        _noflip(p[2]) + plus,
        _flip(p[3]) + plus,
        _flip(p[4]) + plus,
        _noflip(p[5]) + plus,
        _flip(p[6]) + plus,
        _flip(p[7]) + plus,
        _noflip(p[8]) + plus,
        _noflip(p[9]) + plus,
        _noflip(p[10]) + plus,
        _flip(p[1]) + minus,
        _noflip(p[2]) + minus,
        _flip(p[3]) + minus,
        _flip(p[4]) + minus,
        _noflip(p[5]) + minus,
        _flip(p[6]) + minus,
        _flip(p[7]) + minus,
        _noflip(p[8]) + minus,
        _noflip(p[9]) + minus,
        _noflip(p[10]) + minus,
    ]

    sizes = [arr.shape[0] for arr in veh_positions[:10]]
    idx_min = int(np.argmin(sizes))
    n_min = int(min(sizes))

    return RouteData(
        base_station_position=bs,
        veh_positions=veh_positions,
        n_min_samp_of_all_routes=n_min,
        index_veh_min_samples=idx_min,
    )


def load_osm_routes(n_routes: int = 50) -> RouteData | None:
    """Return road-snapped OSM routes for Boston Seaport, or None on failure.

    Requires the optional `osmnx` package (``pip install mmwave-v2i-sim[osm]``).
    Falls back to returning None so callers can use ``load_routes()``.
    The generated routes are cached in ``assets/osm_routes_50.npz`` after
    first download so subsequent calls are instant.
    """
    from mmwave_v2i_sim.sim_engine.osm_routes import (  # noqa: PLC0415
        OSM_AVAILABLE,
        load_or_generate_osm_routes,
    )

    if not OSM_AVAILABLE:
        return None

    try:
        routes = load_or_generate_osm_routes(n_routes=n_routes)
    except Exception as exc:
        _log.warning("OSM route generation failed (%s); using bundled routes", exc)
        return None

    # Determine the base station position from the bundled data (unchanged).
    base = load_routes()

    # n_min_samp = minimum route length across all loaded routes
    sizes = [r.shape[0] for r in routes]
    n_min = int(min(sizes))
    idx_min = int(np.argmin(sizes))

    return RouteData(
        base_station_position=base.base_station_position,
        veh_positions=routes,
        n_min_samp_of_all_routes=n_min,
        index_veh_min_samples=idx_min,
    )
