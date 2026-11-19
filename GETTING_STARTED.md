# Start your own cloud experiment

Choose **one** route. Windows and Mac users can do the entire activity in a browser with their own GitHub account. All setup happens during the workshop.

## A. My GitHub Codespace (Windows, Mac or Linux)

1. **[Create my Linux workspace](https://codespaces.new/andrew-dzambo/ncar-edec-cloud-radiation-workshop/tree/main?quickstart=1)**. Sign in with your own GitHub account. Choose **Create a new codespace** (or **Create codespace**) on `main`. If you previously used an older version of the workshop, create a fresh workspace.
2. GitHub opens a browser editor and runs the workshop installer automatically. It downloads the pinned Python environment, RRTMGP and its coefficient tables into your workspace. While it starts, predict what doubling the liquid water in a cloud will do to surface sunlight.
3. Open **RRTMGP_Cloud_Workshop.ipynb** in the file list if needed. At the top right click **Select Kernel**, then **Python (RRTMGP Workshop)**. If needed, choose **Select Another Kernel → Jupyter Kernel**. You can also select the Python environment whose interpreter ends in `envs/rrtmgp/bin/python`.
4. Click the first code cell and press **Shift+Enter**. When it prints **Ready to run the baseline**, continue below. If workspace creation failed, check the creation log. In a working terminal, you can retry with `bash setup_workshop.sh`. If you are still waiting at minute 10, use the [saved-run activity](SAVED_RUN.md).

Your codespace is private to your account. GitHub applies your available compute and storage allowance. Download your outputs first, then **Stop codespace** from [Your codespaces](https://github.com/codespaces). Delete it when you are finished with the saved files to release storage.

## B. My own Linux machine or Linux login

Use an **x86_64 Linux** terminal (Intel/AMD, glibc 2.28 or newer) with Git, curl, tar, bzip2, internet access and at least 4 GB of free disk space. Use route A for Apple Silicon, ARM Linux, or a laptop without Linux. Windows users with a compatible WSL2 Linux environment can use this route. Run the commands below in your own writable directory. On a cluster use your site's approved interactive session.

```bash
git clone --depth 1 https://github.com/andrew-dzambo/ncar-edec-cloud-radiation-workshop.git
cd ncar-edec-cloud-radiation-workshop
bash setup_workshop.sh && bash launch_workshop.sh 8888
```

Leave the terminal running. **On your Linux laptop or WSL2**, open the `http://127.0.0.1:8888/lab?token=...` address printed by Jupyter in your laptop browser. **On a remote Linux host**, start the tunnel below in a second terminal on your laptop (macOS Terminal or Windows PowerShell). Replace `YOU@HOST` with your login on the machine running Jupyter. If the port is occupied, choose another number in both commands. For a compute node behind a login node, use the site's documented jump-host route.

```text
ssh -N -L 8888:127.0.0.1:8888 YOU@HOST
```

Open the printed localhost URL, choose **RRTMGP_Cloud_Workshop.ipynb** and **Python (RRTMGP Workshop)**, then run the first code cell. All software and data live in your checkout. Each participant has their own files.

### Live model from the terminal

If setup finished but your notebook or kernel will not open, you can still run your own experiment in the same Linux terminal. From the workshop directory run:

```bash
envs/rrtmgp/bin/python run_terminal.py --depth 1000 --lwp 200 --iwp 30
```

The baseline is fixed at 1,000 m, 100 g/m² liquid and 30 g/m² ice. Choose a prediction and change one quantity from those baseline values. The command runs both cases, prints the comparison and writes the CSV, PNGs and NetCDF files to `outputs/terminal/`. Open the PNGs and add your prediction and explanation to your downloaded CSV. To keep another run, add `--output outputs/another_run`.

## Finish within 50 minutes

| Workshop clock | What to do |
|---|---|
| 0–10 min | Start your workspace. Run cell 1 and check for **Ready to run the baseline**. If blocked at minute 10, switch to the [saved-run activity](SAVED_RUN.md). |
| 10–20 min | Run cell 2. Compare surface sunlight and infrared radiation with and without the baseline cloud. |
| 20–35 min | In cell 3, write a prediction, change one input (depth, liquid water path or ice water path), and run the cell. |
| 35–43 min | Run cell 4. Use the table to compare the surface and model-top responses. |
| 43–50 min | Write your explanation in cell 5 and run it. Save your notebook. In the file explorer under `outputs/`, right-click `experiment_record.csv` and one experiment PNG and choose **Download**. |

All five cells run in order with **Shift+Enter**. Keep the notebook at the repository root. If you switch kernels, restart from cell 1.
