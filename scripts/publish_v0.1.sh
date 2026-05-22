#!/usr/bin/env bash
# Publish mmwave-v2i-sim v0.1 to GitHub (linux-ram org).
# Prerequisites: gh auth login, write access to linux-ram org.

set -euo pipefail
cd "$(dirname "$0")/.."
REPO="linux-ram/mmwave-v2i-sim"
MATLAB_REPO="linux-ram/mmWave-V2I-2DRBP"

if ! command -v gh >/dev/null 2>&1; then
  echo "Install GitHub CLI: brew install gh && gh auth login"
  exit 1
fi

gh auth status

_issue_body() {
  # Strip YAML frontmatter from issue template markdown files.
  awk 'BEGIN{f=0} /^---$/ {f++; next} f>=2 {print}' "$1"
}

_ensure_label() {
  local name="$1" color="$2"
  gh label create "${name}" --color "${color}" -R "${REPO}" 2>/dev/null || true
}

if git remote get-url origin >/dev/null 2>&1; then
  echo "== Remote origin exists; pushing main =="
  git push -u origin main
else
  echo "== Creating public repo ${REPO} =="
  gh repo create "${REPO}" \
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
gh release create v0.1.0 --title "v0.1.0" --notes-file docs/RELEASE_NOTES_v0.1.md -R "${REPO}" || \
  gh release edit v0.1.0 --notes-file docs/RELEASE_NOTES_v0.1.md -R "${REPO}"

echo "== Cross-link MATLAB repo README =="
MATLAB_README=$(gh api "repos/${MATLAB_REPO}/readme" --jq .content 2>/dev/null | base64 -d 2>/dev/null || true)
if [[ -n "${MATLAB_README}" ]] && ! grep -q "mmwave-v2i-sim" <<<"${MATLAB_README}"; then
  PATCH="# Python port

**[mmwave-v2i-sim](https://github.com/linux-ram/mmwave-v2i-sim)** — cross-platform GUI, Guillotine/Shelf/MaxRects packing, session ZIP export.

---

${MATLAB_README}"
  SHA=$(gh api "repos/${MATLAB_REPO}/contents/README.md" --jq .sha 2>/dev/null || true)
  if [[ -n "${SHA}" ]]; then
    B64=$(printf '%s' "${PATCH}" | base64 | tr -d '\n')
    if gh api "repos/${MATLAB_REPO}/contents/README.md" -X PUT \
      -f message="Link Python port repository" \
      -f content="${B64}" \
      -f sha="${SHA}" >/dev/null 2>&1; then
      echo "Updated MATLAB README"
    else
      echo "Could not auto-update MATLAB README — add link manually (see docs/RELEASE.md)"
    fi
  else
    echo "Could not read MATLAB README SHA — add link manually (see docs/RELEASE.md)"
  fi
else
  echo "Skip MATLAB README (already linked or no API access)"
fi

echo "== Ensure milestone labels =="
_ensure_label "milestone:m5" "1D76DB"
_ensure_label "milestone:m6" "FBCA04"
_ensure_label "milestone:m9" "5319E7"
gh label create "enhancement" --color "A2EEEF" -R "${REPO}" 2>/dev/null || true
gh label create "documentation" --color "0075CA" -R "${REPO}" 2>/dev/null || true

echo "== Open post-v0.1 issues =="
TMP=$(mktemp -d)
trap 'rm -rf "${TMP}"' EXIT
_issue_body .github/ISSUE_TEMPLATE/m5-3d-kpi-panel.md > "${TMP}/m5.md"
_issue_body .github/ISSUE_TEMPLATE/m6-scale-200.md > "${TMP}/m6.md"
_issue_body .github/ISSUE_TEMPLATE/m9-paper-pdf-ci.md > "${TMP}/m9.md"

if ! gh issue list -R "${REPO}" --search "[m5] 3D viewport" --limit 1 --json number --jq '.[0].number' 2>/dev/null | grep -q .; then
  gh issue create -R "${REPO}" --title "[m5] 3D viewport and live KPI side panel" \
    --body-file "${TMP}/m5.md" --label "milestone:m5,enhancement"
else
  echo "Issue [m5] already exists"
fi
if ! gh issue list -R "${REPO}" --search "[m6] Interactive 200" --limit 1 --json number --jq '.[0].number' 2>/dev/null | grep -q .; then
  gh issue create -R "${REPO}" --title "[m6] Interactive 200-vehicle scale and stress harness" \
    --body-file "${TMP}/m6.md" --label "milestone:m6,enhancement"
else
  echo "Issue [m6] already exists"
fi
if ! gh issue list -R "${REPO}" --search "[m9] IEEE PDF" --limit 1 --json number --jq '.[0].number' 2>/dev/null | grep -q .; then
  gh issue create -R "${REPO}" --title "[m9] IEEE PDF build and reproducible figures in CI" \
    --body-file "${TMP}/m9.md" --label "milestone:m9,documentation"
else
  echo "Issue [m9] already exists"
fi

echo "== Done. Verify CI: https://github.com/linux-ram/mmwave-v2i-sim/actions =="
