# CSV Dataset Exploration & XGBoost Classification

End-to-end data science notebook: synthetic dataset generation, EDA, data cleaning, visualization, and a scikit-learn + XGBoost classification pipeline with full evaluation.

---

## Project Structure

```
csv_exploration.ipynb   # Main notebook (all sections below)
sample_dataset.csv      # Auto-generated on first run — do not commit
```

---

## Notebook Sections

| # | Section | Description |
|---|---------|-------------|
| 1 | Generate Synthetic Dataset | Creates `sample_dataset.csv` (300 rows, 6 columns, injected nulls & duplicates) |
| 2 | Basic EDA | Shape, dtypes, `describe()`, missing value audit |
| 3 | Data Cleaning | Drop duplicates, median imputation, dtype enforcement |
| 4 | Visualizations | Histograms, bar charts, correlation heatmap |
| 5 | Feature Analysis | IQR outlier detection, box plots, pairplot |
| 6 | Scikit-learn Pipeline + XGBoost | Full ML pipeline: preprocessing → XGBClassifier |
| 7 | Cross-Validation & ROC / PR Curves | 5-fold CV metrics table, fold accuracy plot, ROC and PR curves |

---

## ML Pipeline

**Task**: Multiclass classification — predict `department` (`Engineering`, `HR`, `Marketing`, `Sales`) from `age`, `salary`, `years_exp`, `score`, `gender`.

**Pipeline architecture**:

```
ColumnTransformer
├── Numeric  [age, salary, years_exp, score]  →  SimpleImputer(median)  →  StandardScaler
└── Categorical  [gender]                     →  SimpleImputer(most_frequent)  →  OneHotEncoder
        ↓
XGBClassifier(n_estimators=200, max_depth=4, learning_rate=0.1)
```

### Model Performance Metrics

> Run Section 7 of the notebook to reproduce. Values below are representative of the synthetic dataset.

| Metric | Train (mean ± std) | Validation (mean ± std) |
|--------|-------------------|------------------------|
| Accuracy | — | ~0.27 ± 0.04 |
| F1 Macro | — | ~0.27 ± 0.04 |
| F1 Weighted | — | ~0.27 ± 0.04 |
| ROC-AUC (OvR weighted) | — | ~0.50 ± 0.05 |

> **Note**: Near-chance performance is expected — the synthetic dataset has no real signal between features and department labels (both are randomly generated). On real data with genuine feature-target relationships, XGBoost typically achieves significantly higher scores.

### Per-Class Evaluation (Test Set)

| Class | Precision | Recall | F1-Score |
|-------|-----------|--------|----------|
| Engineering | varies | varies | varies |
| HR | varies | varies | varies |
| Marketing | varies | varies | varies |
| Sales | varies | varies | varies |

Run `Section 6 → classification_report` cell to get exact per-class figures from your run.

---

## Setup & Installation

### Requirements

- Python 3.11+
- Jupyter (via VS Code extension or `jupyter notebook`)

### Install dependencies

```bash
pip install numpy pandas matplotlib seaborn scikit-learn xgboost
```

If you see `numpy.dtype size changed` binary incompatibility errors, force-reinstall the affected package:

```bash
pip install --force-reinstall --no-cache-dir <package-name>
```

### Run the notebook

1. Open `csv_exploration.ipynb` in VS Code or JupyterLab
2. Select your Python kernel
3. **Kernel → Restart & Run All**

`sample_dataset.csv` is generated automatically by Section 1 — no external data needed.

---

## Key Design Decisions

- **Imputation inside the pipeline**: raw CSV is passed to the pipeline directly so no data leakage occurs from the earlier cleaning steps in Section 3.
- **Stratified splits**: `train_test_split` and `StratifiedKFold` both use `stratify=y` to preserve class balance across folds.
- **One-vs-Rest for curves**: ROC and PR curves are computed per class (OvR) since XGBoost's `predict_proba` returns per-class probabilities.
