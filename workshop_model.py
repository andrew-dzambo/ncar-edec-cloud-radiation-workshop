"""Small, reproducible RTE+RRTMGP cloud-radiation workshop helpers.

The calculations use the real pyRTE-RRTMGP/Fortran kernels. The atmosphere and
cloud profiles are deliberately idealized teaching inputs, not CAESAR retrievals.
See Pincus et al. (2019), doi:10.1029/2019MS001621, for the radiation framework.
"""
from __future__ import annotations

import hashlib
import importlib.metadata
import json
import os
from functools import lru_cache
from pathlib import Path

# Import netCDF4 before xarray (the upstream test suite uses this order).
import netCDF4  # noqa: F401
import numpy as np
import xarray as xr
from scipy.special import betainc
import matplotlib.pyplot as plt

from pyrte_rrtmgp import rte
from pyrte_rrtmgp.rrtmgp import GasOptics, CloudOptics

PACKAGE_ROOT = Path(__file__).resolve().parent
COEFFICIENT_FILES = (
    "rrtmgp-gas-sw-g224.nc", "rrtmgp-gas-lw-g256.nc",
    "rrtmgp-clouds-sw-bnd.nc", "rrtmgp-clouds-lw-bnd.nc",
)
GRAVITY = 9.80665
CP_DRY = 1004.0


def _finite(name, value, lower=None, upper=None):
    """Validate interactive inputs before calling compiled kernels."""
    value = float(value)
    if not np.isfinite(value):
        raise ValueError(f"{name} must be finite.")
    if lower is not None and value < lower:
        raise ValueError(f"{name} must be >= {lower}.")
    if upper is not None and value > upper:
        raise ValueError(f"{name} must be <= {upper}.")
    return value


def find_data_dir(data_dir=None):
    """Find the installer-managed v1.9 data without an implicit download."""
    path = Path(data_dir or os.environ.get(
        "RRTMGP_DATA", str(PACKAGE_ROOT / ".cache" / "rrtmgp-data")))
    if not all((path / f).is_file() for f in COEFFICIENT_FILES):
        raise FileNotFoundError(
            f"RRTMGP coefficients not found in {path}. Use the facilitator's "
            "configure_workshop.sh command and select the workshop kernel, "
            "or set RRTMGP_DATA to the prepared v1.9 data directory.")
    return path.resolve()


@lru_cache(maxsize=2)
def _load_optics(data_dir_string):
    """Read coefficient tables once per kernel, not once per experiment."""
    path = Path(data_dir_string)
    return {
        "sw_gas": GasOptics(file_path=str(path / COEFFICIENT_FILES[0])),
        "lw_gas": GasOptics(file_path=str(path / COEFFICIENT_FILES[1])),
        "sw_cloud": CloudOptics(file_path=str(path / COEFFICIENT_FILES[2])),
        "lw_cloud": CloudOptics(file_path=str(path / COEFFICIENT_FILES[3])),
    }


def _temperature_pressure(z):
    """Prescribed cool temperature profile and dry hydrostatic pressure.

    The piecewise-linear temperature is a teaching atmosphere, not a measured
    sounding or the U.S. Standard Atmosphere. Integrate dp/p=-g dz/(Rd*T)
    analytically through each segment; surface pressure is 101325 Pa.
    """
    heights = np.array([0., 10000., 20000., 32000., 47000., 51000., 60000.])
    temps = np.array([278., 218., 218., 230., 272., 272., 246.8])
    pressure = np.full_like(np.asarray(z, dtype=float), 101325.)
    for bottom, top, t0, t1 in zip(heights[:-1], heights[1:], temps[:-1], temps[1:]):
        dz = np.clip(z - bottom, 0., top - bottom)
        lapse = (t1 - t0) / (top - bottom)
        integral = dz / t0 if lapse == 0 else np.log1p(lapse * dz / t0) / lapse
        pressure *= np.exp(-GRAVITY * integral / 287.05)
    return np.interp(z, heights, temps), pressure


