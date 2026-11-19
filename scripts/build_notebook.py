"""Rebuild the short, five-cell workshop notebook using only the standard library."""
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
cells = []


def add_cell(kind, text):
    cell = {
        "cell_type": kind,
        "id": f"workshop-{len(cells):02d}",
        "metadata": {},
        "source": text.strip().splitlines(keepends=True),
    }
    if kind == "code":
        cell.update(execution_count=None, outputs=[])
    cells.append(cell)


def md(text):
    add_cell("markdown", text)


def code(text):
    add_cell("code", text)


md('''# Build a cloud, change the radiation
### A 50-minute RTE+RRTMGP experiment

**Question:** How does the amount and vertical placement of liquid water and ice change the radiation reaching the surface and escaping toward space?

## 1. Open and check — 0–10 minutes

Open your own GitHub Codespace or Linux checkout using the [participant instructions](GETTING_STARTED.md). In your personal workspace, select **Python (RRTMGP Workshop)** or the interpreter in `envs/rrtmgp/bin/python`. Press **Shift+Enter** to run each of the five code cells in order.

The first cell checks your installation. While it starts, predict whether adding liquid water will increase or decrease sunlight reaching the surface. If setup is still running at minute 10, open the [saved-run activity](SAVED_RUN.md).

**Plan:** open/check (0–10), baseline (10–20), build/run (20–35), compare (35–43), explain/download (43–50).''')
code('''from pathlib import Path
from scripts.workshop_runtime import prepare_notebook

ROOT = Path.cwd().resolve()
ready = prepare_notebook(ROOT)  # Checks the prepared runtime; does not install or download.
print(f"Ready: Python {ready['python_version']}, pyRTE {ready['pyrte_rrtmgp_version']}, "
      f"RRTMGP {ready['rte_rrtmgp_version']} ({ready['mode']} environment).")

import numpy as np
import pandas as pd
from IPython.display import display, Image, FileLink
from workshop_model import build_column, run_column, save_case, boundary_summary

OUTPUT = ROOT / "outputs"
OUTPUT.mkdir(exist_ok=True)
print("Ready to run the baseline.")''')
md('''## 2. Baseline: follow the energy — 10–20 minutes

**Shortwave (SW)** is sunlight; **longwave (LW)** is thermal infrared radiation. Flux is power per area, in **W m⁻²**.

RRTMGP converts temperature, pressure, and gases into optical properties; RTE uses those properties to calculate fluxes. Cloud optics are supplied separately. This lets us change clouds while holding the atmosphere fixed. *(Pincus et al., 2019, sections 2.2–2.4; paraphrased.)*

**Clear sky** removes cloud water and ice. **All sky** includes our horizontally uniform cloud: cloud fraction is one within the cloud. Both runs use identical prescribed temperature, gases, sunlight, and surface properties.

The baseline has depth **1000 m**, liquid water path **100 g m⁻²**, and ice water path **30 g m⁻²**, with cloud base at 1.5 km. Solid curves are all sky; dashed curves are clear sky. Net flux means **down minus up**.

**Discuss:** How does the cloud change downward SW and LW at the surface?''')
code('''baseline_parameters = dict(depth_m=1000.0, lwp_gm2=100.0, iwp_gm2=30.0)
baseline = run_column(build_column(**baseline_parameters))
baseline_files = save_case(baseline, OUTPUT, "baseline")
display(Image(filename=str(baseline_files["fluxes"])))
baseline_summary = boundary_summary(baseline)
display(baseline_summary.loc[baseline_summary["Boundary"] == "Surface"].round(2))''')
md('''## 3. Build and run your cloud — 20–35 minutes

Edit **one** of the three parameters below; leave the other two at baseline values. The example doubles liquid water path. Write a short prediction, then run the cell.

**LWP/IWP** are column liquid/ice mass per area (**g m⁻²**). **LWC/IWC** are mass per volume (**g m⁻³**). The smooth liquid curve peaks 80% of the way from cloud base to top; ice peaks at 40%. These are chosen teaching shapes. The code integrates them through each layer so the total mass matches your inputs, even for a 50 m cloud.

Pincus et al. emphasize that users must supply the cloud-to-optics mapping (section 4). Our particle sizes, cloud shapes, and prescribed atmosphere are workshop assumptions. Temperature and humidity do not respond to the added cloud; no condensation or precipitation is simulated.''')
code('''# EDIT ONE PARAMETER; baseline values are depth=1000, LWP=100, IWP=30.
CLOUD_DEPTH_M = 1000.0   # Allowed: 50–3000 m.
LWP_G_M2 = 200.0         # Nonnegative liquid water path, g/m².
IWP_G_M2 = 30.0          # Nonnegative ice water path, g/m².
PREDICTION = ""          # Write one sentence before running.
EXPERIMENT_NAME = "experiment01"  # Change this name to keep another run.

atmosphere = build_column(depth_m=CLOUD_DEPTH_M, lwp_gm2=LWP_G_M2, iwp_gm2=IWP_G_M2)
recovered = [float((atmosphere[name] * atmosphere.layer_thickness).sum())
             for name in ("lwc", "iwc")]
np.testing.assert_allclose(recovered, [LWP_G_M2, IWP_G_M2], rtol=1e-12, atol=1e-10)
print(f"Mass check passed: LWP={recovered[0]:g}, IWP={recovered[1]:g} g/m².")
experiment = run_column(atmosphere)
experiment_files = save_case(experiment, OUTPUT, EXPERIMENT_NAME)
display(Image(filename=str(experiment_files["profiles"])))
print("Your cloud has been calculated and saved. Continue to the comparison.")''')
md('''## 4. Compare and discuss — 35–43 minutes

**Cloud radiative effect (CRE)** is all-sky net flux minus clear-sky net flux. Positive surface CRE adds downward energy to the surface. The model top at 60 km approximates the top of the atmosphere; positive CRE there adds energy to the combined atmosphere–surface system.

Run the comparison. Did your prediction hold? Explain one change using reflection, absorption, or emission. At fixed paths, increasing depth spreads the same mass over more height. Each cloudy run has its own matching clear run; compare their CREs.

Radiation is calculated in one vertical column without exchange with neighboring columns. This illustrates the independent-column assumption discussed by Pincus et al. (introduction and section 2.2).''')
code('''display(Image(filename=str(experiment_files["fluxes"])))
comparison = baseline_summary[["Boundary", "Band", "CRE (W/m²)"]].rename(
    columns={"CRE (W/m²)": "Baseline CRE (W/m²)"}).merge(
    boundary_summary(experiment)[["Boundary", "Band", "CRE (W/m²)"]].rename(
        columns={"CRE (W/m²)": "Experiment CRE (W/m²)"}), on=["Boundary", "Band"])
comparison["Change in CRE (W/m²)"] = (
    comparison["Experiment CRE (W/m²)"] - comparison["Baseline CRE (W/m²)"])
display(comparison.round(2))''')
md('''## 5. Explain and download — 43–50 minutes

Complete the interpretation below: **I changed ___. The surface CRE changed by ___ W m⁻² because ___. One simplifying assumption is ___.** Run the cell, save the notebook, and download **one CSV and one PNG** using the links. These downloads complete the activity.

If time remains, save them in your GitHub account using **Add file → Upload files** in your own repository or fork. GitHub upload is optional.

Equations, model settings, extra experiments, and verification details are in [SCIENCE_NOTES.md](SCIENCE_NOTES.md); they are optional reference material.

Reference: Pincus, R., Mlawer, E. J., and Delamere, J. S. (2019), *JAMES*, 11, 3074–3089, [doi:10.1029/2019MS001621](https://doi.org/10.1029/2019MS001621).''')
code('''INTERPRETATION = ""  # Write your explanation here, then run this cell.

record = comparison.copy()
record["experiment_name"] = EXPERIMENT_NAME
record["baseline_depth_m"] = baseline_parameters["depth_m"]
record["baseline_lwp_g_m2"] = baseline_parameters["lwp_gm2"]
record["baseline_iwp_g_m2"] = baseline_parameters["iwp_gm2"]
record["experiment_depth_m"] = experiment.attrs["cloud_depth_m"]
record["experiment_lwp_g_m2"] = experiment.attrs["requested_lwp_gm2"]
record["experiment_iwp_g_m2"] = experiment.attrs["requested_iwp_gm2"]
record["prediction"] = PREDICTION
record["interpretation"] = INTERPRETATION
record.to_csv(OUTPUT / "experiment_record.csv", index=False)
record.to_csv(OUTPUT / f"{EXPERIMENT_NAME}_record.csv", index=False)
print("Download your CSV and PNG below. Add your explanation if still blank, then rerun.")
display(FileLink("outputs/experiment_record.csv"))
display(FileLink(str(experiment_files["fluxes"].relative_to(ROOT))))''')

notebook = {
    "cells": cells,
    "metadata": {
        "kernelspec": {"display_name": "Python (RRTMGP Workshop)",
                       "language": "python", "name": "rrtmgp-workshop"},
        "language_info": {"name": "python", "version": "3.11"},
    },
    "nbformat": 4,
    "nbformat_minor": 5,
}
path = ROOT / "RRTMGP_Cloud_Workshop.ipynb"
path.write_text(json.dumps(notebook, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
words = sum(len(re.findall(r"\S+", "".join(c["source"]))) for c in cells if c["cell_type"] == "markdown")
print(f"Wrote {path.name}: {len(cells)} cells; {sum(c['cell_type']=='code' for c in cells)} code cells; {words} Markdown words.")
