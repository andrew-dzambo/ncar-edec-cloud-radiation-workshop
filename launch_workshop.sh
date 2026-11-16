#!/usr/bin/env bash
# Optional argument: server port (default 8888). Pick a unique port per user.
# Use an approved interactive compute session, not a busy HPC login node.
set -Eeuo pipefail
WORKSHOP_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PORT="${1:-8888}"
if [[ ! "$PORT" =~ ^[0-9]+$ ]] || (( PORT < 1024 || PORT > 65535 )); then
    echo "Choose a numeric port between 1024 and 65535." >&2
    exit 2
fi
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
export PYTHONNOUSERSITE=1 PYTHONPATH=""
JUPYTER="$WORKSHOP_ROOT/envs/rrtmgp/bin/jupyter"
if [[ ! -x "$JUPYTER" ]]; then
    echo "Run bash setup_workshop.sh first, on the Linux server." >&2
    exit 2
fi
cd "$WORKSHOP_ROOT"
exec "$JUPYTER" lab --no-browser --ip=127.0.0.1 --port="$PORT" \
    --ServerApp.port_retries=0 --ServerApp.root_dir="$WORKSHOP_ROOT"
