# Validation of the 50-minute workshop revision (v1.1)

The revised route uses a facilitator-prepared Linux runtime. Participants configure a personal working copy and select its kernel during minutes 0–10; they do not install packages or download model coefficients. All required participant work, including saving results, is scheduled within 50 minutes.

## Checks for this revision

| Check | Result |
|---|---|
| Prepared runtime from the explicit environment lock | Python 3.11, pyRTE-RRTMGP 0.2.5, compiled RTE+RRTMGP 1.9.2 |
| Separate participant copy using the shared runtime | Passed; no participant environment or coefficient directory created |
| Short notebook | All 5 code cells executed successfully with IPython in one process |
| Shared configuration and launcher | Repeated setup, paths containing spaces, missing-data/wrong-kernel messages, and read-only shared-tree behavior passed |
| Local Jupyter HTTP service | Launcher served a participant file successfully (authenticated HTTP 200) |
| Real model calculations | Baseline and edited-cloud clear/all-sky pairs completed |
| Result exports | NetCDF, PNG, and CSV files created in the participant's own directory |
| Synthetic cloud checks | 12 independent profile integrations and 10 invalid-input checks passed |
| Radiation checks | Five cases passed, including zero-cloud identity and 50/3000 m depth cases |
| Official all-sky reference, including clear columns | Passed; maximum flux difference about 5.95 × 10⁻⁶ W m⁻² |
| Vertically integrated heating versus boundary flux balance | Maximum error below 1.5 × 10⁻¹⁴ W m⁻² |

On this build host, the participant configuration command took **2.66 seconds**, and the notebook readiness cell took **0.88 seconds**. These measurements cover automated steps only. They exclude browser sign-in, repository download, human interaction, network congestion, and scheduler delays. They support removing installation from the participant route; they do not prove that a particular event service will start 30 sessions within ten minutes.

**The facilitator must rehearse the complete login-to-first-result route on the actual service with an ordinary participant account.** Test kernel discovery, shared-directory access, concurrent capacity, and PNG/CSV download. A live JupyterHub/Open OnDemand/browser connection and Windows/macOS SSH tunnel have not been tested on the teaching server. The local Jupyter HTTP server worked, but a separate kernel execution attempt failed before the first cell because this build host denied a ZeroMQ network-interface operation (`Operation not permitted`). Therefore all notebook cells were verified through IPython in-process; live kernel execution still needs verification on the event server. See [INSTRUCTOR_GUIDE.md](INSTRUCTOR_GUIDE.md) for deployment and the minute-10 fallback.

## Results and provenance

`startup_validation.json` records this revision's participant-copy execution and timing scope. `validation.json` records the scientific checks. `provenance.json` records model/data pins and coefficient hashes. The same radiation engine passed all 61 upstream Python tests during the initial v1.0 build; that result is retained as historical engine validation, not represented as a new live-server test.

[The completed reference notebook](examples/RRTMGP_Cloud_Workshop_reference.ipynb) and its HTML counterpart contain the new five-cell route with actual model results. Run the clean notebook at the repository root for your own experiment. The HTML embeds the figures; optional equation rendering can require its MathJax CDN. Sample output files remain in `examples/outputs/`.

## Facilitator-only verification commands

Run these from the prepared shared checkout during deployment or rehearsal, not as participant tasks:

```bash
envs/rrtmgp/bin/python scripts/validate_workshop.py --output validation.json
envs/rrtmgp/bin/pyrte_rrtmgp run_tests
```

These checks establish implementation consistency, not observational validation or realistic microphysics for every user-selected cloud. No participant preparation is assigned outside the workshop.