def build_column(depth_m=1000., lwp_gm2=100., iwp_gm2=30.,
                 cloud_base_m=1500., liquid_radius_um=10., ice_diameter_um=60.,
                 solar_zenith_deg=60., surface_albedo=0.15):
    """Construct a one-column atmosphere with exactly conserved water paths.

    Liquid shape: f_L(x)=30*x**4*(1-x), the Beta(5,2) density, mode 0.8.
    Ice shape: f_I(x)=60*x**2*(1-x)**3, the Beta(3,4) density, mode 0.4.
    x=(z-cloud_base)/depth. LWC=(LWP/depth)*f_L, in g m-3, and likewise IWC.
    Layer paths use analytic beta CDF differences rather than point sampling.
    Cloud boundaries coincide with grid interfaces; >=40 layers resolve clouds
    even at the minimum allowed depth of 50 m.

    IMPORTANT: this pyRTE version calls its ice size input ``rei`` but actually
    interpolates the ice EFFECTIVE DIAMETER lookup table, in micrometres.
    """
    depth_m = _finite("depth_m", depth_m, 50., 3000.)
    lwp_gm2 = _finite("lwp_gm2", lwp_gm2, 0.)
    iwp_gm2 = _finite("iwp_gm2", iwp_gm2, 0.)
    cloud_base_m = _finite("cloud_base_m", cloud_base_m, 0., 10000.)
    liquid_radius_um = _finite("liquid_radius_um", liquid_radius_um, 2.5, 21.5)
    ice_diameter_um = _finite("ice_diameter_um", ice_diameter_um, 10., 180.)
    solar_zenith_deg = _finite("solar_zenith_deg", solar_zenith_deg, 0., 89.)
    surface_albedo = _finite("surface_albedo", surface_albedo, 0., 1.)
    cloud_top = cloud_base_m + depth_m

    # Background resolution is 250 m below 12 km and 1 km above it. Replace
    # all background interfaces inside the cloud with >=40 evenly spaced cells.
    background = np.r_[np.arange(0., 12000.1, 250.), np.arange(13000., 60000.1, 1000.)]
    outside = background[(background < cloud_base_m) | (background > cloud_top)]
    n_cloud = max(40, int(np.ceil(depth_m / 25.)))
    z_level = np.unique(np.r_[outside, np.linspace(cloud_base_m, cloud_top, n_cloud + 1)])
    dz = np.diff(z_level)
    z_layer = 0.5 * (z_level[:-1] + z_level[1:])
    temp_level, pres_level = _temperature_pressure(z_level)
    temp_layer, pres_layer = _temperature_pressure(z_layer)

    x_level = np.clip((z_level - cloud_base_m) / depth_m, 0., 1.)
    liquid_weights = np.diff(betainc(5, 2, x_level))
    ice_weights = np.diff(betainc(3, 4, x_level))
    layer_lwp = lwp_gm2 * liquid_weights
    layer_iwp = iwp_gm2 * ice_weights
    # All gas inputs are mol/mol of dry air, not mass mixing ratio or ppm.
    h2o = 0.006 * np.exp(-z_layer / 2000.) + 3.e-6
    o3 = 3.e-8 + 8.e-6 * np.exp(-0.5 * ((z_layer - 25000.) / 6500.)**2)

    # The pinned wrapper renames level differences to layer without resetting
    # indexes. Leave vertical dimensions unindexed to avoid spurious alignment.
    ds = xr.Dataset()
    for name, values, units in (
        ("pres_layer", pres_layer, "Pa"), ("temp_layer", temp_layer, "K"),
        ("h2o", h2o, "mol mol-1"), ("o3", o3, "mol mol-1"),
        ("lwp", layer_lwp, "g m-2"), ("iwp", layer_iwp, "g m-2"),
        ("lwc", layer_lwp / dz, "g m-3"), ("iwc", layer_iwp / dz, "g m-3"),
        ("rel", np.full_like(dz, liquid_radius_um), "um"),
        ("rei", np.full_like(dz, ice_diameter_um), "um"),
    ):
        ds[name] = (("column", "layer"), values[None, :], {"units": units})
    for name, values, units in (("pres_level", pres_level, "Pa"),
                               ("temp_level", temp_level, "K")):
        ds[name] = (("column", "level"), values[None, :], {"units": units})
    ds["z_level"] = ("level", z_level, {"units": "m", "positive": "up"})
    ds["z_layer"] = ("layer", z_layer, {"units": "m", "positive": "up"})
    ds["layer_thickness"] = ("layer", dz, {"units": "m"})
    ds["normalized_cloud_altitude"] = ("layer", (z_layer - cloud_base_m) / depth_m)
    ds["surface_temperature"] = ("column", [278.], {"units": "K"})
    for gas, vmr in {"co2": 420.e-6, "ch4": 1.8e-6, "n2o": 0.32e-6,
                     "n2": 0.7808, "o2": 0.2095, "co": 0.}.items():
        ds[gas] = xr.DataArray(vmr, attrs={"units": "mol mol-1"})
    ds["lwp"].attrs["long_name"] = "liquid water path of each layer (not total column LWP)"
    ds["iwp"].attrs["long_name"] = "ice water path of each layer (not total column IWP)"
    ds["rel"].attrs["long_name"] = "liquid effective radius"
    ds["rei"].attrs["long_name"] = "ice effective diameter (legacy pyRTE variable name)"
    ds.attrs = {
        "title": "Idealized synthetic-cloud teaching atmosphere",
        "cloud_depth_m": depth_m, "cloud_base_m": cloud_base_m,
        "requested_lwp_gm2": lwp_gm2, "requested_iwp_gm2": iwp_gm2,
        "solar_zenith_deg": solar_zenith_deg, "surface_albedo": surface_albedo,
        "surface_emissivity": 0.98, "liquid_radius_um": liquid_radius_um,
        "ice_diameter_um": ice_diameter_um, "cloud_fraction": 1.,
        "ice_roughness_table_index": 1,  # Second category, fixed by pyRTE v0.2.5.
        "liquid_shape": "Beta(5,2): mode x=0.8", "ice_shape": "Beta(3,4): mode x=0.4",
        "assumptions": "Independent plane-parallel column; aerosol-free; prescribed gases and temperatures; no saturation adjustment or microphysical evolution; top at 60 km; dry hydrostatic pressure.",
    }
    np.testing.assert_allclose(layer_lwp.sum(), lwp_gm2, atol=1.e-10, rtol=1.e-12)
    np.testing.assert_allclose(layer_iwp.sum(), iwp_gm2, atol=1.e-10, rtol=1.e-12)
    return ds


