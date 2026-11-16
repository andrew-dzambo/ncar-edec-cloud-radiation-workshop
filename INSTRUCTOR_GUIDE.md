# Instructor guide

## Prepare the class

The 50 minutes are **learning and experiments after prework**, not a guarantee that 30 first-time account setups and network installations finish inside class. Send [GETTING_STARTED.md](GETTING_STARTED.md) several days ahead. Ask everyone to arrive with a GitHub account, a fork of the workshop, tested Linux access, and Jupyter open in the correct kernel.

1. Share the [workshop repository](https://github.com/andrew-dzambo/ncar-edec-cloud-radiation-workshop) and [participant setup guide](GETTING_STARTED.md). Ask participants to fork it under their own accounts. Keep downloaded model sources, coefficient caches, and environments out of Git.
2. Test installation and a complete notebook run on the actual teaching server under an ordinary participant account. Confirm outbound access to GitHub and conda-forge, sufficient disk space, and site-specific Jupyter/scheduler instructions.
3. Plan for 20–30 separate participant working directories. Keep the numerical libraries at one thread per process. Reserve capacity with the administrator; start by allowing 1 CPU and 4 GB per participant allocation and measure actual requirements on that server.
4. Avoid 30 simultaneous downloads. The explicit lock avoids repeated dependency solving; stagger prework. The supplied workflow uses a separate `envs/rrtmgp` in each participant's workshop folder. An administrator can design a shared installation, but must adapt the notebook's environment-path check and setup call and test permissions first. It is not a switch built into this package. Do not copy a built conda environment to a new path because its paths can be embedded. Allow at least 4 GB disk per default installation, including caches.
5. Allocate unique Jupyter ports, or preferably use a managed JupyterHub/Open OnDemand service. On a cluster, ensure interactive jobs can start before class; queue time is outside the lesson.
6. Open the packaged sample quicklooks/reference notebook as a fallback for discussing results if participants lose network access. Label these as supplied reference runs; they do not replace running participants' own experiments.

## Facilitation plan (50 minutes)

| Time | Instructor action | Participant product |
|---|---|---|
| 0–5 min | Ask which flux a cloud changes first; distinguish sunlight from thermal radiation | One prediction |
| 5–10 min | Explain gas optics, transport, and coefficient tables; run verification | Working engine and version record |
| 10–20 min | Guide baseline SW/LW plots and upward/downward directions | Surface versus top-of-atmosphere comparison |
| 20–30 min | Explain path versus content; point to liquid/ice peak heights | A mass-conserving synthetic cloud |
| 30–42 min | Assign each table one experiment below | Baseline/experiment comparison |
| 42–47 min | Ask for a sign, a mechanism, and a limitation | Three-sentence interpretation |
| 47–50 min | Demonstrate browser upload to a fork | Saved CSV plus one figure |

With 20–30 participants, use 5–6 discussion groups while each person runs their own notebook. Keep the editable parameter cell on screen. Avoid making a full Fortran compile, an upstream test suite, or Git command-line authentication part of the timed activity.

## Experiment assignments

| Group | Change only this | Prediction to test |
|---|---|---|
| A | LWP: 100 → 200 g m⁻² | How does extra liquid affect downward surface SW? |
| B | IWP: 30 → 100 g m⁻² | How does more ice change reflected SW and outgoing LW? |
| C | Depth: 1000 → 2000 m at fixed paths | How can radiation change when total mass does not? |
| D | LWP → 0, keep IWP | Which phase dominates this particular mixed-phase example? |
| E | Both paths → 0 | Do clear and all-sky results become identical? |
| F (optional) | Depth: 1000 → 50 m or 1000 → 3000 m at fixed paths | How strongly does content change as the same mass is spread out? |

Use the notebook's supplied baseline parameters for all other settings. Default radius and ice size are held fixed. Do not promise that every effect is monotonic or universal: the answer depends on sunlight, surface reflectivity, temperature, particle sizes, and phase. At fixed paths, depth changes the vertical placement of mass and its temperature, not simply total cloud amount. Very thin/high-mass clouds can be unrealistic; treat them as imposed optical experiments.

## What to emphasize

- **Engine versus input:** RRTMGP maps gases to optical properties; RTE calculates fluxes. We prescribe clouds and use separate lookup tables.
- **Path versus content:** `g m^-2` is column mass; `g m^-3` is local concentration. At fixed path, doubling depth halves the vertically averaged content.
- **All-sky meaning:** one fully cloudy column, not fractional cloud cover or a satellite footprint average.
- **Instantaneous response:** clear and cloudy runs use the same thermodynamic state. The atmosphere has not warmed, cooled, condensed, or precipitated in response.
- **Surface versus TOA:** positive net-down CRE at the surface increases radiative energy entering the surface. Positive TOA CRE increases energy entering the combined atmosphere/surface. Neither alone equals atmospheric heating.
- **Verification versus validation:** matching a supplied reference tests implementation. It does not quantify uncertainty for an arbitrary invented cloud.
- **Paper versus workshop:** beta cloud shapes, idealized atmosphere, and selected particle sizes are our pedagogical choices. Pincus et al. explain the computational framework and its tradeoffs.

## Maintaining this repository from ChatGPT Work

The workshop repository is [andrew-dzambo/ncar-edec-cloud-radiation-workshop](https://github.com/andrew-dzambo/ncar-edec-cloud-radiation-workshop). Andrew's GitHub account is connected to the Work conversation used to prepare and upload this activity.

For future changes, provide that repository URL in Work and describe the requested update. For example: `Update the workshop instructions in https://github.com/andrew-dzambo/ncar-edec-cloud-radiation-workshop on a new branch and open a pull request.` A pull request presents the proposed changes for review before they are merged into the main branch.

If the connection cannot access this repository, review the GitHub integration's repository access and include `ncar-edec-cloud-radiation-workshop`. Repository permissions determine which read and write actions are available. No password or access token needs to be pasted into chat.

Participants only need their own GitHub accounts for forking and saving results; they do not need to connect GitHub to ChatGPT. Their upload procedure is in [GETTING_STARTED.md](GETTING_STARTED.md#5-save-and-share-your-result).

Official references:

- [ChatGPT plugins](https://learn.chatgpt.com/docs/plugins)
- [GitHub application repository access](https://docs.github.com/en/apps/using-github-apps/reviewing-and-modifying-installed-github-apps)
- [Uploading files to a repository](https://docs.github.com/en/repositories/working-with-files/managing-files/adding-a-file-to-a-repository)

## Teaching notes on the paper

Pincus et al. (2019), https://doi.org/10.1029/2019MS001621:

- Sections 2.2–2.4, pp. 3077–3079: optical properties, source terms, transport, and assembling a radiation calculation.
- Sections 2.3 and 3.1, pp. 3078 and 3080–3081: correlated-k treatment and spectral sampling.
- Introduction, pp. 3074–3076: independent-column approximation and the role of parameterization.
- Section 4, pp. 3086–3087: host-model responsibility for clouds and aerosols and choices in the balance of flexibility, efficiency, and accuracy.

The notebook paraphrases these ideas. It does not claim that the paper recommends the synthetic liquid/ice profiles or supplies an uncertainty bound for these cloudy cases.
