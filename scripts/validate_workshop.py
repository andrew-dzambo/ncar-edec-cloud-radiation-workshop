#!/usr/bin/env python3
"""Validate the workshop against upstream answers and physical bookkeeping.

Run from any directory with the workshop environment's Python:
    envs/rrtmgp/bin/python scripts/validate_workshop.py --output validation.json

No network access is needed once setup_workshop.sh has completed.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import time

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACKAGE_ROOT))

import numpy as np
from scipy.integrate import quad

from workshop_model import (GRAVITY, CP_DRY, build_column, run_column,
                            verify_reference)


def check_inputs():
    """Invalid public inputs must fail before they reach compiled kernels."""
    invalid = [
        {"depth_m": np.nan}, {"depth_m": -1.}, {"depth_m": 49.},
        {"depth_m": 3001.}, {"lwp_gm2": -1.}, {"iwp_gm2": np.inf},
        {"liquid_radius_um": 0.}, {"ice_diameter_um": np.nan},
        {"solar_zenith_deg": 90.}, {"surface_albedo": 1.01},
    ]
    for kwargs in invalid:
        try:
            build_column(**kwargs)
        except ValueError:
            continue
        raise AssertionError(f"Expected ValueError for {kwargs}")
    return len(invalid)


def check_profiles():
    """Use independent numerical quadrature to check layer-integrated shapes."""
    checks = 0
    max_path_error = 0.
    max_shape_error = 0.
    min_cloud_layers = 100000
    for depth in (50., 1000., 3000.):
        for liquid, ice in ((0., 0.), (100., 0.), (0., 30.), (100., 30.)):
            ds = build_column(depth_m=depth, lwp_gm2=liquid, iwp_gm2=ice)
            z = ds.z_level.values
            dz = np.diff(z)
            base = ds.attrs["cloud_base_m"]
            cloud = (z[:-1] >= base) & (z[1:] <= base + depth)
            min_cloud_layers = min(min_cloud_layers, int(cloud.sum()))
            assert cloud.sum() >= 40
            assert np.all(dz > 0)
            assert np.all(np.diff(ds.pres_level.values, axis=-1) < 0)
            assert np.any(z == base) and np.any(z == base + depth)
            for name, concentration, requested, shape in (
                ("lwp", "lwc", liquid, lambda x: 30*x**4*(1-x)),
                ("iwp", "iwc", ice, lambda x: 60*x**2*(1-x)**3),
            ):
                path = ds[name].values.ravel()
                assert np.all(path >= 0)
                assert np.all(path[~cloud] == 0)
                # Recover column water from the delivered layer-mean contents.
                recovered = float(np.sum(ds[concentration].values.ravel()*dz))
                np.testing.assert_allclose(recovered, requested, rtol=1.e-12, atol=1.e-10)
                max_path_error = max(max_path_error, abs(recovered-requested))
                # Independent adaptive integration checks every cloudy layer.
                for k in np.flatnonzero(cloud):
                    lower, upper = (z[k]-base)/depth, (z[k+1]-base)/depth
                    expected = requested*quad(shape, lower, upper, epsabs=1.e-13)[0]
                    np.testing.assert_allclose(path[k], expected, rtol=1.e-10, atol=1.e-11)
                    max_shape_error = max(max_shape_error, abs(float(path[k])-expected))
            checks += 1
    return {"cases": checks, "minimum_cloud_layers": min_cloud_layers,
            "max_water_path_error_g_m2": max_path_error,
            "max_layer_shape_error_g_m2": max_shape_error}


def check_radiation():
    """Check true clear/cloud identity and whole-column energy accounting."""
    cases = (("zero_thin", 50., 0., 0.),
             ("liquid_thin", 50., 100., 0.),
             ("mixed_default", 1000., 100., 30.),
             ("ice_deep", 3000., 0., 30.),
             ("mixed_deep", 3000., 100., 30.))
    summaries = []
    max_closure_error = 0.
    for name, depth, liquid, ice in cases:
        started = time.perf_counter()
        result = run_column(build_column(depth_m=depth, lwp_gm2=liquid, iwp_gm2=ice))
        for variable in result:
            assert np.isfinite(result[variable].values).all(), variable
        if liquid == 0. and ice == 0.:
            for band in ("sw", "lw"):
                for direction in ("up", "down"):
                    field = f"{band}_flux_{direction}"
                    np.testing.assert_allclose(result[field], result[field+"_clear"],
                                               rtol=0, atol=1.e-10)
            for band in ("sw", "lw", "total"):
                np.testing.assert_allclose(result[band+"_cre"], 0., rtol=0, atol=1.e-10)
        # Energy absorbed by all layers must equal the top-minus-bottom
        # net-downward boundary flux. This checks the heating SIGN as well
        # as units, layer ordering, pressure weighting and dimensional alignment.
        pressure_mass = (result.pres_level.values[:, :-1]
                         - result.pres_level.values[:, 1:]) / GRAVITY
        for band in ("sw", "lw", "total"):
            for suffix in ("", "_clear"):
                heating = result[f"{band}_heating_rate{suffix}"].values
                integrated_power = float(np.sum(heating*CP_DRY*pressure_mass/86400.))
                net = result[f"{band}_flux_net{suffix}"].values.ravel()
                boundary_power = float(net[-1]-net[0])
                np.testing.assert_allclose(integrated_power, boundary_power,
                                           rtol=1.e-12, atol=1.e-10)
                max_closure_error = max(max_closure_error,
                                        abs(integrated_power-boundary_power))
        summaries.append({"case": name, "depth_m": depth,
                          "layers": result.sizes["layer"],
                          "surface_total_cre_W_m2": float(result.total_cre.isel(column=0, level=0)),
                          "elapsed_seconds": round(time.perf_counter()-started, 3)})
    return {"cases": summaries, "max_column_energy_closure_error_W_m2": max_closure_error}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="Also write the JSON report to this path")
    args = parser.parse_args()
    start = time.perf_counter()
    report = {
        "status": "passed",
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "upstream_reference_tolerance": {"relative": 1.e-5, "absolute_W_m2": 1.e-7},
        "upstream_reference_max_absolute_errors_W_m2": verify_reference(),
        "invalid_input_checks": check_inputs(),
        "profile_checks": check_profiles(),
        "radiation_checks": check_radiation(),
        "scope": "Workshop helper and upstream all-sky reference; not a guarantee of observational accuracy or physical realism of imposed clouds.",
    }
    report["elapsed_seconds"] = round(time.perf_counter()-start, 3)
    text = json.dumps(report, indent=2, allow_nan=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")


if __name__ == "__main__":
    main()