def _check_sizes(atmosphere, optics):
    for key in ("sw_cloud", "lw_cloud"):
        cloud = optics[key]
        for name, mask_name, low, high in (
            ("rel", "lwp", float(cloud.rel_min), float(cloud.rel_max)),
            ("rei", "iwp", float(cloud.dei_min), float(cloud.dei_max)),
        ):
            selected = np.asarray(atmosphere[name])[np.asarray(atmosphere[mask_name]) > 0]
            if selected.size and (selected.min() < low or selected.max() > high):
                raise ValueError(f"{name} outside {key} table range [{low}, {high}] um.")


def _solve_fluxes(atmosphere, optics, cloudy, albedo, mu0, emissivity):
    """Compute fresh gas optics for every pair; add_to modifies its target."""
    spectra = []
    for band in ("sw", "lw"):
        props = optics[f"{band}_gas"].compute(atmosphere, add_to_input=False)
        if band == "sw":
            props["surface_albedo_direct"] = albedo
            props["surface_albedo_diffuse"] = albedo
            props["mu0"] = mu0
        else:
            props["surface_emissivity"] = emissivity
        if cloudy:
            # LW absorption optical depth excludes the scattering contribution.
            kind = rte.OpticsTypes.TWO_STREAM if band == "sw" else rte.OpticsTypes.ABSORPTION
            cloud_props = optics[f"{band}_cloud"].compute(atmosphere, problem_type=kind)
            props = cloud_props.rte.add_to(props, delta_scale=(band == "sw"))
        spectra.append(props.rte.solve(add_to_input=False))
    return xr.merge(spectra)


