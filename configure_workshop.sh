#!/usr/bin/env bash
# Participant setup, during the workshop: use the instructor's prepared shared checkout.
# Nothing is installed in either checkout, and no shared files are modified.
set -Eeuo pipefail
WORKSHOP_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
if [[ $# -ne 1 ]]; then
    echo "Usage: bash configure_workshop.sh /path/to/instructor/shared-checkout" >&2
    exit 2
fi
if [[ "$(uname -s)" != Linux || "$(uname -m)" != x86_64 ]]; then
    echo "Run this in the Linux x86_64 server terminal (JupyterLab Terminal or SSH from your laptop)." >&2
    exit 2
fi
if [[ ! -d "$1" ]]; then
    echo "Shared checkout does not exist or is not mounted: $1. Use the path supplied by your instructor." >&2
    exit 2
fi
SHARED_ROOT="$(cd -- "$1" && pwd)"
SHARED_PYTHON="$SHARED_ROOT/envs/rrtmgp/bin/python"
if [[ ! -x "$SHARED_PYTHON" ]]; then
    echo "Prepared shared Python is missing: $SHARED_PYTHON" >&2
    echo "Ask the instructor to check the shared path/runtime. Do not install a separate environment during the workshop." >&2
    exit 2
fi
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
export PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 JUPYTER_PREFER_ENV_PATH=0 PYTHONPATH=""
exec "$SHARED_PYTHON" -B "$WORKSHOP_ROOT/scripts/workshop_runtime.py" configure \
    --root "$WORKSHOP_ROOT" --source-root "$SHARED_ROOT"
