#!/usr/bin/env python3
"""Fail early if the selected interpreter is not the tested workshop runtime."""
import importlib
import importlib.metadata
import json
from pathlib import Path
import sys

for package in ["numpy", "scipy", "pandas", "xarray", "netCDF4", "matplotlib",
                "pyrte_rrtmgp", "ipykernel", "jupyterlab", "nbformat", "nbclient", "nbconvert"]:
    importlib.import_module(package)
assert sys.version_info[:2] == (3, 11), "The workshop environment requires Python 3.11."
assert importlib.metadata.version("pyrte_rrtmgp") == "0.2.5", "Expected pyRTE-RRTMGP 0.2.5."
records = list((Path(sys.prefix) / "conda-meta").glob("rte_rrtmgp-*.json"))
assert len(records) == 1, "Expected exactly one conda rte_rrtmgp runtime record."
record = json.loads(records[0].read_text())
assert record["version"] == "1.9.2", "Expected compiled RTE+RRTMGP 1.9.2."
print(f"Runtime ready: Python {sys.version.split()[0]}, pyRTE-RRTMGP 0.2.5, compiled RTE+RRTMGP 1.9.2")
