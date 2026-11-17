#!/usr/bin/env python3
"""Check the active interpreter without installing or modifying its environment."""
import importlib
import importlib.metadata
import json
from pathlib import Path
import sys


def check_runtime():
    """Return version details, or raise a readable error for an invalid runtime."""
    if sys.version_info[:2] != (3, 11):
        raise RuntimeError("The workshop environment requires Python 3.11.")
    for package in ["numpy", "scipy", "pandas", "xarray", "netCDF4", "matplotlib",
                    "pyrte_rrtmgp", "ipykernel", "jupyterlab", "nbformat", "nbclient", "nbconvert"]:
        try:
            importlib.import_module(package)
        except ImportError as exc:
            raise RuntimeError(f"The prepared runtime is missing or cannot import {package}.") from exc
    version = importlib.metadata.version("pyrte_rrtmgp")
    if version != "0.2.5":
        raise RuntimeError(f"Expected pyRTE-RRTMGP 0.2.5; found {version}.")
    records = list((Path(sys.prefix) / "conda-meta").glob("rte_rrtmgp-*.json"))
    if len(records) != 1:
        raise RuntimeError("Expected exactly one conda rte_rrtmgp runtime record.")
    record = json.loads(records[0].read_text())
    if record["version"] != "1.9.2":
        raise RuntimeError(f"Expected compiled RTE+RRTMGP 1.9.2; found {record['version']}.")
    return {"python_version": sys.version.split()[0],
            "pyrte_rrtmgp_version": version, "rte_rrtmgp_version": record["version"]}


if __name__ == "__main__":
    result = check_runtime()
    print(f"Runtime ready: Python {result['python_version']}, pyRTE-RRTMGP 0.2.5, compiled RTE+RRTMGP 1.9.2")
