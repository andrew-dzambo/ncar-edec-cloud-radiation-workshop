# Before class: Windows or Mac laptop, Linux model

Your GitHub account stores your work. Your Linux account runs the model. They are different accounts; a GitHub account does not give you Linux access. Ask the workshop organizer for your Linux username, host name, and any VPN or scheduler instructions before class.

## 1. Make your copy on GitHub

Sign in to GitHub. Open [andrew-dzambo/ncar-edec-cloud-radiation-workshop](https://github.com/andrew-dzambo/ncar-edec-cloud-radiation-workshop) and choose **Fork → Create fork**. Copy the HTTPS URL from your fork's **Code** menu. Fork the small workshop repository, not the much larger model/data repositories: the installer downloads those automatically.

Public source downloads do not require authentication. Your account is used to keep your experiment record. You can upload that record through GitHub's browser interface without setting up SSH keys or a command-line token during class.

## 2. Download the workshop

The simplest path is to clone directly **on the Linux server**. Open **PowerShell** on Windows 10/11 or **Terminal** on macOS; both can use these SSH commands. Replace `LINUX_USER`, `LINUX_HOST`, and `YOUR_GITHUB_NAME` with your real values. If Windows does not recognize `ssh`, enable the Windows OpenSSH Client optional feature or use your institution's SSH client.

```text
ssh LINUX_USER@LINUX_HOST
```

Then, in that Linux terminal:

```bash
git clone https://github.com/YOUR_GITHUB_NAME/ncar-edec-cloud-radiation-workshop.git
cd ncar-edec-cloud-radiation-workshop
bash setup_workshop.sh
```

`YOUR_GITHUB_NAME` is your GitHub username; the repository name is `ncar-edec-cloud-radiation-workshop`. Use the actual URL from your fork if you renamed it. If Git is unavailable, ask the organizer to provide it or use the ZIP route below.

**ZIP route (works on both laptop operating systems):** open the [workshop repository](https://github.com/andrew-dzambo/ncar-edec-cloud-radiation-workshop) and select **Code → Download ZIP**. The `main` branch downloads as `ncar-edec-cloud-radiation-workshop-main.zip`. In your laptop terminal, change into Downloads and copy it:

```text
scp ncar-edec-cloud-radiation-workshop-main.zip LINUX_USER@LINUX_HOST:~/
```

On Linux, extract and install:

```bash
unzip ncar-edec-cloud-radiation-workshop-main.zip
cd ncar-edec-cloud-radiation-workshop-main
bash setup_workshop.sh
```

If you download another branch, rename your fork, or receive the original `RRTMGP_Cloud_Workshop_v1.0.zip` from the instructor, substitute that ZIP's actual filename and extracted folder name. Downloading and copying the ZIP is cross-platform; the shell installer runs on Linux. An Apple Silicon laptop is fine because the computation happens remotely on x86_64 Linux.

## 3. Launch Jupyter on the server

For a teaching server where interactive work is allowed, remain inside the workshop folder and use the supplied launcher (it limits numerical threads and uses the correct Python environment):

```bash
bash launch_workshop.sh 8888
```

Keep that terminal running. Open a **second laptop terminal** and forward the port:

```text
ssh -N -L 8888:127.0.0.1:8888 LINUX_USER@LINUX_HOST
```

Open the token-bearing `http://127.0.0.1:8888/lab?token=...` URL printed by Jupyter in your laptop browser. Keep the token private. The tunnel terminal may appear idle; that is normal. If port 8888 is occupied, choose another port, for example 8892, in both commands and the browser URL. On a shared server, each participant needs an available remote port; the organizer can assign ports 8901–8930 in advance.

Open [RRTMGP_Cloud_Workshop.ipynb](RRTMGP_Cloud_Workshop.ipynb) in Jupyter and select **Python (RRTMGP Workshop)** when offered. If another kernel is selected, the first cells explain how to switch. Run cells in order with **Shift+Enter**. Do not start the activity by opening the `.ipynb` in the GitHub webpage: GitHub displays notebooks but does not execute them.

## 4. OSCER-style cluster alternative

Use your center's approved JupyterHub/Open OnDemand service if available. On a scheduled cluster, installs may be allowed on a login node but calculations/Jupyter may require an interactive compute allocation. Follow local policy. No partition, account, queue, or hostname is guessed in this package.

An illustrative SLURM request is:

```bash
salloc --time=01:30:00 --cpus-per-task=1 --mem=4G
srun --pty bash
hostname
```

Your center may require `--partition` and `--account`. In the allocated compute shell, change into the workshop folder and run the Jupyter command above. With SSH access to compute nodes via the login host, this laptop command forwards directly to the compute node's loopback interface:

```text
ssh -N -J LINUX_USER@LOGIN_HOST -L 8888:127.0.0.1:8888 LINUX_USER@COMPUTE_HOST
```

Replace `COMPUTE_HOST` with the hostname reported inside your allocation. Not every center permits this SSH path; use the center's documented tunnel/Open OnDemand route when it does not. Forwarding only to the login node's loopback will not reach Jupyter running on a compute node. Keep the allocation alive for the workshop. The organizer must test this path before class.

## 5. Save and share your result

Save the notebook. In Jupyter's file browser download `outputs/experiment_record.csv` and one experiment PNG. Open your own GitHub fork, choose **Add file → Upload files**, upload the small files, and commit with a descriptive message such as `Test doubled liquid water path`. Uploading through the browser works on both laptop operating systems. Keep generated model environments and coefficient downloads out of the repository.

## Troubleshooting

| Symptom | Action |
|---|---|
| `ModuleNotFoundError: pyrte_rrtmgp` | Run setup on Linux and select the workshop kernel; check the notebook's printed Python path. |
| Kernel not listed | Restart Jupyter after setup, or launch `envs/rrtmgp/bin/jupyter lab` from the installed folder. |
| Package or GitHub download fails | Check server outbound access/proxy with the organizer; first-time offline installation is not supported. |
| Browser cannot connect | Keep both server and tunnel sessions running; match host and ports; check VPN and allocation. |
| `Address already in use` | Choose an unused port in both Jupyter and the SSH tunnel. |
| Setup rejects platform | Run it on x86_64 Linux, not macOS or native Windows; the laptop is the client. |
| Environment/kernel fails after moving folder | Keep the installed folder at its original path, or ask the organizer to recreate the environment at the final path; conda environments and kernels contain absolute paths. |
| Widget is unavailable | The activity uses editable Python parameter cells; no widget extension is required. |

Useful official references: [GitHub forks](https://docs.github.com/en/pull-requests/how-tos/work-with-forks/fork-a-repo), [uploading files](https://docs.github.com/en/repositories/working-with-files/managing-files/adding-a-file-to-a-repository), and [Jupyter security](https://jupyter-server.readthedocs.io/en/latest/operators/security.html).
