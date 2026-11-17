# Start the workshop: minutes 0–10

All participant setup happens during the 50-minute activity. Use your Windows or Mac laptop browser. The facilitator will provide the **Jupyter URL**, **login details**, and **shared workshop directory** at the start. No local Python, terminal, or model installation is needed.

## 0–2 minutes: sign in

Open the facilitator's JupyterHub/Open OnDemand URL and sign in. Open the workshop's JupyterLab session using the facilitator's instructions. If sign-in fails, ask for help immediately.

## 2–5 minutes: get your working copy

In JupyterLab, open **Terminal** from the launcher. Run these commands in that terminal, replacing `/SHARED/WORKSHOP_DIR` with the exact directory supplied by the facilitator:

```bash
cd ~
git clone https://github.com/andrew-dzambo/ncar-edec-cloud-radiation-workshop.git
cd ncar-edec-cloud-radiation-workshop
bash configure_workshop.sh /SHARED/WORKSHOP_DIR
```

This downloads your own small copy and configures it to use the prepared model environment and coefficients. It does not install packages. If you already have this folder, open it and run the `configure_workshop.sh` command there instead of cloning again.

## 5–8 minutes: open the notebook

In JupyterLab's file browser, open `ncar-edec-cloud-radiation-workshop`, then **RRTMGP_Cloud_Workshop.ipynb**. Choose **Python (RRTMGP Workshop)** as the kernel. Refresh the page if the new kernel is not listed.

The notebook on GitHub is a preview; run your copy inside JupyterLab.

## 8–10 minutes: check readiness and begin

Run the notebook's readiness section with **Shift+Enter**, then begin the baseline calculation. Follow the notebook for the remaining activity.

**If you are not running by minute 10:** ask the facilitator for a prepared notebook copy or pair with someone whose session works. Do not start a package installation during the activity. Supplied reference figures can support discussion if the service is unavailable, but they are not results from your own model run.

## Finish by minute 50

Save the notebook. In JupyterLab's file browser, open `outputs`, then download **experiment_record.csv** and one experiment **PNG**. These are your activity results.

Forking the [repository](https://github.com/andrew-dzambo/ncar-edec-cloud-radiation-workshop) and uploading selected results to your GitHub account are optional after the activity. See the [facilitator guide](INSTRUCTOR_GUIDE.md#optional-github-follow-up) for that procedure.
