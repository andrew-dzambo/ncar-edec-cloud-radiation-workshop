#!/usr/bin/env bash
# Start Jupyter from your own checkout after configure_workshop.sh.
# Optional argument: server port (default 8888); use your assigned unique port.
# Use an approved interactive session. This launcher never installs anything.
set -Eeuo pipefail
WORKSHOP_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PORT="${1:-8888}"
if [[ $# -gt 1 || ! "$PORT" =~ ^[0-9]+$ ]] || (( 10#$PORT < 1024 || 10#$PORT > 65535 )); then
    echo "Usage: bash launch_workshop.sh PORT (a number from 1024 to 65535)." >&2
    exit 2
fi
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
export PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 JUPYTER_PREFER_ENV_PATH=0 PYTHONPATH=""
if [[ -f "$WORKSHOP_ROOT/.workshop-runtime.json" ]]; then
    PYTHON="$WORKSHOP_ROOT/.workshop-python"
    if [[ ! -x "$PYTHON" ]]; then
        echo "Shared runtime link is missing or unavailable. Rerun bash configure_workshop.sh SHARED_CHECKOUT." >&2
        exit 2
    fi
else
    PYTHON="$WORKSHOP_ROOT/envs/rrtmgp/bin/python"
    if [[ ! -x "$PYTHON" ]]; then
        echo "First run bash configure_workshop.sh /path/to/instructor/shared-checkout on the Linux server." >&2
        exit 2
    fi
fi
exec "$PYTHON" -B "$WORKSHOP_ROOT/scripts/workshop_runtime.py" launch \
    --root "$WORKSHOP_ROOT" --port="$PORT"
