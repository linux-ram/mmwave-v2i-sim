# Validation Report

## sim_engine (primary, MATLAB parity)

| Vehicles | Trim mean | Trim std |
|---:|---:|---:|
| 1 | 0.7617 | 0.0159 |
| 2 | 0.7344 | 0.0164 |
| 5 | 0.5314 | 0.0201 |
| 10 | 0.4639 | 0.0071 |
| 50 | 0.2721 | 0.0043 |

### Checks

- trim_loss_in_valid_range: True
- trim_loss_varies_with_density: True
- nonzero_trim_at_n50: True

## legacy core (research engine)

| Vehicles | Trim (Python) | Trim (proxy) | Delta |
|---:|---:|---:|---:|
| 1 | 0.7764 | 0.1520 | 0.6244 |
| 2 | 0.4862 | 0.1660 | 0.3202 |
| 5 | 0.1000 | 0.1840 | -0.0840 |
| 10 | 0.0860 | 0.2060 | -0.1200 |
| 50 | 0.0687 | 0.2980 | -0.2293 |

### Checks

- trim_loss_in_valid_range: True
- trim_loss_trend_monotonic_soft: False

## Summary

- sim_engine_checks_pass: True
- legacy_checks_pass: False
- all_checks_pass (v0.1 gate): True

## Caveats

- v0.1 release gates on sim_engine checks; legacy block is informational.
- Original MATLAB repo: https://github.com/linux-ram/mmWave-V2I-2DRBP
- Uses configs/scenario_legacy_research.yaml research engine.
- trim_loss_matlab_proxy is an illustrative trend, not File Exchange output.
