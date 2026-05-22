#!/usr/bin/env python3
"""Run a short headless simulation for each open-license city preset."""

from __future__ import annotations

import json
from pathlib import Path

from mmwave_v2i_sim.config.schema import load_scenario_config
from mmwave_v2i_sim.core.engine import SimulationEngine

PRESETS = [
    ("Boston Seaport", Path("configs/scenario_city_boston.yaml")),
    ("San Francisco SoMa", Path("configs/scenario_city_sfo.yaml")),
    ("RTP Campus", Path("configs/scenario_city_rtp.yaml")),
]


def main() -> None:
    rows = []
    for label, cfg_path in PRESETS:
        cfg = load_scenario_config(cfg_path)
        art = SimulationEngine(cfg).run()
        rows.append(
            {
                "label": label,
                "preset": cfg.city.preset,
                "mean_los_ratio": art.mean_los_ratio,
                "mean_trim_loss": art.mean_trim_loss,
                "mean_sinr_28ghz": art.mean_sinr_db_by_band.get(28.0, 0.0),
                "mean_sinr_39ghz": art.mean_sinr_db_by_band.get(39.0, 0.0),
                "beam_mode": cfg.radio.beam_mode,
            }
        )
        print(
            f"{label}: LoS={art.mean_los_ratio:.3f} trim={art.mean_trim_loss:.3f} "
            f"SINR28={art.mean_sinr_db_by_band.get(28.0, 0):.1f} dB beam={cfg.radio.beam_mode}"
        )

    out = Path("artifacts/city_preset_summary.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
