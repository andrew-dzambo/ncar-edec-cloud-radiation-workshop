# Facilitator guide

## Delivery model

The full participant experience lasts **50 minutes**, including startup. Participants have no assigned preparation. Provide a prepared institutional **JupyterHub/Open OnDemand** service on Linux x86_64 and aim to have each participant running by minute 10. Windows and Mac laptops use the same browser workflow.

Server deployment is the facilitator's responsibility and is separate from the participant activity. The ten-minute startup window is a rehearsal target, not a promise that new accounts, a cold installation, or an arbitrary server can be made ready in that time. Nothing in this repository confirms that your institutional service has already been configured.

## What the facilitator supplies

| Item | Required at the start |
|---|---|
| Jupyter URL | A working institutional JupyterHub/Open OnDemand entry point |
| Access | Institutional or guest credentials that work onsite; a tested route through any VPN or authentication requirements |
| Session choice | Exact server/profile selection, with capacity available for 20–30 participants |
| Shared directory | The absolute path to the prepared workshop checkout, containing its environment and coefficients |
| Personal workspace | A writable home/work directory for each participant's notebook and output files |
| Fallback | A verified notebook template and sample results available without another download |

Replace `/SHARED/WORKSHOP_DIR` in the projected startup command with your actual path. Do not leave participants to infer server names, queues, accounts, or directory locations.

## Deploy once on the server

The standalone installer is for the facilitator or server administrator. On the chosen Linux x86_64 host (glibc >=2.28), create the shared installation at its final location:

```bash
git clone https://github.com/andrew-dzambo/ncar-edec-cloud-radiation-workshop.git /SHARED/WORKSHOP_DIR
cd /SHARED/WORKSHOP_DIR
bash setup_workshop.sh
```

Substitute an actual writable deployment path before running these commands. The installer downloads the pinned runtime, sources, and coefficient data. Allow at least 4 GB disk space including caches. Keep the resulting environment at that path; conda environments can contain absolute paths.

Ensure ordinary participants can read and traverse the shared environment and coefficient directories. They should write only to their own workshop copies. Verify that `configure_workshop.sh /SHARED/WORKSHOP_DIR` can register **Python (RRTMGP Workshop)** for an ordinary account and that the institutional Jupyter service discovers that user kernel. Each participant's configuration points to the shared runtime and data; no participant package download or solve is needed.

Run the scientific checks in the shared installation:

```bash
envs/rrtmgp/bin/python scripts/validate_workshop.py --output validation.json
envs/rrtmgp/bin/pyrte_rrtmgp run_tests
```

## Rehearse the actual startup

Use a fresh ordinary participant account, not an administrator shell. Start the clock at the login page and follow [GETTING_STARTED.md](GETTING_STARTED.md) through the first model run. Verify browser access on the event network, Git availability, the small repository download, shared-directory permissions, kernel discovery, and downloading the final PNG/CSV.

Reserve enough sessions for all 20–30 participants and test representative concurrent demand. Numerical libraries are limited to one thread per process. Begin capacity planning with one CPU and 4 GB RAM per participant session, then measure on the actual service. Check queue/startup delays with the administrator. Download large packages and coefficients once during deployment, not 30 times during the activity.

Keep a verified, writable-copy template available on the service. If GitHub access fails, distribute a personal copy of that template. If an individual is still blocked at minute 10, pair them with a working participant. If the service fails broadly, use the supplied reference plots for discussion and label them as supplied runs; do not imply participants have executed their own experiments.

## Facilitation plan

| Minutes | Participant action | Facilitator focus |
|---|---|---|
| 0–2 | Sign in | Display URL, credentials route, and session choice |
| 2–5 | Clone and configure | Supply the exact shared-directory command |
| 5–8 | Open notebook and kernel | Resolve kernel-selection problems |
| 8–10 | Check readiness; begin baseline | Apply the minute-10 fallback |
| 10–20 | Interpret baseline fluxes | Distinguish sunlight, thermal radiation, and flux direction |
| 20–35 | Build a cloud and check mass | Change one parameter and predict its effect |
| 35–43 | Compare radiation | Explain surface versus model-top changes |
| 43–50 | Download PNG/CSV; discuss | Ask for a change, a mechanism, and a limitation |

Use 5–6 discussion groups while participants work in their own sessions. Keep the editable cloud-parameter cell on screen. Long explanations are optional in [SCIENCE_NOTES.md](SCIENCE_NOTES.md); the notebook should drive the activity.

## Experiment assignments

| Group | Change only this | Prediction to test |
|---|---|---|
| A | LWP: 100 → 200 g m⁻² | How does extra liquid affect surface sunlight? |
| B | IWP: 30 → 100 g m⁻² | How does more ice change reflected SW and outgoing LW? |
| C | Depth: 1000 → 2000 m at fixed paths | How can radiation change when total mass does not? |
| D | LWP → 0, keep IWP | Which phase dominates this mixed-phase example? |
| E | Both paths → 0 | Do clear and all-sky fluxes become identical? |
| F | Depth: 1000 → 50 or 3000 m at fixed paths | How does spreading the same mass change water content? |

Keep other settings fixed. Responses depend on sunlight, surface reflectivity, temperature, particle sizes, and phase; do not promise universally monotonic effects. Clouds are imposed optical experiments with no microphysical evolution or temperature adjustment. All sky means a fully cloudy single column, not a fractional-cloud average. Positive net-down CRE at a boundary is not by itself atmospheric heating.

## Optional GitHub follow-up

GitHub authentication, forking, and uploading are not required to finish the timed activity. Afterwards, participants can fork [the repository](https://github.com/andrew-dzambo/ncar-edec-cloud-radiation-workshop), choose **Add file → Upload files** in their fork, and upload the saved CSV and one PNG. Keep environments and coefficient downloads out of Git.

Andrew can request future updates from ChatGPT Work using this repository's URL and a description of the change. Participants do not need to connect GitHub to ChatGPT.

## Alternative deployment: SSH instead of JupyterHub

Use this route only if the facilitator has tested it and can deliver it within the startup target. It adds terminal/tunnel steps, so a prepared browser service is preferred. Give participants exact commands with real host names, usernames, ports, and the shared-directory path.

On a permitted interactive Linux session, obtain a personal working copy, configure it, and launch Jupyter:

```bash
git clone https://github.com/andrew-dzambo/ncar-edec-cloud-radiation-workshop.git
cd ncar-edec-cloud-radiation-workshop
bash configure_workshop.sh /SHARED/WORKSHOP_DIR
bash launch_workshop.sh 8888
```

In a second laptop terminal (Windows PowerShell or macOS Terminal), forward the port:

```text
ssh -N -L 8888:127.0.0.1:8888 LINUX_USER@LINUX_HOST
```

Open the token-bearing localhost URL printed by Jupyter. Keep both sessions running. Assign distinct remote ports on a shared host and match each port in the launcher and tunnel commands.

On a scheduled cluster, arrange the interactive allocation and institution-approved connection route beforehand. If Jupyter runs on a compute node, a tunnel to the login node's loopback will not reach it. Where compute-node SSH via a login host is permitted, the laptop tunnel can use:

```text
ssh -N -J LINUX_USER@LOGIN_HOST -L 8888:127.0.0.1:8888 LINUX_USER@COMPUTE_HOST
```

Use the site's documented route if this is not permitted. Do not use workshop time to discover scheduler or firewall requirements. The scientific verification results and live-server testing limits are recorded in [VALIDATION.md](VALIDATION.md).
