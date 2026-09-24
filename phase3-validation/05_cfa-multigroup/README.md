# 05 Multi-group CFA

**Notebook:** [`05_cfa-multigroup.Rmd`](05_cfa-multigroup.Rmd) · **Report:** [`05_cfa-multigroup.html`](05_cfa-multigroup.html)

## What it does

Checks the three-factor model of the 13-item UXVis scale (Cognitive value, Intuitiveness, Visualization), both on the whole sample and separately for each system. The notebook:

1. describes the sample;
2. checks normality, per item (Shapiro-Wilk) and multivariate (Mardia);
3. checks the pattern of missing data (Little's MCAR test);
4. checks that factor analysis is appropriate (Bartlett's test, KMO);
5. computes reliability: Cronbach's α, Guttman's λ6 and McDonald's ω;
6. fits the three-factor confirmatory factor analysis (CFA) with full-information maximum likelihood (FIML):
   - on the pooled data;
   - as a multi-group model across the five systems (Power BI, Tableau, JMP, Excel, Data Studio), to test whether the model holds the same way for every system (measurement invariance).

## Inputs

| File | From |
|---|---|
| `multigroup_ratings.csv` | [step 00](../00_collapse-categories/README.md) `output/` |

## Outputs (`output/`)

| File | Content |
|---|---|
| `items_correlations.csv` | Polychoric correlations of the 13 items |
| `items-correlation-plot.pdf` | Heatmap of these correlations |
| `reliability-subscales.csv` | α, standardised α and ω for each factor: pooled and per system |
| `reliability-global-by-stimuli.csv` | α and ω (1-factor and 3-factor) for each system |
| `fit_indices_pooled.csv` | CFA fit indices, pooled sample (df, χ², CFI, TLI, RMSEA, SRMR, AIC, BIC, …) |
| `fit_indices_multigroup.csv` | Multi-group CFA fit indices |
| `fit_indices_<system>.csv` | CFA fit indices for each system (`power_bi`, `tableau`, `jmp`, `excel`, `data_studio`) |
| `corr_matrix_<system>.csv` | Item correlations for each system |
