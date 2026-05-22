#!/usr/bin/env bash
# Regenerate requirements-lock.txt from the active venv (PyPI pins only, no -e paths).
set -euo pipefail
cd "$(dirname "$0")/.."
ROOT="$(pwd)"
OUT="${ROOT}/requirements-lock.txt"
if [[ ! -x "${ROOT}/.venv/bin/pip" ]]; then
  echo "Create .venv and pip install -e '.[dev]' first."
  exit 1
fi
{
  echo "# Pinned dependencies for reproducible installs (CI and local)."
  echo "# Install the project separately: pip install -e \".[dev]\""
  echo "# Regenerate: bash scripts/refresh_lock.sh"
  "${ROOT}/.venv/bin/pip" freeze | grep -v '^-e ' | grep -v '^#' | grep -v '^mmwave-v2i-sim'
} > "${OUT}"
echo "Wrote ${OUT}"
