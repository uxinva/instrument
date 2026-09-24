# 04 Number of factors

**Notebook:** [`04_number-of-factors.Rmd`](04_number-of-factors.Rmd) · **Reports:** [3 factors](https://uxinva.github.io/instrument/phase3-validation/04_number-of-factors/04_number-of-factors_3-factors.html) · [4 factors](https://uxinva.github.io/instrument/phase3-validation/04_number-of-factors/04_number-of-factors_4-factors.html)

## What it does

Exploratory factor analysis (EFA) on the polychoric correlation matrix of the 13 UXVis items (from step 03):

1. **Is the data suitable for factor analysis?** Bartlett's test of sphericity and the Kaiser-Meyer-Olkin index (KMO, including the value for each item).
2. **How many factors?** Horn's parallel analysis (MinRes), shown as a scree plot.
3. **EFA** with minimum residual (MinRes) extraction and two oblique rotations, **Oblimin** and **Promax**. The results are:
   - factor loadings
   - communalities (h²) and uniquenesses (u²)
   - item complexity
   - correlations between factors (Φ)
   - fit indices: TLI, RMSEA, RMSR and BIC

The notebook runs twice, controlled by the `k_factors` parameter:

| `k_factors` | Why | Output folder |
|---|---|---|
| 4 | Number suggested by the scree plot | `output/4-factors/` |
| 3 | Number of factors in the theoretical model | `output/3-factors/` |

`render_all.R` runs both versions.

## Inputs

| File | From |
|---|---|
| `polychoric_correlation_matrix_r.csv` | [step 03](../03_polychoric-correlations/README.md) `output/uxvis-scales/` |
| `polychoric_correlation_matrix_n.csv` | [step 03](../03_polychoric-correlations/README.md) `output/uxvis-scales/` |

## Outputs (`output/3-factors/` and `output/4-factors/`)

| File | Content |
|---|---|
| `scree_plot_parallel_analysis.pdf` | Scree plot from parallel analysis |
| `efa_factor_loadings_ordered.csv` | Oblimin: loadings sorted by main factor and loading size |
| `efa_factor_correlations.csv` | Oblimin: correlations between factors |
| `efa_global_fit_indices.csv` | Oblimin: TLI, RMSEA, RMSR, BIC |
| `efa_promax_factor_loadings_ordered.csv` | Promax: sorted loadings |
| `efa_promax_factor_correlations.csv` | Promax: correlations between factors |
| `efa_promax_global_fit_indices.csv` | Promax: fit indices |
