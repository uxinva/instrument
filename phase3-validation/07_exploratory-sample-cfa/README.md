# 07 CFA of the alternative structures on the exploratory sample

**Notebook:** [`07_exploratory-sample-cfa.Rmd`](07_exploratory-sample-cfa.Rmd) · **Report:** [`07_exploratory-sample-cfa.html`](https://uxinva.github.io/instrument/phase3-validation/07_exploratory-sample-cfa/07_exploratory-sample-cfa.html)

## What it does

Fits the **same 11 structures as step 06** on the **exploratory sample** of phase 2.2
(506 participants; Gephi, Power BI, Qlik, Tableau, JMP), to check how stable the 3- and
4-factor structures are across samples (suggestion of Anne-Flore Cabouat, 2026-11-04).

Specification identical to step 06: ML (lavaan default), `missing = "fiml"`, collapsed data
(≤ 2.5%, same rule); pooled, unconstrained multi-group by tool, and each tool alone. It also
records whether each solution is admissible (`lavInspect(fit, "post.check")`) and the lavaan
warnings, and compares every structure with the validation results of step 06.

Caveat: the 13 items of `3_Factor_A` were selected on this sample (phase 2.2, step 05), so its
fit here is optimistic; `4_Factor_C` was derived from the EFA of the validation sample.

## Inputs

| File | From |
|---|---|
| `phase2-2-item-reduction/data/prepared/ratings-stimulus_collapsed.csv` | phase 2.2 `data/prepare_data.py` |
| `phase3-validation/data/codebook/items.csv` | item code → short name |
| `06_alternative-structures/output/CFA_Model_Fit_Comparison.xlsx` | [step 06](../06_alternative-structures/README.md), for the comparison |

## Outputs (`output/`)

| File | Content |
|---|---|
| `CFA_Model_Fit_Exploratory.xlsx` | Same sheets as step 06 (fit, α/ω/AVE, loadings, latent correlations; pooled, multi-group, by tool), plus `admissible` and `warnings` |
| `Comparison_Exploratory_vs_Validation.xlsx` | Pooled and multi-group fit side by side, with the change; α, ω and AVE of `3_Factor_A` and `4_Factor_C` |
| `run_info.txt`, `sessionInfo.txt` | Data file, MD5, run time; R session |