def run_column(atmosphere, data_dir=None):
    """Solve identical cloudy and clear columns; return inputs plus fluxes.

    Clear sky removes condensed water only. Both runs retain identical gases,
    temperature, pressure, surface and sun. Net flux is DOWN minus UP; cloud
    radiative effect (CRE) is cloudy net minus clear net at the same interface.
    """
    path = find_data_dir(data_dir)
    optics = _load_optics(str(path))
    _check_sizes(atmosphere, optics)
    mu0 = float(np.cos(np.deg2rad(atmosphere.attrs["solar_zenith_deg"])))
    clear = _solve_fluxes(atmosphere.copy(deep=True), optics, False,
                         atmosphere.attrs["surface_albedo"], mu0, 0.98)
    cloudy = _solve_fluxes(atmosphere.copy(deep=True), optics, True,
                          atmosphere.attrs["surface_albedo"], mu0, 0.98)
    result = atmosphere.copy(deep=True)
    for suffix, fluxes in (("", cloudy), ("_clear", clear)):
        for name in fluxes.data_vars:
            result[name + suffix] = fluxes[name]
            result[name + suffix].attrs["units"] = "W m-2"
        for band in ("sw", "lw"):
            result[f"{band}_flux_net{suffix}"] = result[f"{band}_flux_down{suffix}"] - result[f"{band}_flux_up{suffix}"]
        result[f"total_flux_net{suffix}"] = result[f"sw_flux_net{suffix}"] + result[f"lw_flux_net{suffix}"]
        for band in ("sw", "lw", "total"):
            net = result[f"{band}_flux_net{suffix}"]
            net.attrs.update(units="W m-2", positive="down")
            f = net.transpose("column", "level").values
            dp = -np.diff(result.pres_level.values, axis=-1)
            heating = GRAVITY / CP_DRY * np.diff(f, axis=-1) / dp * 86400.
            result[f"{band}_heating_rate{suffix}"] = (
                ("column", "layer"), heating,
                {"units": "K day-1", "positive": "warming", "description": "Instantaneous dry-air flux-divergence diagnostic; temperature is not advanced"})
    for band in ("sw", "lw", "total"):
        result[f"{band}_cre"] = result[f"{band}_flux_net"] - result[f"{band}_flux_net_clear"]
        result[f"{band}_cre"].attrs.update(units="W m-2", description="All-sky minus clear-sky net downward flux")
    for name in result:
        if not np.all(np.isfinite(result[name].values)):
            raise RuntimeError(f"Non-finite output in {name}; do not interpret this run.")
    result.attrs.update(
        pyrte_version=importlib.metadata.version("pyrte-rrtmgp"),
        runtime_core_version="1.9.2 (pinned conda runtime)", data_version="1.9",
        reference="Pincus, Mlawer, and Delamere (2019), https://doi.org/10.1029/2019MS001621",
        solver="SW two-stream with delta scaling; LW absorption-only, one quadrature angle",
        coefficient_sha256=json.dumps({f: hashlib.sha256((path/f).read_bytes()).hexdigest() for f in COEFFICIENT_FILES}),
    )
    return result


def _plot_style():
    return {"font.size": 11, "axes.labelweight": "bold", "axes.titleweight": "bold",
            "axes.linewidth": 1.2, "lines.linewidth": 2.2, "figure.facecolor": "white",
            "savefig.facecolor": "white", "xtick.direction": "out", "ytick.direction": "out"}


def _tidy(axes):
    for ax in np.asarray(axes).ravel():
        ax.grid(True, alpha=.22)
        for label in ax.get_xticklabels() + ax.get_yticklabels():
            label.set_fontweight("bold")
        ax.spines[["top", "right"]].set_visible(False)


