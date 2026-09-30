"""
Generate paper/tables/*.tex from the CSV outputs produced by the four
Kaggle notebooks (notebooks/01..04). This keeps every number in the paper
traceable to a specific notebook run — no hand-typed results.

Usage (after downloading /kaggle/working from each committed notebook
version into one local folder, merging the tables/ subfolders together):

    python paper/make_tables.py --outputs path/to/downloaded/outputs

Default --outputs is "../outputs" (the local smoke-test run committed
alongside this script). IMPORTANT: the tables shipped in paper/tables/ out
of the box come from a FAST DEBUG configuration (N_TRIALS=3, 1 CV repeat,
3 ablation folds) used only to verify the pipeline runs end-to-end without
errors. They are placeholders. Re-run this script against the full-settings
Kaggle output (N_TRIALS=40, n_repeats=10) before the paper numbers are
final -- see the "PLACEHOLDER" note printed for every table and the
\\PlaceholderNotice box in paper.tex.
"""
import argparse
from pathlib import Path

import pandas as pd


def write_tex(df, path, caption, label, float_fmt="%.3f", escape=True, **kw):
    tex = df.to_latex(float_format=float_fmt, escape=escape, **kw)
    path.write_text(tex, encoding="utf-8")
    print(f"  wrote {path}  ({df.shape[0]}x{df.shape[1]})")


def main(outputs: Path, tables_dir: Path):
    tables_dir.mkdir(parents=True, exist_ok=True)
    print(f"Reading Kaggle notebook outputs from: {outputs}")

    def load(name):
        p = next(outputs.rglob(name), None)
        if p is None:
            print(f"  [skip] {name} not found under {outputs}")
            return None
        return pd.read_csv(p)

    # --- T1: descriptive statistics ------------------------------------
    t1 = load("T1_descriptive.csv")
    if t1 is not None:
        t1 = t1.rename(columns={t1.columns[0]: "Variable"}).set_index("Variable")
        write_tex(t1, tables_dir / "T1_descriptive.tex",
                  "Descriptive statistics of the 110 real blasts used in this study.",
                  "tab:descriptive")

    # --- T2: sites -------------------------------------------------------
    t2 = load("T2_sites.csv")
    if t2 is not None:
        write_tex(t2, tables_dir / "T2_sites.tex",
                  "Mines/quarries represented in the database.", "tab:sites", index=False)

    # --- T4: main benchmark results per protocol -------------------------
    # summarise() in Notebook 02 writes these with a 2-row (metric, mean/std)
    # MultiIndex header and an index named "model" -> read_csv(header=[0,1])
    # recovers that structure; P3_pooled has no std row (pooled OOF metrics).
    for proto, cap, has_std in [("T4_results_P1.csv", "paper-split protocol (P1)", True),
                                 ("T4_results_P2.csv", "repeated grouped 5-fold CV protocol (P2)", True),
                                 ("T4_results_P3_pooled.csv", "leave-one-site-out protocol (P3, pooled OOF)", False)]:
        p = next(outputs.rglob(proto), None)
        if p is None:
            print(f"  [skip] {proto} not found under {outputs}")
            continue
        if has_std:
            raw = pd.read_csv(p, header=[0, 1], index_col=0)
            raw = raw[raw.index.notna()]  # drops the stray "model" header-echo row
            metrics_ = list(dict.fromkeys(raw.columns.get_level_values(0)))
            fmt = pd.DataFrame(index=raw.index)
            for m in metrics_:
                fmt[m] = raw[(m, "mean")].round(3).astype(str) + " $\\pm$ " + raw[(m, "std")].round(3).astype(str)
            fmt.index.name = "Model"
            fmt = fmt.reindex(raw[("RMSE", "mean")].sort_values().index)
        else:
            raw = pd.read_csv(p, index_col=0)
            raw.index.name = "Model"
            fmt = raw.round(3).sort_values("RMSE")
        basis = "mean $\\pm$ std over folds" if has_std else "pooled out-of-fold"
        write_tex(fmt, tables_dir / proto.replace(".csv", ".tex"),
                  f"Benchmark results ({basis}) under the {cap}.",
                  f"tab:{proto[:-4].lower()}", float_fmt="%.3f", escape=False)

    # --- T5: significance --------------------------------------------------
    t5 = load("T5_significance.csv")
    if t5 is not None:
        write_tex(t5, tables_dir / "T5_significance.tex",
                  "Corrected resampled t-test (Nadeau \\& Bengio, 2003) of each model "
                  "against the best model, Holm-corrected p-values, protocol P2.",
                  "tab:significance", index=False)

    # --- T7: vs literature ---------------------------------------------
    t7 = load("T7_vs_literature.csv")
    if t7 is not None:
        t7 = t7.rename(columns={t7.columns[0]: "Model"})
        write_tex(t7.set_index("Model"), tables_dir / "T7_vs_literature.tex",
                  "Comparison with published results on the 12 shared validation blasts.",
                  "tab:vs_literature")

    # --- T6: ablations ----------------------------------------------------
    # written by Notebook 04 with a 2-row (ablation, model) MultiIndex row
    # header and a (metric, mean/std) MultiIndex column header.
    p6 = next(outputs.rglob("T6_ablations.csv"), None)
    if p6 is not None:
        raw = pd.read_csv(p6, header=[0, 1], index_col=[0, 1])
        raw = raw[raw.index.get_level_values(0).notna()]
        metrics_ = list(dict.fromkeys(raw.columns.get_level_values(0)))
        fmt = pd.DataFrame(index=raw.index)
        for m in metrics_:
            fmt[m] = raw[(m, "mean")].round(3).astype(str) + " $\\pm$ " + raw[(m, "std")].round(3).astype(str)
        fmt.index.names = ["Feature set", "Model"]
        write_tex(fmt, tables_dir / "T6_ablations.tex",
                  "Ablation study: effect of feature subsets on benchmark accuracy "
                  "(mean $\\pm$ std, grouped CV).", "tab:ablations", escape=False)
    else:
        print("  [skip] T6_ablations.csv not found under", outputs)

    # --- T8: conformal coverage ---------------------------------------
    t8 = load("T8_conformal_coverage.csv")
    if t8 is not None:
        write_tex(t8, tables_dir / "T8_conformal_coverage.tex",
                  "Empirical coverage and width of 90\\% split-conformal prediction "
                  "intervals under protocols P2 and P3.", "tab:conformal", index=False)

    # --- permutation importance -----------------------------------------
    ti = load("permutation_importance.csv")
    if ti is not None:
        ti = ti.rename(columns={ti.columns[0]: "Feature"})
        write_tex(ti.set_index("Feature"), tables_dir / "T_importance.tex",
                  "Permutation importance (RMSE increase) of each blast parameter, per model.",
                  "tab:importance")

    print("\nDone. \\input{tables/...} these files from paper.tex.")
    print("REMINDER: verify these came from the FULL Kaggle run (N_TRIALS=40, "
          "n_repeats=10), not the fast debug configuration, before submitting.")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--outputs", type=Path,
                     default=Path(__file__).parent.parent / "outputs",
                     help="Folder containing the merged tables/ output of notebooks 01-04 "
                          "(download /kaggle/working from each committed notebook version "
                          "and merge the tables/ subfolders here). The placeholder tables "
                          "shipped in paper/tables/ were built from "
                          "../outputs_placeholder_debug_run (fast debug settings) - point "
                          "this at the FULL run's output before the paper is finalised.")
    ap.add_argument("--tables_dir", type=Path, default=Path(__file__).parent / "tables")
    args = ap.parse_args()
    main(args.outputs, args.tables_dir)
