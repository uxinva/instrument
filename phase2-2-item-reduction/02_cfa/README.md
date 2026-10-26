# 02 Multi-group CFA

**Notebook:** [`02_cfa.Rmd`](02_cfa.Rmd) · **Report:** `02_cfa.html`

## What it does

For every version and model, the notebook fits a **multi-group confirmatory factor analysis** with `lavaan`:

- **Groups:** stimulus (Tableau, Qlik, Power BI, Gephi, JMP).
- **Estimation:** maximum likelihood with full-information ML for missing data (`missing = "fiml"`). This is the same specification as the old notebooks.
- **Structure:** one latent factor per scale, with the items as indicators.
- **Full model:** fitted once per structure. Versions A–D share the 3-factor full model, i.e. the 49 items that started the phase (`screened_3_factors`; before 2026-10-18 it was the 65 EFA items). Version E uses the 4-factor one (61 items).
- **Measurement invariance:** configural, metric (equal loadings) and scalar (equal loadings and intercepts), compared with likelihood-ratio tests. Off by default (`invariance: FALSE` in the YAML header); set it to `TRUE` to run it (much slower).
- **Convergence:** the notebook records whether each model converged and any lavaan warning, and lists the problem models at the end of the run.

Item lists come from [`../item_versions_config.R`](../item_versions_config.R), the same file as step 01.

## Inputs

| File | Content |
|---|---|
| `../data/prepared/ratings-stimulus_collapsed.csv` | Collapsed ratings (see [data](../data/README.md)) |
| `../item_versions_config.R` | Item lists for all versions and models |

## Outputs (`output/`)

| File | Content |
|---|---|
| `fit_summary_wide.csv` | **Fit for the paper table**: χ², df, p, TLI, CFI, RMSEA, SRMR; rows = index × model, columns = version |
| `fit_all_versions_long.csv` | One row per version × model: convergence, warnings, χ², df, p, CFI, TLI, RMSEA (+ 90% CI), SRMR, N, number of parameters |
| `fit-summary-table.tex` | **Paper table** (LaTeX, label `tab:fit-summary`): χ² (df), CFI, TLI, RMSEA and SRMR by model and version, in the layout of *Results Summary* (Table 10). Needs `graphicx` |
| `invariance_all_versions.csv` | Configural / metric / scalar comparison for every reduced model (LRT, CFI, TLI, RMSEA, SRMR) |
| `<Version>/fit_indices-<model>.csv` | All `lavaan::fitMeasures` for that model |
| `<Version>/std_loadings-<model>.csv` | Standardised loadings per group; `group` is lavaan's group number and `stimulus` the tool name (column added on 2026-10-16; runs before that have only the number) |
| `<Version>/factor_cor-<model>.csv` | Latent factor correlations per tool (added on 2026-10-16) |
| `<Version>/invariance-<model>.csv` | Invariance comparison for that model |
| `run_info.txt`, `sessionInfo.txt` | Data file, MD5, run time, R and package versions |

## Comparison with the old results

The old *Results Summary* fit values were computed on different data, most likely the **uncollapsed** ratings (as the old reliability values were; this cannot be confirmed because the uncollapsed source file is missing). They are therefore **not** expected to match. Same model structure (npar = 990, df = 10060, N = 506), different data:

| Version A–D, full model | χ² | CFI | TLI | RMSEA | SRMR |
|---|---|---|---|---|---|
| Old (uncollapsed data) | 19462.995 | 0.608 | 0.595 | 0.0961 | 0.0861 |
| New (collapsed data, 2026-10-15) | 18509.487 | 0.637 | 0.624 | 0.0911 | 0.0819 |

In the old table, the SRMR of Version E Model_1 showed the RMSEA by mistake.

**WRMR** is not reported. It is only defined for the WLSMV estimator, and this analysis uses ML, so the WRMR row of the old table stays empty.
