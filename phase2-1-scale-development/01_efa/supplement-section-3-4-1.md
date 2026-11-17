# Supplementary note: Section 3.4 (appropriateness of the data, factorability, number of factors)

Script: `phase2-1-scale-development/01_efa/01_efa.Rmd`, unless stated otherwise. Output paths without a folder are relative to `phase2-1-scale-development/01_efa/output/`.

## 3.4.1.2 Empirical Observations in Survey Data

| Data | File |
|---|---|
| Shapiro-Wilk test, skewness and kurtosis per item; share of answers in the top categories and in the negative categories | `item-normality.csv` |
| Mardia's test of multivariate normality | `sampling-adequacy-summary.csv` |
| Item histograms (uncollapsed answers, 2.5% threshold) | `plots/figure-histograms-task-cognition.pdf`, `plots/figure-histograms-system.pdf`, `plots/figure-histograms-visualization.pdf` |

## 3.4.1.3 Methodological Decisions and Justifications

| Data | File |
|---|---|
| Polychoric correlation matrices (whole sample and each tool) | `correlations/polychoric-<group>.csv` |
| Principal axis loadings, 1–6 factors | `loadings/pa-<k>-factors-<group>.csv` |
| Fit indices | `fit-indices.csv` |

## 3.4.2 Factorability and Sampling Adequacy

| Data | File |
|---|---|
| Size of the polychoric correlations (share above .30 and .50, negative ones) | `correlation-summary.csv` |
| Correlation plot, whole sample | `plots/polychoric-agg.pdf` |
| Bartlett's test and KMO | `sampling-adequacy-summary.csv` |

## 3.4.3.2–3.4.3.3 Scree plots, parallel analysis and solutions of 1–6 factors

| Data | File |
|---|---|
| Scree plots with parallel analysis | `plots/scree-<group>.pdf`; figures for the paper `plots/figure-scree-pooled.pdf` and `plots/figure-scree-by-system.pdf` |
| Factors suggested by parallel analysis | `sampling-adequacy-summary.csv` |
| Parallel analysis repeated with 20 seeds | `parallel-analysis-stability.csv` |
| Other criteria, whole sample (principal components, polychoric simulated data, MAP, eigenvalues > 1) | `number-of-factors-criteria-agg.csv` |
| Fit indices of the 1–6 factor solutions (RMSEA, TLI, RMSR, BIC) | `fit-indices.csv` |
| Cross-loadings of the 1–6 factor solutions | Script `phase2-1-scale-development/02_efa-loadings/efa_loadings.py`; files `phase2-1-scale-development/02_efa-loadings/output/agg/agg-loadings-<k>-factors.csv` (whole sample) and `.../output/all-groups-loadings-<k>-factors.csv` (all groups) |

## 3.4.4 Exploratory Factor Analysis

| Data | File |
|---|---|
| Loadings and variance explained, 1–6 factors (collapsed data) | `loadings/pa-<k>-factors-<group>.csv` |
| Same solutions on the uncollapsed data, whole sample | `loadings-uncollapsed/pa-<k>-factors-agg.csv` |
| Comparison collapsed vs uncollapsed (congruence, items changing factor, variance) | `collapsed-vs-uncollapsed-agg.csv` |
| Variance explained by each factor, 1–6 factor solutions, collapsed and uncollapsed | `variance-explained-agg.csv` |
| Cross-loadings and items without a loading above 0.32 | Script `phase2-1-scale-development/02_efa-loadings/efa_loadings.py`; file `phase2-1-scale-development/02_efa-loadings/output/agg/agg-loadings-<k>-factors.csv` |

## 3.4.6 Fit of the factor structures

| Data | File |
|---|---|
| EFA fit indices (CFI, TLI, RMSEA, RMSR, BIC) | `fit-indices.csv`; LaTeX table `table-efa-fit.tex` |
| CFA of the 1–6 factor structures (ML-FIML and WLSMV): CFI, TLI, RMSEA, SRMR, BIC | Script `phase2-1-scale-development/03_cfa-structures/03_cfa-structures.Rmd`; file `phase2-1-scale-development/03_cfa-structures/output/cfa-fit-by-structure.csv`; LaTeX table `.../output/table-cfa-fit.tex` |
| EFA and CFA fit side by side | `phase2-1-scale-development/03_cfa-structures/output/efa-vs-cfa-fit.csv` |
| Items of each factor in the 1–6 factor structures | `phase2-1-scale-development/03_cfa-structures/output/item-assignment.csv` |
| Correlations between factors (CFA, WLSMV) | `phase2-1-scale-development/03_cfa-structures/output/factor-correlations-wlsmv.csv` |

`<group>` is `agg` (whole sample), `tableau`, `qlik`, `power-bi`, `gephi` or `jmp`. `<k>` is the number of factors, 1–6.
