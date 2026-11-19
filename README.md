# NCAR EDEC Cloud Radiation Workshop

Build a cloud and measure how it changes sunlight and thermal radiation in **50 minutes**. Each person runs the notebook in their own Linux workspace. Windows and Mac users can use the browser option.

**[Start here: create my GitHub Codespace](https://codespaces.new/andrew-dzambo/ncar-edec-cloud-radiation-workshop/tree/main?quickstart=1)**

**[Participant instructions, including your own Linux or SSH login](GETTING_STARTED.md)** · [Workshop notebook](RRTMGP_Cloud_Workshop.ipynb) · [Saved-run activity if setup is slow](SAVED_RUN.md)

Allow the first 10 minutes for startup. The first launch downloads the pinned model and data. At minute 10, participants who are still waiting can work with the supplied baseline and doubled-liquid runs directly on GitHub. Run the baseline by minute 20, change one cloud property by minute 35, then compare the fluxes and save your PNG and CSV by minute 50. [Facilitator instructions](INSTRUCTOR_GUIDE.md).

## What you control

Set cloud depth to **50–3000 m**, liquid water path (LWP), and ice water path (IWP). The prescribed liquid and ice profiles peak at **0.8** and **0.4** of normalized cloud altitude and conserve the requested water paths. Paths use **g m⁻²**; contents use **g m⁻³**.

Clear and all-sky runs use the same atmosphere. Here, all sky means one fully cloudy horizontal column where cloud mass is present. Net flux is **down minus up**; cloud radiative effect is **all-sky net minus clear-sky net**. These are idealized optical experiments, not observed cloud retrievals.

## Model versions and further reading

| Component | Version |
|---|---|
| Executing Fortran library | `rte_rrtmgp=1.9.2` |
| Python interface | `pyrte_rrtmgp=0.2.5` |
| Coefficient data | v1.9 |
| Separate core source for inspection | v1.9.3 |

Exact source pins and coefficient hashes are in [provenance.json](provenance.json). See [SCIENCE_NOTES.md](SCIENCE_NOTES.md) for optional explanations, [VALIDATION.md](VALIDATION.md) for checks and limitations, and [examples](examples/) for a completed reference run and sample outputs.

Pincus, R., Mlawer, E. J., and Delamere, J. S.: Balancing accuracy, efficiency, and flexibility in radiation calculations for dynamical models, *J. Adv. Model. Earth Syst.*, **11**, 3074–3089, [doi:10.1029/2019MS001621](https://doi.org/10.1029/2019MS001621), 2019. The synthetic cloud shapes are workshop choices. Upstream [core code](https://github.com/earth-system-radiation/rte-rrtmgp), [Python interface](https://github.com/earth-system-radiation/pyRTE-RRTMGP), and [data](https://github.com/earth-system-radiation/rrtmgp-data) retain their own licenses and notices.
