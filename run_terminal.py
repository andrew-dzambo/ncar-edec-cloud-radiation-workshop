"""Run the live workshop experiment on personal Linux without a Jupyter server."""
import argparse
import os
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--depth", type=float, default=1000, help="Cloud depth in m (50–3000)")
    parser.add_argument("--lwp", type=float, default=200, help="Liquid water path in g/m²")
    parser.add_argument("--iwp", type=float, default=30, help="Ice water path in g/m²")
    parser.add_argument("--output", type=Path, default=Path("outputs/terminal"),
                        help="Output directory for this experiment")
    args = parser.parse_args()
    os.environ["MPLBACKEND"] = "Agg"
    from scripts.workshop_runtime import prepare_notebook
    prepare_notebook(Path(__file__).resolve().parent)
    from workshop_model import build_column, run_column, save_case, boundary_summary

    # Validate the participant's inputs before running either radiation calculation.
    experiment_column = build_column(depth_m=args.depth, lwp_gm2=args.lwp, iwp_gm2=args.iwp)
    baseline = run_column(build_column(depth_m=1000, lwp_gm2=100, iwp_gm2=30))
    experiment = run_column(experiment_column)
    save_case(baseline, args.output, "baseline")
    save_case(experiment, args.output, "experiment")
    paired = {}
    for label, result in [("Baseline", baseline), ("Experiment", experiment)]:
        paired[label] = boundary_summary(result).set_index(["Boundary", "Band"])["CRE (W/m²)"]
    record = paired["Baseline"].to_frame("Baseline CRE (W/m²)")
    record["Experiment CRE (W/m²)"] = paired["Experiment"]
    record["Change in CRE (W/m²)"] = paired["Experiment"] - paired["Baseline"]
    print(record.round(2).to_string())
    record["depth_m"] = args.depth
    record["lwp_g_m2"] = args.lwp
    record["iwp_g_m2"] = args.iwp
    record.to_csv(args.output / "experiment_record.csv")
    print(f"Your comparison CSV, plots, and NetCDF files are in {args.output.resolve()}.")


if __name__ == "__main__":
    main()
