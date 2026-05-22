#!/usr/bin/env bash
# Publish mmwave-v2i-sim v0.1 to GitHub (linux-ram org).
# Prerequisites: gh auth login, write access to linux-ram org.

set -euo pipefail
cd "$(dirname "$0")/.."

if ! command -v gh >/dev/null 2>&1; then
  echo "Install GitHub CLI: brew install gh && gh auth login"
  exit 1
fi

gh auth status

if git remote get-url origin >/dev/null 2>&1; then
  echo "== Remote origin exists; pushing main =="
  git push -u origin main
else
  echo "== Creating public repo linux-ram/mmwave-v2i-sim =="
  gh repo create linux-ram/mmwave-v2i-sim \
    --public \
    --source=. \
    --remote=origin \
    --description "Python desktop port of the mmWave V2I 2DRBP link-layer simulator" \
    --push
fi

echo "== Tag v0.1.0 =="
git tag -a v0.1.0 -m "Initial public release: MATLAB-parity GUI and sim_engine" 2>/dev/null || true
git push origin v0.1.0

echo "== GitHub Release =="
gh release create v0.1.0 --title "v0.1.0" --notes-file docs/RELEASE_NOTES_v0.1.md || \
  gh release edit v0.1.0 --notes-file docs/RELEASE_NOTES_v0.1.md

echo "== Cross-link MATLAB repo README =="
MATLAB_README=$(gh api repos/linux-ram/mmWave-V2I-2DRBP/readme --jq .content | base64 -d 2>/dev/null || true)
if [[ -n "${MATLAB_README}" ]] && ! grep -q "mmwave-v2i-sim" <<<"${MATLAB_README}"; then
  PATCH="# Python port

**[mmwave-v2i-sim](https://github.com/linux-ram/mmwave-v2i-sim)** — cross-platform GUI, Guillotine/Shelf/MaxRects packing, session export.

---

${MATLAB_README}"
  printf '%s' "${PATCH}" | gh api repos/linux-ram/mmWave-V2I-2DRBP/contents/README.md \
    -X PUT -f message="Link Python port repository" \
    -f content="$(printf '%s' "${PATCH}" | base64)" \
    --jq .content >/dev/null 2>/dev/null && echo "Updated MATLAB README" || \
    echo "Could not auto-update MATLAB README — add link manually (see docs/RELEASE.md)"
else
  echo "Skip MATLAB README (already linked or no API access)"
fi

echo "== Open post-v0.1 issues =="
gh issue create --title "[m5] 3D viewport and live KPI side panel" \
  --body-file .github/ISSUE_TEMPLATE/m5-3d-kpi-panel.md --label "milestone:m5,enhancement" || true
gh issue create --title "[m6] Interactive 200-vehicle scale and stress harness" \
  --body-file .github/ISSUE_TEMPLATE/m6-scale-200.md --label "milestone:m6,enhancement" || true
gh issue create --title "[m9] IEEE PDF build and reproducible figures in CI" \
  --body-file .github/ISSUE_TEMPLATE/m9-paper-pdf-ci.md --label "milestone:m9,documentation" || true

echo "== Done. Verify CI: https://github.com/linux-ram/mmwave-v2i-sim/actions =="
