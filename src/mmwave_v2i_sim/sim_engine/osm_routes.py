"""OSM road-snapped routes for Boston Seaport (optional, requires osmnx).

If osmnx is unavailable the module can still be imported; callers check
`OSM_AVAILABLE` before calling any function, and `load_osm_routes()` in
loader.py will fall back to the bundled vehicularRoutes.mat paths.
"""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np

# Boston Seaport centre used by the original MATLAB data.
BSP_CENTER_LAT: float = 42.3522
BSP_CENTER_LON: float = -71.0465
BSP_RADIUS_M: float = 700.0

# sim coordinate frame limits (from constants.py – avoid circular import)
_MAP_XMIN, _MAP_XMAX = 50.0, 1069.0
_MAP_YMIN, _MAP_YMAX = -50.0, 620.0

# Cache location
_ASSETS = Path(__file__).resolve().parents[3] / "assets"
_CACHE_GRAPHML = _ASSETS / "osm_road_graph.graphml"
_CACHE_NPZ = _ASSETS / "osm_routes_50.npz"

try:
    import osmnx as ox  # type: ignore[import]
    import networkx as nx  # type: ignore[import]
    OSM_AVAILABLE = True
except ImportError:
    OSM_AVAILABLE = False


# ---------------------------------------------------------------------------
# Projection helpers
# ---------------------------------------------------------------------------

def _latlon_to_local(lat: float, lon: float) -> tuple[float, float]:
    """Convert WGS-84 to local metres centred on BSP_CENTER_LAT/LON."""
    R = 6_371_000.0  # earth radius in metres
    dlat = math.radians(lat - BSP_CENTER_LAT)
    dlon = math.radians(lon - BSP_CENTER_LON)
    x = R * dlon * math.cos(math.radians(BSP_CENTER_LAT))
    y = R * dlat
    # Shift from centred-at-zero to the sim frame origin
    cx = (_MAP_XMIN + _MAP_XMAX) / 2.0
    cy = (_MAP_YMIN + _MAP_YMAX) / 2.0
    return x + cx, y + cy


# ---------------------------------------------------------------------------
# Graph / route building
# ---------------------------------------------------------------------------

def _fetch_or_load_graph():  # type: ignore[return]
    """Return an OSM driveable graph, loading from cache if present."""
    if not OSM_AVAILABLE:
        raise ImportError("osmnx is required for OSM route generation")

    if _CACHE_GRAPHML.is_file():
        G = ox.load_graphml(str(_CACHE_GRAPHML))  # type: ignore[attr-defined]
    else:
        G = ox.graph_from_point(  # type: ignore[attr-defined]
            (BSP_CENTER_LAT, BSP_CENTER_LON),
            dist=BSP_RADIUS_M,
            network_type="drive",
            simplify=True,
        )
        _ASSETS.mkdir(parents=True, exist_ok=True)
        ox.save_graphml(G, filepath=str(_CACHE_GRAPHML))  # type: ignore[attr-defined]
    return G


def _node_to_local(G, node_id: int) -> tuple[float, float]:  # type: ignore[type-arg]
    data = G.nodes[node_id]
    return _latlon_to_local(data["y"], data["x"])


def _route_to_xyz(G, path_nodes: list[int]) -> np.ndarray:  # type: ignore[type-arg]
    """Return Nx3 array of x,y,z for a node-list route."""
    pts = []
    for nid in path_nodes:
        x, y = _node_to_local(G, nid)
        pts.append([x, y, 0.0])
    return np.array(pts, dtype=float)


def _interpolate_route(route: np.ndarray, n_steps: int) -> np.ndarray:
    """Linearly interpolate a route to exactly n_steps samples."""
    if len(route) < 2:
        return np.tile(route[0] if len(route) else [0, 0, 0], (n_steps, 1))
    distances = np.cumsum(
        np.concatenate([[0], np.linalg.norm(np.diff(route[:, :2], axis=0), axis=1)])
    )
    total_dist = distances[-1]
    if total_dist < 1e-6:
        return np.tile(route[0], (n_steps, 1))
    interp_dists = np.linspace(0, total_dist, n_steps)
    interp = np.stack([
        np.interp(interp_dists, distances, route[:, col])
        for col in range(route.shape[1])
    ], axis=1)
    return interp


def generate_osm_routes(n_routes: int = 50, n_steps: int = 200) -> list[np.ndarray]:
    """Generate `n_routes` road-snapped route arrays of shape (n_steps, 3).

    Downloads the OSM graph (or loads from cache), picks n_routes distinct
    origin-destination intersection pairs, finds shortest-path routes, and
    interpolates each to n_steps samples.
    """
    G = _fetch_or_load_graph()
    nodes = list(G.nodes)
    rng = np.random.default_rng(42)  # deterministic — same routes every run

    # Filter to nodes inside the sim frame with some padding
    pad = 50.0
    valid_nodes = [
        n for n in nodes
        if (_MAP_XMIN - pad <= _node_to_local(G, n)[0] <= _MAP_XMAX + pad
            and _MAP_YMIN - pad <= _node_to_local(G, n)[1] <= _MAP_YMAX + pad)
    ]
    if len(valid_nodes) < 4:
        valid_nodes = nodes  # fall back to all nodes

    routes: list[np.ndarray] = []
    tried = 0
    idx_pool = list(range(len(valid_nodes)))
    rng.shuffle(idx_pool)

    pool_iter = iter(idx_pool)
    while len(routes) < n_routes and tried < 10 * n_routes:
        tried += 1
        try:
            src_idx = next(pool_iter) % len(valid_nodes)
            dst_idx = (src_idx + len(valid_nodes) // (n_routes + 1) + tried) % len(valid_nodes)
            src = valid_nodes[src_idx]
            dst = valid_nodes[dst_idx]
            if src == dst:
                continue
            path_nodes = nx.shortest_path(G, src, dst, weight="length")
            if len(path_nodes) < 2:
                continue
            raw = _route_to_xyz(G, path_nodes)
            routes.append(_interpolate_route(raw, n_steps))
        except Exception:
            continue

    if not routes:
        raise RuntimeError("OSM route generation found no valid paths")

    while len(routes) < n_routes:
        routes.append(routes[len(routes) % len(routes)][::-1])

    return routes[:n_routes]


def load_or_generate_osm_routes(n_routes: int = 50, n_steps: int = 200) -> list[np.ndarray]:
    """Return cached routes if available, otherwise generate and cache them."""
    if _CACHE_NPZ.is_file():
        npz = np.load(_CACHE_NPZ)
        return [npz[f"route{i}"] for i in range(int(npz["n_routes"]))]

    routes = generate_osm_routes(n_routes=n_routes, n_steps=n_steps)
    save_dict = {f"route{i}": r for i, r in enumerate(routes)}
    save_dict["n_routes"] = np.array(len(routes))
    _ASSETS.mkdir(parents=True, exist_ok=True)
    np.savez(_CACHE_NPZ, **save_dict)
    return routes