def plot_profiles(ds):
    """Cloud water content profiles with continuous analytic peaks marked."""
    with plt.rc_context(_plot_style()):
        fig, axes = plt.subplots(1, 3, figsize=(13.5, 5.2), constrained_layout=True)
        depth = ds.attrs["cloud_depth_m"]
        base = ds.attrs["cloud_base_m"]
        x = np.linspace(0, 1, 501)
        z = (base + x * depth) / 1000.
        liquid = ds.attrs["requested_lwp_gm2"] / depth * 30 * x**4 * (1-x)
        ice = ds.attrs["requested_iwp_gm2"] / depth * 60 * x**2 * (1-x)**3
        for ax, continuous, name, color, peak, title in (
            (axes[0], liquid, "lwc", "#1565a8", .8, "A. Liquid water"),
            (axes[1], ice, "iwc", "#9b52aa", .4, "B. Ice water"),
        ):
            ax.plot(continuous, z, color=color, label="Continuous target")
            inside = (ds.z_layer >= base) & (ds.z_layer <= base + depth)
            ax.scatter(ds[name].isel(column=0).where(inside, drop=True),
                       ds.z_layer.where(inside, drop=True)/1000., s=10, color=color, alpha=.6,
                       label="Layer mean used by model")
            ax.axhline((base + peak*depth)/1000., color=color, ls=":", lw=1.5,
                       label=f"Target peak: x = {peak:.1f}")
            ax.set(title=title, xlabel=r"Water content (g m$^{-3}$)", ylabel="Altitude (km)")
            ax.legend(fontsize=8, loc="best")
        axes[2].plot(ds.temp_layer.isel(column=0)-273.15, ds.z_layer/1000., color="#293241")
        axes[2].axhspan(base/1000., (base+depth)/1000., color="#d9e9f5", label="Synthetic cloud")
        axes[2].axvline(0, color="gray", ls=":")
        axes[2].set(title="C. Prescribed atmosphere", xlabel="Temperature (°C)", ylabel="Altitude (km)", ylim=(0, max(12., (base+depth)/1000.+1.)))
        axes[2].legend(fontsize=9)
        fig.suptitle(f"Synthetic cloud: depth {depth:g} m | LWP {float(ds.lwp.sum()):g} g m⁻² | IWP {float(ds.iwp.sum()):g} g m⁻²", fontweight="bold", fontsize=15)
        _tidy(axes)
    return fig


def plot_fluxes(ds):
    """Directional and net flux quicklooks; clear dashed, all-sky solid."""
    with plt.rc_context(_plot_style()):
        fig, axes = plt.subplots(1, 3, figsize=(14, 5.4), constrained_layout=True)
        height = ds.z_level / 1000.
        for ax, band, title in zip(axes[:2], ("sw", "lw"), ("A. Shortwave", "B. Longwave")):
            for direction, color in (("down", "#1565a8"), ("up", "#cf6032")):
                for suffix, style, sky in (("", "-", "All sky"), ("_clear", "--", "Clear sky")):
                    ax.plot(ds[f"{band}_flux_{direction}{suffix}"].isel(column=0), height,
                            color=color, ls=style, label=f"{sky}: {direction}")
            ax.set_title(title)
            ax.legend(fontsize=9)
        for suffix, style, sky in (("", "-", "All sky"), ("_clear", "--", "Clear sky")):
            axes[2].plot(ds[f"total_flux_net{suffix}"].isel(column=0), height,
                         color="#49358b", ls=style, label=sky)
        axes[2].axvline(0, color="gray", lw=1)
        axes[2].set_title("C. SW + LW net downward")
        axes[2].legend(fontsize=9)
        for ax in axes:
            ax.axhspan(ds.attrs["cloud_base_m"]/1000., (ds.attrs["cloud_base_m"]+ds.attrs["cloud_depth_m"])/1000., color="#d9e9f5", alpha=.65, zorder=0)
            ax.set(xlabel=r"Flux (W m$^{-2}$)", ylabel="Altitude (km)", ylim=(0, 20))
        fig.suptitle("Clear-sky and all-sky radiation | lower 20 km of a 60 km column", fontsize=15, fontweight="bold")
        _tidy(axes)
    return fig


def boundary_summary(ds):
    """Compact table of cloudy/clear net fluxes and CRE at surface and model top (an approximation to TOA)."""
    rows = []
    for name, index in (("Surface", 0), ("Model top (60 km)", -1)):
        for band in ("sw", "lw", "total"):
            rows.append({"Boundary": name, "Band": band.upper(),
                         "Clear net (W/m²)": float(ds[f"{band}_flux_net_clear"].isel(column=0, level=index)),
                         "All-sky net (W/m²)": float(ds[f"{band}_flux_net"].isel(column=0, level=index)),
                         "CRE (W/m²)": float(ds[f"{band}_cre"].isel(column=0, level=index))})
    import pandas as pd
    return pd.DataFrame(rows)


