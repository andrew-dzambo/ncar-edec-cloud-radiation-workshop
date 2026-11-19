# If setup is still running at minute 10

These are **saved RRTMGP calculations** from the same workshop notebook. You can complete this comparison directly on GitHub while your own installation finishes. Switch back to the notebook for a live experiment as soon as it is ready.

1. **Predict.** A cloud is 1,000 m deep and contains 100 g/m² of liquid water and 30 g/m² of ice. What happens to sunlight reaching the surface if you double the liquid water and keep everything else fixed? Write down your prediction.
2. **Read the baseline.** Open the [baseline flux plot](examples/outputs/baseline_fluxes.png) and the [surface and model-top values](examples/outputs/baseline_boundary_summary.csv). Compare clear and all-sky **surface SW** net flux. Net flux means downward minus upward.
3. **Follow the change.** Open the [edited cloud profile](examples/outputs/experiment01_profiles.png) and [edited flux plot](examples/outputs/experiment01_fluxes.png). Locate the liquid and ice maxima. Which part of the spectrum changes most when LWP rises to 200 g/m²?
4. **Quantify it.** In the [experiment CSV](examples/outputs/experiment_record.csv), find the **Surface / SW** row and read **Change in CRE (W/m²)**. Is the change positive or negative? Compare it with the Surface / LW row. CRE means all-sky minus clear-sky net flux.
5. **Save by minute 50.** Download the experiment CSV and one PNG with GitHub's **Download raw file** button. Record one sentence in your copy: “Using the supplied runs, doubling LWP changed surface SW CRE by ___ W/m² because ___.” Describe one assumption, such as fixed particle size. If you ran your own notebook instead, save the files it created under `outputs/`.
