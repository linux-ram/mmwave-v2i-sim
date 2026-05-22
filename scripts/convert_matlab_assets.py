"""Convert vehicularRoutes.mat to open redistribution formats."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import scipy.io as sio

ROOT = Path(__file__).resolve().parents[1]
MAT = ROOT / "assets" / "vehicularRoutes.mat"
OUT_NPZ = ROOT / "assets" / "vehicular_routes.npz"
OUT_BS = ROOT / "assets" / "base_station.json"


def main() -> None:
    data = sio.loadmat(MAT)
    paths = {f"path{i}": data[f"path{i}"] for i in range(1, 11)}
    bs = data["BS_pos"].reshape(-1).tolist()
    np.savez(OUT_NPZ, **paths)
    OUT_BS.write_text(json.dumps({"BS_pos": bs}, indent=2), encoding="utf-8")
    print(f"Wrote {OUT_NPZ} and {OUT_BS}")


if __name__ == "__main__":
    main()
