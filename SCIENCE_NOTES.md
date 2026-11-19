# Optional science and implementation reference

The five-cell notebook is the complete 50-minute activity. These notes contain derivations, settings, and optional investigations for readers who want more detail; none is required to finish the activity.

## What RRTMGP and RTE each do

RRTMGP maps atmospheric pressure, temperature, and gas concentrations to optical properties and emission sources. RTE uses those properties and boundary conditions to calculate radiative fluxes. Cloud optical properties are supplied by a separate mapping and added to the gas properties for a cloudy calculation. Pincus et al. (2019), sections 2.2–2.4, pp. 3077–3079, explain this separation.

Gas absorption varies strongly across the spectrum. The correlated-k method groups absorption of similar strength within spectral bands and approximates spectral integrals using weighted samples called **g-points**. A g-point is not one fixed wavelength. The spectral mapping is treated as correlated between atmospheric layers; imperfect correlation is one source of error. Lookup tables are part of the model configuration because their design affects accuracy and computational cost. See Pincus et al., sections 2.3 and 3.1, pp. 3078 and 3080–3081.

This workshop uses one independent, plane-parallel column. No radiation is exchanged with neighboring columns. Shortwave calculations include scattering through a two-stream solver with delta scaling of cloud optics. The selected longwave calculation includes absorption and emission, uses one quadrature angle, and neglects longwave scattering. RTE supports other choices; neglect of longwave scattering is this workshop's configuration, not a universal RRTMGP restriction. See Pincus et al., introduction and section 2.2.

## Synthetic cloud profiles

Let cloud base be \(z_b\), cloud depth be \(H\), and normalized height be

$$x=\frac{z-z_b}{H}.$$

For \(0\le x\le1\), the prescribed profiles are

$$\mathrm{LWC}(z)=\frac{\mathrm{LWP}}{H}\,30x^4(1-x),$$

$$\mathrm{IWC}(z)=\frac{\mathrm{IWP}}{H}\,60x^2(1-x)^3.$$

Both contents are zero outside the cloud. With water paths in g m⁻² and depth in m, contents are in g m⁻³. The shape factors are beta probability densities: Beta(5,2) for liquid and Beta(3,4) for ice. They each integrate to one with respect to \(x\). Their interior modes are

$$x_{\mathrm{mode}}=\frac{a-1}{a+b-2},$$

which gives **0.8 for liquid** and **0.4 for ice**. If a phase's total path is zero, its content is zero everywhere and it has no unique peak. These skewed shapes supply a curved rise and fall with an interior maximum; they are not literal exponential functions and are not profiles prescribed by Pincus et al.

The cumulative integrals are

$$C_L(x)=6x^5-5x^6,$$

$$C_I(x)=20x^3-45x^4+36x^5-10x^6.$$

For each layer, the code clips its normalized lower and upper boundaries to \([0,1]\), then assigns

$$\Delta\mathrm{LWP}_j=\mathrm{LWP}\,[C_L(x_{j+1})-C_L(x_j)],$$

and likewise for ice. The implementation evaluates these integrals with `scipy.special.betainc` for numerical stability. Dividing each layer path by layer thickness gives the layer-mean content used in the model. Thus

$$\sum_j \overline{\mathrm{LWC}}_j\,\Delta z_j=\mathrm{LWP},\qquad
\sum_j \overline{\mathrm{IWC}}_j\,\Delta z_j=\mathrm{IWP}.$$

Use this sum for mass checks. A trapezoidal integral of layer-center values is a different discretization and need not recover the exact path. Cloud boundaries coincide with grid interfaces; clouds have at least 40 layers even at the 50 m minimum depth. The plot shows the continuous target and layer means. A maximum among layer means can differ slightly from the continuous mode.

## Prescribed atmosphere and optical choices

| Quantity | Workshop value or assumption |
|---|---|
| Cloud depth | 50–3000 m; baseline 1000 m |
| Cloud base | 1500 m in the main notebook |
| Baseline total LWP / IWP | 100 / 30 g m⁻² |
| Liquid effective radius | 10 µm |
| Ice effective diameter | 60 µm |
| Ice roughness | Index 1, the second tabulated category in the pinned wrapper |
| Horizontal cloud fraction | 1 wherever cloud mass is present |
| Surface temperature / pressure | 278 K / 101325 Pa |
| Surface albedo / emissivity | 0.15 / 0.98 |
| Solar zenith angle | 60° |
| Model top | 60 km, approximately 20.3 Pa; an approximate top-of-atmosphere boundary |
| Temperature and gases | Prescribed analytic profiles; not CAESAR observations |
| Pressure profile | Dry hydrostatic calculation through the prescribed temperature profile |
| Aerosols | Absent |
| Feedbacks | No temperature/humidity adjustment, condensation, freezing, precipitation, or latent heating |

The cloud-optics interface requires **water path in each layer**, not the total column path repeated in every layer. In pyRTE-RRTMGP 0.2.5, the input named `rei` is passed to an **ice effective-diameter** lookup table despite its radius-like name. The helper therefore passes the 60 µm diameter unchanged. Liquid `rel` is an effective radius. Different particle sizes or ice optical assumptions can change radiation even if LWP and IWP are unchanged.

Pincus et al., section 4, pp. 3086–3087, emphasize that users supply the cloud-to-optics mapping appropriate to their application. Our synthetic profiles, fixed sizes, and atmospheric state are teaching choices. Very thin, massive clouds or imposed phase at unsuitable temperatures can be unrealistic even if the radiative equations return finite values. This activity does not reproduce a ROMANS aircraft retrieval or satellite-footprint calculation.

