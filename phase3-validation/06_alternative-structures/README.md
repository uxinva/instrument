# 06 Alternative structures

**Notebook:** [`06_alternative-structures.Rmd`](06_alternative-structures.Rmd) · **Report:** [`06_alternative-structures.html`](https://uxinva.github.io/instrument/phase3-validation/06_alternative-structures/06_alternative-structures.html)

## What it does

Compares **11 competing factor structures** (from 1 to 4 factors) for the UXVis scale, on the pooled data and on each of the five systems (Tableau, JMP, Excel, Data Studio, Power BI). For each sample the notebook:

1. computes smoothed polychoric correlation matrices;
2. runs Horn's parallel analysis;
3. fits EFA models (MinRes, Promax rotation, 1–4 factors) and reports the variance explained;
4. fits a CFA of every structure with full-information maximum likelihood (FIML), reporting:
   - fit indices
   - reliability (α, ω) and average variance extracted (AVE) of each factor
   - standardised loadings (λ)

The results are collected in two Excel workbooks, so each structure can be compared on the whole sample and within each system.

## Inputs

| File | From |
|---|---|
| `multigroup_ratings.csv` | [step 00](../00_collapse-categories/README.md) `output/` |

## Outputs (`output/`)

### Figures

| File | Content |
|---|---|
| `Polychoric_Correlations_Consolidated.pdf` | Polychoric correlation heatmaps: pooled and each system |
| `scree_plot_pooled.pdf` | Scree plot (parallel analysis), pooled |
| `scree_plot_<system>.pdf` | Scree plot for each system |

### Tables

| File | Content |
|---|---|
| `efa_promax_factor_loadings_ordered.csv` | Pooled 3-factor Promax solution: loadings, h², u², complexity |
| `EFA_Summary_Consolidated.xlsx` | EFA workbook (sheets listed below) |
| `CFA_Model_Fit_Comparison.xlsx` | CFA workbook (sheets listed below) |

**`EFA_Summary_Consolidated.xlsx`**

| Sheet | Content |
|---|---|
| Parallel_Analysis | Real vs. simulated eigenvalues and suggested number of factors |
| Variance_Explained | Sums of squared loadings, proportion and cumulative variance |
| `1F_Pooled` … `4F_<system>` | Loadings for the 1- to 4-factor solutions, pooled and per system |

**`CFA_Model_Fit_Comparison.xlsx`**

| Sheet | Content |
|---|---|
| Pooled_Fit | χ², df, p, CFI, TLI, RMSEA, SRMR, AIC, BIC for the 11 models (pooled) |
| Pooled_Reliability_AVE | α, ω and AVE for each factor of each model |
| Pooled_CFA_Loadings | Standardised loadings, R², standard errors and p-values |
| Multigroup_Fit | Unconstrained multi-group CFA fit for the 11 models |
| By_Stimulus_Fit | CFA fit for each system and model |
| By_Stimulus_Reliability | α, ω and AVE for each system and model |
| By_Stimulus_CFA_Loadings | Standardised loadings for each system and model |
