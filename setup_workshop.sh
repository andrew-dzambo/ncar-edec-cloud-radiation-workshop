#!/usr/bin/env bash
# Instructor/server preparation only, before the timed activity.
# Participants use configure_workshop.sh during the workshop; no assigned preparation.
# Standalone users may also run this installer outside the timed workshop.
# Run on the Linux server: bash setup_workshop.sh
# Windows PowerShell/macOS Terminal are used to SSH to that server first.
# No sudo, shell-profile edits, conda activation, or GitHub credentials are used.
set -Eeuo pipefail
trap 'printf "Setup stopped at line %s. Read the error above, fix it, then rerun this script.\n" "$LINENO" >&2' ERR
WORKSHOP_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
RUNTIME_PREFIX="$WORKSHOP_ROOT/envs/rrtmgp"

if [[ "$(uname -s)" != Linux || "$(uname -m)" != x86_64 ]]; then
    echo "This installer targets a Linux x86_64 server. SSH there from Windows or macOS, then rerun it." >&2
    exit 2
fi
# The tested conda-forge lock includes libraries requiring glibc >= 2.28.
GLIBC_DESCRIPTION="$(getconf GNU_LIBC_VERSION 2>/dev/null || true)"
GLIBC_VERSION="${GLIBC_DESCRIPTION##* }"
GLIBC_MAJOR="${GLIBC_VERSION%%.*}"
GLIBC_MINOR="${GLIBC_VERSION#*.}"
GLIBC_MINOR="${GLIBC_MINOR%%.*}"
if [[ ! "$GLIBC_MAJOR" =~ ^[0-9]+$ || ! "$GLIBC_MINOR" =~ ^[0-9]+$ ]] || \
   (( GLIBC_MAJOR < 2 || (GLIBC_MAJOR == 2 && GLIBC_MINOR < 28) )); then
    echo "This tested environment requires glibc >= 2.28 (e.g., a RHEL 8/9-compatible Linux node)." >&2
    echo "Ask your server administrator for a compatible compute node or supported container." >&2
    exit 2
fi
for program in curl tar sha256sum; do
    command -v "$program" >/dev/null || { echo "Missing $program; ask the Linux server administrator to provide it." >&2; exit 2; }
done

# Keep 20-30 simultaneous learners from each starting many BLAS/OpenMP threads.
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
export PYTHONNOUSERSITE=1 PYTHONPATH=""
mkdir -p "$WORKSHOP_ROOT/.tools" "$WORKSHOP_ROOT/.cache" "$WORKSHOP_ROOT/envs"
MAMBA="$WORKSHOP_ROOT/.tools/bin/micromamba"
if [[ ! -x "$MAMBA" ]]; then
    echo "Downloading micromamba 2.10.0 (about 7 MB) ..."
    ARCHIVE="$WORKSHOP_ROOT/.cache/micromamba-2.10.0.tar.bz2"
    curl --fail --location --retry 3 --connect-timeout 30 --max-time 300 \
        "https://micro.mamba.pm/api/micromamba/linux-64/2.10.0" -o "$ARCHIVE.part"
    printf '%s  %s\n' '9a97976244929bbae28fb1fae504e74a3e7e6d1932870e3a03321f01b7fbd07b' "$ARCHIVE.part" | sha256sum --check -
    mv "$ARCHIVE.part" "$ARCHIVE"
    tar -xjf "$ARCHIVE" -C "$WORKSHOP_ROOT/.tools" bin/micromamba
fi

if [[ ! -x "$RUNTIME_PREFIX/bin/python" ]]; then
    # Explicit URLs + package hashes reproduce the instructor-prepared environment.
    if [[ -f "$WORKSHOP_ROOT/environment-linux-64.lock" ]]; then
        SPEC="$WORKSHOP_ROOT/environment-linux-64.lock"
    else
        SPEC="$WORKSHOP_ROOT/environment.yml"
    fi
    "$MAMBA" create --yes --root-prefix "$WORKSHOP_ROOT/.cache/micromamba" \
        --prefix "$RUNTIME_PREFIX" --file "$SPEC" --strict-channel-priority
fi
if ! "$RUNTIME_PREFIX/bin/python" "$WORKSHOP_ROOT/scripts/check_runtime.py"; then
    echo "The existing envs/rrtmgp environment is incomplete or incompatible." >&2
    echo "Move that directory aside, then rerun setup_workshop.sh to recreate it." >&2
    exit 2
fi

"$RUNTIME_PREFIX/bin/python" "$WORKSHOP_ROOT/scripts/provision_sources.py"
"$RUNTIME_PREFIX/bin/python" -m ipykernel install --prefix "$RUNTIME_PREFIX" \
    --name rrtmgp-workshop --display-name "Python (RRTMGP Workshop)" \
    --env OMP_NUM_THREADS 1 --env OPENBLAS_NUM_THREADS 1 --env MKL_NUM_THREADS 1 \
    --env NUMEXPR_NUM_THREADS 1 --env PYTHONNOUSERSITE 1
printf '\nInstructor runtime ready. Give participants this shared checkout path:\n  %s\nThey run from their own cloned checkout:\n  bash configure_workshop.sh "%s"\n' "$WORKSHOP_ROOT" "$WORKSHOP_ROOT"