## Fluxes, cloud radiative effect, and heating

Upward and downward fluxes are positive magnitudes in their respective directions. The notebook defines net flux as downward minus upward:

$$F_{\mathrm{net}}=F_{\downarrow}-F_{\uparrow}.$$

Cloud radiative effect is calculated separately for SW, LW, and their sum:

$$\mathrm{CRE}=F_{\mathrm{net,all}}-F_{\mathrm{net,clear}}.$$

The clear and cloudy runs have identical temperature, gases, grid, sunlight, and surface conditions. The clear calculation omits condensed-water optics. Positive surface CRE adds net radiative energy to the surface; positive model-top CRE adds energy to the combined atmosphere–surface system. Neither boundary value alone equals atmospheric heating. Atmospheric absorption depends on the difference between net flux entering at the top and leaving at the bottom.

Depth changes also alter the vertical grid. Each experiment therefore has its own matched clear/cloudy pair; compare paired CREs instead of assuming clear fluxes are identical across depth experiments. At fixed paths and sizes, total cloud optical depth can remain similar while vertical temperature placement and the distribution relative to absorbing gas change. A depth response is not guaranteed to be monotonic.

NetCDF outputs include diagnostic heating rates. With pressure increasing downward and net flux defined downward,

$$Q=-\frac{g}{c_p}\frac{\partial F_{\mathrm{net}}}{\partial p}\,86400
\qquad[\mathrm{K\,day^{-1}}].$$

The factor converts seconds to days. The workshop uses \(g=9.80665\) m s⁻² and dry-air \(c_p=1004\) J kg⁻¹ K⁻¹. This is an instantaneous flux-divergence diagnostic; atmospheric temperature is not advanced.

## Reproducibility

| Component | Pin | Role |
|---|---|---|
| Executing Fortran library | `rte_rrtmgp=1.9.2` | Precompiled routines called by Python |
| Official Python interface | `pyrte_rrtmgp=0.2.5` | Model interface |
| RTE+RRTMGP source | v1.9.3, `c4098f552dc362986d67a32377c511d60b1d3d1b` | Source for inspection; not the executing 1.9.2 library |
| Python source | v0.2.5, `2fcb4eb306708c8a38974f34371c4206a505ce9f` | Reference source |
| Coefficient data | v1.9, `eff0433faf9cbac3ad14fbf608bef0c26ebc4c79` | Gas and cloud tables |

The four selected files are `rrtmgp-gas-sw-g224.nc`, `rrtmgp-gas-lw-g256.nc`, `rrtmgp-clouds-sw-bnd.nc`, and `rrtmgp-clouds-lw-bnd.nc`. They provide 224 SW and 256 LW gas g-points. Downloaded source and executing library versions are deliberately reported separately, matching the prior ROMANS setup.

`save_case` writes the atmospheric inputs and radiation results to NetCDF; cloud-profile, flux, and CRE PNGs; and a boundary-summary CSV. The NetCDF includes coefficient hashes, versions, input parameters, native and clear-sky fluxes, net fluxes, CREs, and heating diagnostics. The main notebook's final CSV also retains the prediction and interpretation.

## Optional verification

Personal workspace setup installs the model and data. The first notebook cell checks that installation. The instructor can run the package validation separately. These checks establish implementation consistency, not the uncertainty of an arbitrary invented cloud.

After the notebook's first cell has run, the official reference check can also be run in an additional cell:

```python
from workshop_model import verify_reference
verify_reference()
```

This reproduces the upstream 24-column all-sky example, including eight cloud-free and sixteen cloudy columns, and compares SW/LW upward and downward fluxes against the supplied reference files. The acceptance tolerance is `rtol=1e-5`, `atol=1e-7 W m⁻²`. The paper's benchmark accuracy statistics are specific to its tested configurations; they are not an error bound for these synthetic clouds.

A separate physical consistency check is:

```python
empty = run_column(build_column(depth_m=1000, lwp_gm2=0, iwp_gm2=0))
for band in ("sw", "lw", "total"):
    np.testing.assert_allclose(
        empty[f"{band}_flux_net"], empty[f"{band}_flux_net_clear"],
        rtol=1e-10, atol=1e-8,
    )
```

## Optional additional experiments

Keep the baseline at depth 1000 m, LWP 100 g m⁻², and IWP 30 g m⁻². Change one quantity at a time, use a fresh experiment name, and rerun notebook cells 3–5 to retain a separate result record.

- Increase IWP to 100 g m⁻². Compare the response with doubling LWP.
- Set LWP to zero while retaining IWP. Which phase dominates this particular mixed-phase example?
- Double depth to 2000 m at fixed paths. Explain why the average contents fall without a change in total mass.
- Compare two additional runs at 50 m and 3000 m with fixed paths. The built-in table compares each with the 1000 m baseline; compare the two saved records directly for the 50-to-3000 m difference.
- Remove both phases. The all-sky and clear-sky calculations should agree.

## Reference and source links

Pincus, R., Mlawer, E. J., and Delamere, J. S.: Balancing accuracy, efficiency, and flexibility in radiation calculations for dynamical models, *J. Adv. Model. Earth Syst.*, **11**, 3074–3089, https://doi.org/10.1029/2019MS001621, 2019.

- [RTE+RRTMGP core](https://github.com/earth-system-radiation/rte-rrtmgp)
- [Official Python interface, v0.2.5](https://github.com/earth-system-radiation/pyRTE-RRTMGP/tree/v0.2.5)
- [Coefficient data, v1.9](https://github.com/earth-system-radiation/rrtmgp-data/tree/v1.9)

The teaching explanations paraphrase the supplied paper; the PDF is not redistributed.
