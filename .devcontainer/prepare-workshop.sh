#!/usr/bin/env bash
# Codespaces can open the editor while the notebook environment installs.
set -o pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." || exit 1
if mkdir -p .cache && bash setup_workshop.sh 2>&1 | tee .cache/workshop-setup.log; then
    exit 0
fi

# A network or storage error should leave participants with a working editor.
# Running the installer directly in a terminal still returns its real exit code.
printf '\nWorkshop setup stopped. Open .cache/workshop-setup.log for details.\n'
printf 'In a new terminal you can retry with: bash setup_workshop.sh\n'
printf 'Open SAVED_RUN.md to continue the activity immediately.\n'
