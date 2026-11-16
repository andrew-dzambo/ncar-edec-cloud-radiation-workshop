# NCAR EDEC Cloud Radiation Workshop

**Build a cloud, change the radiation.** This activity explores computing clear-sky and all-sky radiation quantities using RTE+RRTMGP.

A 50-minute Python/Jupyter activity for 20–30 participants, prepared for Andrew Dzambo's Synthetic Satellite Footprint Project. Run the model on a **Linux x86_64 server**; use Windows PowerShell or macOS Terminal to connect, and your laptop browser to view Jupyter. No local Fortran compiler is needed.

Start with the [GETTING_STARTED.md](GETTING_STARTED.md) markdown file and keep this open in another tab. Open [RRTMGP_Cloud_Workshop.ipynb](RRTMGP_Cloud_Workshop.ipynb) - this will be the main notebook for the activity. The notebook downloads/checks the pinned model components, runs actual RTE+RRTMGP calculations, and saves radiation and cloud-profile figures. The accompanying Python module contains the "model plumbing" so participants can focus on experiments. Keep the notebook and companion files together. [INSTRUCTOR_GUIDE.md](INSTRUCTOR_GUIDE.md) gives the class plan and GitHub instructions; [VALIDATION.md](VALIDATION.md) records what was tested and the remaining server preflight. The [examples](examples/) folder contains a [completed reference notebook](examples/RRTMGP_Cloud_Workshop_reference.ipynb) and [sample outputs](examples/outputs/).

## Learning goals

- Distinguish incoming sunlight, reflected sunlight, and thermal infrared radiation.
- Explain what RRTMGP computes and what RTE solves.
- Construct a cloud from a depth and column liquid/ice water paths.
- Compare clear and cloudy fluxes.
- Make and test a prediction, then save a short result in a GitHub fork.

## Before the activity begins

Have a GitHub account and fork [this workshop repository](https://github.com/andrew-dzambo/ncar-edec-cloud-radiation-workshop) (not the upstream RRTMGP repository). Confirm Linux SSH access, run `bash setup_workshop.sh`, then `bash launch_workshop.sh 8888`. First-time package and coefficient downloads are prework; their time depends on network and server policy. The notebook repeats this setup check safely. The instructor should preflight the exact server in advance. The tested environment requires Linux x86_64 with glibc >=2.28; allow at least 4 GB disk space including downloads and caches (about 1.6 GB installed environment).

## Class timeline

| Minutes | Activity |
|---|---|
| 0–5 | Open notebook; predict how a cloud changes surface sunlight |
| 5–10 | Verify installation, versions, coefficients, and vocabulary |
| 10–20 | Run baseline clear and cloudy columns; read the flux quicklooks |
| 20–30 | Build a synthetic cloud; verify liquid and ice mass budgets |
| 30–42 | Change one variable; compare surface and top-of-atmosphere effects |
| 42–47 | Interpret results with a partner and state one assumption |
| 47–50 | Save a short result and upload it to your GitHub fork |

## Version choices

| Component | Pin | Role |
|---|---|---|
| Executing Fortran library | `rte_rrtmgp=1.9.2` | Precompiled library used by Python |
| Official Python interface | `pyrte_rrtmgp=0.2.5` | Calls the compiled routines |
| RTE+RRTMGP source | v1.9.3, `c4098f552dc362986d67a32377c511d60b1d3d1b` | Source downloaded for inspection; not substituted for the executing library |
| Python source | v0.2.5, `2fcb4eb306708c8a38974f34371c4206a505ce9f` | Reference implementation |
| Coefficient data | v1.9, `eff0433faf9cbac3ad14fbf608bef0c26ebc4c79` | Gas and cloud optical lookup tables |

## Cloud and flux conventions

Cloud depth can be between 50–3000 m. LWP and IWP are entered in **g m⁻²**; LWC and IWC are plotted in **g m⁻³**. At normalized altitude `x=(z-cloud_base)/cloud_depth`, liquid follows `30*x**4*(1-x)` and ice follows `60*x**2*(1-x)**3` inside the cloud, zero outside. Their smooth maxima occur at 0.8 and 0.4, respectively. Exact integrals give each layer's mass, so changing resolution does not change the column water budget. These profiles are purely for demonstration purposes only. See Pincus et al. (2019) for additional examples.

All-sky here means a horizontally uniform, fully cloudy column wherever cloud mass is present. Clear-sky uses the same atmosphere and boundary conditions with cloud mass removed. Net flux is **down minus up**. Cloud radiative effect (CRE) is **all-sky net minus clear-sky net**. Positive surface CRE means more net radiative energy entering the surface; positive model-top CRE means more net radiative energy entering the atmospheric column plus surface. The model ends at 60 km, used as an approximate top-of-atmosphere boundary.

## Reference and upstream sources

Pincus, R., Mlawer, E. J., and Delamere, J. S.: Balancing accuracy, efficiency, and flexibility in radiation calculations for dynamical models, *J. Adv. Model. Earth Syst.*, **11**, 3074–3089, https://doi.org/10.1029/2019MS001621, 2019.

- Core code: https://github.com/earth-system-radiation/rte-rrtmgp
- Python interface: https://github.com/earth-system-radiation/pyRTE-RRTMGP
- Coefficient data: https://github.com/earth-system-radiation/rrtmgp-data
- Python documentation: https://earth-system-radiation.github.io/pyRTE-RRTMGP/

Paper explanations in the notebook are paraphrases with section references. The paper PDF is not redistributed. Upstream repositories retain their own licenses and notices. Licensing of the original workshop materials is managed separately from those upstream components.
