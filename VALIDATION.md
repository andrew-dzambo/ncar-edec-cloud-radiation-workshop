# Personal Linux workshop validation

A fresh personal checkout installed the pinned environment, model sources and coefficient data in 59 seconds on the test host. This measures the installer on one host with network/package caching available. GitHub sign-in, creation of a hosted Codespace, extensions and participant interaction add time. The guide gives an individual participant a saved-run activity at minute 10.

The five current notebook cells ran in order with IPython using this checkout’s own environment. Both baseline and doubled-liquid calculations produced PNG, CSV and NetCDF outputs. The terminal route also ran a changed-depth experiment, and its default comparison matched the notebook for all six boundary/band rows. The official reference and synthetic cloud checks passed. The test host restricted Jupyter kernel sockets. The GitHub Actions **Personal Linux notebook** check exercises a real kernel on an Ubuntu runner; its result is available in the repository’s Actions tab. Browser startup under an individual GitHub account is a separate check.

## Earlier tests

The v1.1 shared-runtime configuration was tested separately. Its timing record, `startup_validation.json`, applies only to a preinstalled shared environment. The checks in `validation.json` are from the individual Linux run. The example notebook and HTML contain real saved outputs from that individual run.