def plot_cre(ds):
    """CRE profile and boundary budget; positive means more net downward flux."""
    with plt.rc_context(_plot_style()):
        fig, axes = plt.subplots(1, 2, figsize=(12.5, 5.2), constrained_layout=True)
        colors = {"sw": "#d49422", "lw": "#b84456", "total": "#49358b"}
        for band in colors:
            axes[0].plot(ds[f"{band}_cre"].isel(column=0), ds.z_level/1000., color=colors[band], label=band.upper())
        axes[0].axvline(0, color="gray", lw=1)
        axes[0].set(title="A. Cloud radiative effect", xlabel=r"All sky − clear sky net flux (W m$^{-2}$)", ylabel="Altitude (km)", ylim=(0, 20))
        axes[0].legend()
        positions = np.arange(2)
        for i, band in enumerate(colors):
            values = [float(ds[f"{band}_cre"].isel(column=0, level=j)) for j in (0, -1)]
            axes[1].bar(positions + (i-1)*.24, values, .24, color=colors[band], label=band.upper())
        axes[1].axhline(0, color="gray", lw=1)
        axes[1].set_xticks(positions, ["Surface", "Model top\n(60 km)"])
        axes[1].set(title="B. Boundary energy change", ylabel=r"CRE (W m$^{-2}$)")
        axes[1].legend()
        fig.suptitle("Cloud radiative effect: positive = more net downward energy", fontweight="bold", fontsize=15)
        _tidy(axes)
    return fig


def save_case(result, output_dir="outputs", stem="baseline"):
    """Save reproducible inputs/results plus three readable PNG quicklooks."""
    if not stem or Path(stem).name != stem:
        raise ValueError("stem must be a simple filename without directory separators")
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    paths = {"netcdf": output / f"{stem}_radiation.nc"}
    result.to_netcdf(paths["netcdf"])
    for name, plot in (("profiles", plot_profiles), ("fluxes", plot_fluxes), ("cre", plot_cre)):
        paths[name] = output / f"{stem}_{name}.png"
        fig = plot(result)
        fig.savefig(paths[name], dpi=170)
        plt.close(fig)
    paths["summary"] = output / f"{stem}_boundary_summary.csv"
    boundary_summary(result).to_csv(paths["summary"], index=False)
    return paths


def verify_reference(data_dir=None):
    """Compare against the official 24-column all-sky SW/LW reference case.

    This deliberately reproduces the upstream test inputs exactly, including
    upstream example gas numbers. It is separate from our teaching atmosphere.
    The reference case includes eight cloud-free and sixteen cloudy columns.
    """
    from pyrte_rrtmgp.examples import compute_RCE_profiles, compute_RCE_clouds
    path = find_data_dir(data_dir)
    optics = _load_optics(str(path))
    atmosphere = compute_RCE_profiles(300, 24, 72)
    for gas, vmr in {"co2": 348.e-6, "ch4": 1650.e-9, "n2o": 306.e-9,
                     "n2": .7808, "o2": .2095, "co": 0.}.items():
        atmosphere[gas] = vmr
    atmosphere = atmosphere.merge(compute_RCE_clouds(optics["lw_cloud"], atmosphere.pres_layer, atmosphere.temp_layer))
    fluxes = _solve_fluxes(atmosphere, optics, True, .06, .86, .98)
    errors = {}
    for band in ("sw", "lw"):
        reference_path = path / "examples" / "all-sky" / "reference" / f"rrtmgp-allsky-{band}-no-aerosols.nc"
        with xr.open_dataset(reference_path, decode_cf=False) as reference:
            for direction, ref_direction in (("up", "up"), ("down", "dn")):
                name = f"{band}_flux_{direction}"
                expected = reference[f"{band}_flux_{ref_direction}"].values.T
                actual = fluxes[name].values
                np.testing.assert_allclose(actual, expected, rtol=1.e-5, atol=1.e-7,
                                           err_msg=f"Official reference failed: {name}")
                errors[name] = float(np.max(np.abs(actual-expected)))
    return errors
