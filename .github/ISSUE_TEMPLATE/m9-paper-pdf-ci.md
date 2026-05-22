---
name: m9 — IEEE PDF and CI figure build
about: Post-v0.1 publication artifact automation
title: "[m9] IEEE PDF build and reproducible figures in CI"
labels: milestone:m9, documentation
---

## Goal

Automate publication artifacts from committed experiment outputs.

## Acceptance criteria

- [ ] `scripts/build_paper.sh` runs in CI (or release workflow) with `pdflatex`
- [ ] `paper/figures/` regenerated from validation/batch outputs
- [ ] `paper/main.pdf` reproducible from clean checkout
- [ ] README documents one-command paper build

## Context

v0.1 includes `paper/main.tex` and sample figures; PDF CI is deferred.
