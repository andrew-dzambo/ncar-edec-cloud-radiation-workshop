# Facilitator guide for personal workspaces

Project the repository home page or the [activity slide (PNG)](presentation/Workshop_activity_slide.png) and paste the [personal Codespace launch link](https://codespaces.new/andrew-dzambo/ncar-edec-cloud-radiation-workshop/tree/main?quickstart=1) and [participant guide](GETTING_STARTED.md) into the online chat. Participants with their own x86_64 Linux may choose route B. Everyone works in their own copy and keeps their own outputs.

**Start the clock as people arrive.** Invite participants to start the installer at minute 0, then use the science slides while the downloads run. GitHub runs the setup automatically when it creates a new codespace. Existing shared installations can still use the legacy configuration script, but the public workshop uses personal workspaces.

| Time | Facilitation |
|---|---|
| 0–10 | Start personal Linux sessions, select the kernel and run cell 1. Cold starts depend on downloads and account availability. If the kernel picker stalls after installation, point participants to the live terminal command in the guide. At minute 10 send anyone still waiting to [the saved-run activity](SAVED_RUN.md). |
| 10–20 | Compare baseline sunlight and infrared fluxes. |
| 20–35 | Ask for a prediction, then change one input. |
| 35–43 | Compare cloud radiative effects at the surface and model top. |
| 43–50 | Save the CSV and PNG. Ask for one change and its physical explanation. Stop Codespaces after downloading. |

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

