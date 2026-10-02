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

## Workflow (GitHub-synced — current)

The repo is [mobashshir-ubn-zainuddin/Rock-fragmentation-analysis-post-blasting](https://github.com/mobashshir-ubn-zainuddin/Rock-fragmentation-analysis-post-blasting),
already holding `data/`. Each notebook now opens with a **Setup — sync with
the GitHub repository** cell that clones/pulls this repo into
`/kaggle/working/repo` and writes every output under `repo/outputs/`, then
closes with a **Push results to GitHub** cell. This removes the manual
"create a second Kaggle Dataset" step: Notebook 02 pushes its benchmark
tables, Notebook 03 pulls them automatically (via `sync_repo()`) and pushes
its models/SHAP tables, Notebook 04 pulls both and pushes its own results.

One-time setup per Kaggle notebook:
1. Create a GitHub **fine-grained personal access token** scoped only to
   this repo, with **Contents: Read and write**.
2. On Kaggle: *Add-ons → Secrets* → add it as `GITHUB_TOKEN`, and attach
   that secret to each of the four notebooks.
3. Session options → **Internet: on**, Persistence → *Variables and Files*
   (already set — this is what keeps `/kaggle/working/repo` around between
   runs of the *same* notebook; the GitHub push/pull is what shares results
   *across* the four different notebooks).

Then, in order:
1. Run `notebooks/01_eda.ipynb` (data comes from the attached `blasting`
   Kaggle Dataset, or straight from the repo if you only attach the repo).
2. Run `notebooks/02_baselines_and_ml_benchmark.ipynb` at **full settings**
   (`N_TRIALS=40`, `n_repeats=10` — already the default; the earlier debug
   run used 3/1 only to verify no errors). It checkpoints a push after each
   of P1/P2/P3, so an interrupted session doesn't lose completed work.
3. Run `notebooks/03_interpretability.ipynb`, then
   `notebooks/04_uncertainty_ablations.ipynb` — both auto-pull the prior
   notebooks' pushed outputs at the top.
4. Locally: `git pull` this repo (now containing the real `outputs/` from
   Kaggle), then `python paper/make_tables.py --outputs outputs` to
   regenerate `paper/tables/*.tex` from the real results.
5. Copy the real figures into `paper/figures/`, delete the
   `\PlaceholderNotice` box in `paper.tex`, fill in the Discussion/
   Conclusion placeholders, and compile (Overleaf, IEEEtran built in).

**Security note:** `GITHUB_TOKEN` is read fresh from Kaggle Secrets for
every git command and passed only as a one-off `-c http.extraheader=...`,
never written into `.git/config` or any file under `/kaggle/working` — so
it cannot leak even if a notebook's output is later made public. Keep the
token scoped to this one repo only.

See `IMPLEMENTATION_PLAN.txt` for the full research design, literature
baseline, and evaluation rationale.
