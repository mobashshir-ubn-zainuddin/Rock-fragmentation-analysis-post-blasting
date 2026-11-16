# Machine Learning-Based Prediction of Rock Fragmentation from Blast Design Parameters

A leakage-aware ML benchmark for predicting mean blast fragment size (X₅₀) from blast-design, explosive, and rock-property parameters, evaluated against the Kuznetsov / Kuz-Ram empirical models. All experiments use real field measurements — no synthetic training data.

> **Paper:** "Machine Learning-Based Prediction of Rock Fragmentation from Blast Design Parameters: A Leakage-Aware Benchmark on a Multi-Mine Database" — IEEEtran conference format, compiled at `paper/paper.pdf`.

---

## Dataset

- **110 bench blasts** from **10 mines and quarries** across 5 countries (Spain, Turkey, Indonesia, India, USA)
- Compiled from Hudaverdi et al. (2011) and Kulatilake et al. (2010)
- **7 input features:** S/B, H/B, B/D, T/B, powder factor (Pf), in-situ block size (X_B), elastic modulus (E)
- **Target:** mean fragment size X₅₀ (m)

---

## Models Benchmarked

| Type | Models |
|---|---|
| Empirical | Kuznetsov equation, Kuz-Ram |
| Linear | Multivariate Regression (MVR), Ridge |
| Kernel | Support Vector Regression (SVR), Gaussian Process (GPR) |
| Ensemble | Random Forest, Extra Trees, XGBoost, LightGBM, CatBoost |
| Neural | Artificial Neural Network (ANN) |

---

## Evaluation Protocols

| Protocol | Description |
|---|---|
| **P1** | Original paper split (90 train / 12 test, single run) |
| **P2** | Repeated duplicate-aware grouped k-fold CV (10×5 folds) |
| **P3** | Leave-one-site-out (LOSO) — generalization to unseen mines |

Statistical significance: corrected resampled t-test (Nadeau & Bengio 2003) with Holm correction.

**Key result:** CatBoost achieves best mean RMSE **0.084 m** (R² = 0.73) under P2. Performance degrades to RMSE **0.171 m** under P3, exposing a site-identity confound masked by conventional random splits.

---

## Reproducing the Results

### On Kaggle (recommended)

1. **One-time setup per notebook:**
   - Create a GitHub fine-grained personal access token scoped to this repo with *Contents: Read and write*.
   - On Kaggle: *Add-ons → Secrets* → add it as `GITHUB_TOKEN`, attach to each notebook.
   - Session options → *Internet: on*, Persistence → *Variables and Files*.

2. **Run notebooks in order:**
   ```
   01_eda.ipynb
   02_baselines_and_ml_benchmark.ipynb   (N_TRIALS=40, n_repeats=10)
   03_interpretability.ipynb
   04_uncertainty_ablations.ipynb
   ```
   Each notebook auto-pulls prior outputs from GitHub at startup and pushes its own results on completion.

3. **Generate paper tables locally:**
   ```bash
   git pull   # fetch outputs/ pushed by Kaggle
   python paper/make_tables.py --outputs outputs
   ```

### Locally

```bash
git clone https://github.com/mobashshir-ubn-zainuddin/Rock-fragmentation-analysis-post-blasting
cd Rock-fragmentation-analysis-post-blasting
pip install scikit-learn xgboost lightgbm catboost shap dill joblib pandas numpy matplotlib
jupyter notebook notebooks/01_eda.ipynb
```

> The full benchmark (P2: 10 repeats × 5 folds × 40 Optuna trials × 10 models) is compute-heavy. Use `N_TRIALS=5, n_repeats=3` for a quick local check.

---

## Compiling the Paper

```bash
cd paper
pdflatex paper.tex
bibtex paper
pdflatex paper.tex
pdflatex paper.tex
```

Requires a LaTeX distribution with IEEEtran, booktabs, siunitx, hyperref, amsmath. Tested with MiKTeX on Windows and TeX Live on Linux.

---

## Security Note

`GITHUB_TOKEN` is read fresh from Kaggle Secrets for every git command and passed only as a one-off `-c http.extraheader=...` argument — never written into `.git/config` or any notebook output file. Keep the token scoped to this repository only.

---

## Citation

If you use this dataset or benchmark, please cite the original database sources:

- T. Hudaverdi, P. H. S. W. Kulatilake, and C. Kuzu, "Prediction of blast fragmentation using multivariate analysis procedures," *Int. J. Numer. Anal. Methods Geomech.*, vol. 35, no. 12, 2011.
- P. H. S. W. Kulatilake, W. Qiong, T. Hudaverdi, and C. Kuzu, "Mean particle size prediction in rock blast fragmentation using neural networks," *Engineering Geology*, vol. 114, no. 3–4, 2010.
