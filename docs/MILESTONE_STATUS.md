# Program milestone status (v0.2 checkpoint)

| ID | Milestone | Status | Notes |
|----|-----------|--------|-------|
| m0 | Baseline & reproducibility | **Done** | CI, lockfile, 70+ tests |
| m1 | Core simulation engine | **Done** (v0.2) | `sim_engine` + legacy `core/` + ZIP export |
| m2 | Mobility & city scene | **Done** (simplified) | Boston/SFO/RTP presets, `demo_city_presets.py`, [CITY_PRESETS.md](CITY_PRESETS.md) |
| m3 | Channel, LOS, beam | **Done** (simplified) | 3D geometric LOS, 28/39 GHz, `codebook` / `ideal` beam modes |
| m4 | Scheduler / packing | **Done** | Guillotine, Shelf, MaxRects |
| m5 | Desktop GUI | **Done** (v0.1 scope) | 2D parity GUI; 3D/KPI → issue #1 |
| m6 | Scale & stability | **Partial** | GUI ≤50 veh; 200 headless legacy |
| m7 | Validation | **Done** | sim_engine validation gate |
| m8 | Release readiness | **Done** | Public repo, README visuals, paper PDF |
| m9 | IEEE paper | **Done** (v0.2) | `paper/main.tex`, figures, `paper/main.pdf` when built |

Post-v0.2 optional work: GitHub issues [#1](https://github.com/linux-ram/mmwave-v2i-sim/issues/1)–[#3](https://github.com/linux-ram/mmwave-v2i-sim/issues/3).
