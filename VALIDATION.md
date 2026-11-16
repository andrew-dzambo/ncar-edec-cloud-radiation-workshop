# Validation of version 1.0

Tested on Linux x86_64 using the included explicit environment lock. These are actual model runs, not illustrative or emulated fluxes.

| Check | Result |
|---|---|
| Fresh environment created from the explicit lock | Passed |
| Setup rerun and source/coefficient checksum verification | Passed |
| Official `pyrte_rrtmgp run_tests` suite | 61 passed |
| Official all-sky example, including clear columns | Passed; maximum flux difference about 5.95 × 10⁻⁶ W m⁻² |
| Independent numerical integration of synthetic profiles | 12 cases passed |
| Invalid depth, mass, and other input rejection | 10 cases passed |
| Zero-cloud, pure-liquid, pure-ice, mixed-phase radiation cases | 5 cases passed |
| Minimum and maximum cloud depths | 50 m and 3000 m passed |
| Minimum in-cloud grid resolution | At least 40 layers |
| Vertically integrated heating versus boundary flux balance | Maximum error 1.43 × 10⁻¹⁴ W m⁻² |
| Participant notebook code | All 7 code cells executed successfully using IPython in one process |
| Quicklook images | Visually inspected for labels, units, legends, and clipping |

The notebook was executed in-process because this build host prohibits Jupyter kernel socket binding (both TCP and local IPC). The real model, installation, imports, plots, CSV/NetCDF exports, and all code cells ran successfully. **A live Jupyter browser/kernel connection and the Windows/macOS SSH tunnel have not been tested on the teaching server.** The instructor must preflight that site-specific path, including any queue, account, and firewall requirements.

`examples/RRTMGP_Cloud_Workshop_reference.ipynb` and `.html` contain captured real results for viewing. Run the clean notebook at the package root for participants' work. The HTML embeds figures; equation rendering may require access to its MathJax CDN. Sample output files are in `examples/outputs/`.

Warm paired clear/all-sky calculations took about 0.3 seconds here, excluding plotting and initial table loading. This is a measurement on this host, not a class-time or server-performance guarantee. First-time installation and access setup belong in prework.

Recheck the science with:

```bash
envs/rrtmgp/bin/python scripts/validate_workshop.py --output validation.json
```

Optionally rerun the complete official suite before class (not during the timed lesson):

```bash
envs/rrtmgp/bin/pyrte_rrtmgp run_tests
```

Machine-readable numerical details are in `validation.json`; source pins and coefficient hashes are in `provenance.json`. These checks establish implementation consistency, not observational validation or realistic microphysics for every user-selected cloud.
