---
name: m6 — Interactive scale and stress harness
about: Post-v0.1 performance and stability milestone
title: "[m6] Interactive 200-vehicle scale and stress harness"
labels: milestone:m6, enhancement
---

## Goal

Meet interactive scale targets from the program milestone plan.

## Acceptance criteria

- [ ] GUI profile supporting ~200 vehicles at agreed minimum frame rate
- [ ] `scripts/bench_scale.py` documented with reference hardware budgets
- [ ] Stress/endurance test (e.g. 1-hour simulated run) in CI or documented manual harness
- [ ] `tests/test_scale.py` gated in CI for regression

## Context

v0.1 GUI caps at 50 vehicles (`N_VEHICLE_OPTIONS`). Legacy `configs/scenario_scale_200.yaml` supports headless 200-vehicle runs via `core/`.
