"""CLI for mmWave V2I simulation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from mmwave_v2i_sim.config.schema import SimConfig, ScenarioConfig, load_scenario_config
from mmwave_v2i_sim.sim_engine.batch import run_density_sweep
from mmwave_v2i_sim.sim_engine.engine import SimSession
from mmwave_v2i_sim.ui.app import run_desktop_app


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="mmWave V2I simulator.")
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("configs/scenario_default.yaml"),
        help="Path to scenario configuration YAML",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("artifacts/run_summary.json"),
        help="Where to write run summary artifact",
    )
    parser.add_argument(
        "--gui",
        action="store_true",
        help="Launch desktop GUI (Figure 1 + Figure 2)",
    )
    parser.add_argument(
        "--batch",
        action="store_true",
        help="Run Figure 3-style vehicle density sweep headlessly",
    )
    return parser


def _sim_config(config: ScenarioConfig) -> SimConfig:
    return config.matlab


def main() -> None:
    args = build_parser().parse_args()
    config = load_scenario_config(args.config)
    sim_cfg = _sim_config(config)

    if args.gui:
        run_desktop_app(sim_cfg)
        return

    if args.batch:
        result = run_density_sweep(num_trials=sim_cfg.num_trials, seed=sim_cfg.seed)
        artifact = {
            "engine": "sim_engine",
            "n_vehicle": result.n_vehicle,
            "mean_trim_loss": result.mean_trim_loss,
            "std_trim_loss": result.std_trim_loss,
        }
    else:
        session = SimSession(n_vehicle=sim_cfg.n_vehicle, seed=sim_cfg.seed)
        snap = session.reset()
        steps = [snap.to_dict() if hasattr(snap, "to_dict") else _snap_dict(snap)]
        while True:
            nxt = session.step()
            if nxt is None:
                break
            steps.append(_snap_dict(nxt))
        artifact = {
            "engine": "sim_engine",
            "n_vehicle": sim_cfg.n_vehicle,
            "seed": sim_cfg.seed,
            "steps_run": len(steps),
            "trim_history": session.trim_history,
            "final_trim_loss": session.trim_history[-1] if session.trim_history else None,
        }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as handle:
        json.dump(artifact, handle, indent=2, sort_keys=True)
    print(json.dumps(artifact, indent=2, sort_keys=True))


def _snap_dict(snap: object) -> dict[str, object]:
    from mmwave_v2i_sim.sim_engine.engine import StepSnapshot

    assert isinstance(snap, StepSnapshot)
    return {
        "i_num": snap.i_num,
        "n_vehicle": snap.n_vehicle,
        "trim_loss": snap.packing.trim_loss,
        "n_rsb_unpacked": snap.packing.n_rsb_left_unpacked,
        "rb": list(snap.rb),
    }


if __name__ == "__main__":
    main()
