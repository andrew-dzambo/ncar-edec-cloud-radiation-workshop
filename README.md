# NCAR EDEC Cloud Radiation Workshop

**Build a cloud, change the radiation.** In this 50-minute activity, participants run RTE+RRTMGP, change a synthetic cloud, and save clear-sky/all-sky radiation results. All participant setup is included in the activity.

Use a Windows or Mac laptop browser to access the organizer's prepared Linux Jupyter service. Participants download a small working copy of this repository and select the shared workshop environment; they do not install the model or its dependencies.

**Start here:** [Participant instructions](GETTING_STARTED.md) → [Workshop notebook](RRTMGP_Cloud_Workshop.ipynb).

The organizer must supply a working JupyterHub/Open OnDemand URL, access credentials, and the shared workshop directory. See the [facilitator guide](INSTRUCTOR_GUIDE.md) for deployment and rehearsal. This repository does not mean that an institutional server has already been configured.

## The 50-minute activity

| Minutes | Activity |
|---|---|
| 0–2 | Sign in to the organizer's Jupyter service |
| 2–5 | Download your working copy and configure the shared environment |
| 5–8 | Open the notebook and choose the workshop kernel |
| 8–10 | Run the readiness check and begin the baseline |
| 10–20 | Compare baseline clear-sky and all-sky fluxes |
| 20–35 | Create your cloud and check its water budget |
| 35–43 | Compare the radiation response |
| 43–50 | Save a PNG and CSV; discuss the result |

Ten minutes is the startup target for a rehearsed, prepared service. Creating accounts or installing a model on an arbitrary server is not part of that target. GitHub forking and uploading results are optional follow-up activities.

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
