# Rock Fragmentation Prediction from Blast Parameters

Conference-paper project: predicting mean blast fragment size (X50) from
blast-design, explosive and rock-property parameters using ML, benchmarked
against the Kuznetsov/Kuz-Ram and MVR models. **All experiments run on
Kaggle. All data are real field measurements — no synthetic data is used
for training or testing.**

## Layout
```
data/
  raw/hudaverdi2010_local_90.csv           90 blasts, from the user's original files
  raw/external/                             GitHub transcription of the full 110-blast DB
  processed/blast_master_110.csv            <- upload this to Kaggle as a Dataset
  DATA_NOTES.txt                            full provenance + 2 corrected values

notebooks/                                  run in order, on Kaggle
  01_eda.ipynb                              Phase 1: exploratory data analysis
  02_baselines_and_ml_benchmark.ipynb       Phases 2-5: protocols, baselines, ML, stats
  03_interpretability.ipynb                 Phase 6: SHAP, permutation importance, PDP
  04_uncertainty_ablations.ipynb            Phases 7-8: conformal intervals, design tool,
                                             ablations

paper/
  paper.tex, references.bib                 IEEEtran conference paper (compiles on Overleaf)
  make_tables.py                            regenerates paper/tables/*.tex from Kaggle CSV
                                             output — no hand-typed numbers
  tables/, figures/                         auto-generated LaTeX tables + copied PNGs

outputs_placeholder_debug_run/              fast-debug run used only to verify the
                                             pipeline runs end to end (NOT final results)

IMPLEMENTATION_PLAN.txt                     the original detailed step-by-step plan
```

## Workflow
1. Upload `data/processed/blast_master_110.csv` + `data/DATA_NOTES.txt` as a
   Kaggle Dataset.
2. Run `notebooks/01_eda.ipynb` on Kaggle (Add Input -> your dataset).
3. Run `notebooks/02_baselines_and_ml_benchmark.ipynb` at **full settings**
   (`N_TRIALS=40`, `n_repeats=10` — already the default in the notebook;
   the debug run used 3/1 only to verify no errors). Commit the version,
   then create a second Kaggle Dataset from `/kaggle/working` (e.g.
   `rock-blast-benchmark-outputs`).
4. Run `notebooks/03_interpretability.ipynb` and
   `notebooks/04_uncertainty_ablations.ipynb`, both with the benchmark
   dataset added as a second input.
5. Download all four notebooks' `/kaggle/working` folders, merge their
   `tables/` subfolders into one local `outputs/` directory.
6. `python paper/make_tables.py --outputs outputs` to regenerate
   `paper/tables/*.tex` from the real results.
7. Copy the real figures into `paper/figures/`, delete the
   `\PlaceholderNotice` box in `paper.tex`, fill in the Discussion/
   Conclusion placeholders, and compile (Overleaf, IEEEtran built in).

See `IMPLEMENTATION_PLAN.txt` for the full research design, literature
baseline, and evaluation rationale.
