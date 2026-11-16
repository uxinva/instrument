# Step 03: confirmatory factor analysis of the 1–6 factor structures

> **Status:** new on 2026-11-13. This analysis was not part of the original material. It tests, as confirmatory models, the EFA structures of [step 01](../01_efa/README.md).

## EFA fit and CFA fit

- **EFA (step 01).** Every item loads on every factor. The fit indices of `psych::fa` (TLI, RMSEA, RMSR, BIC) describe how well this free solution reproduces the polychoric correlations.
- **CFA (this step).** Each item loads **only** on the factor of its largest EFA loading. All other loadings are fixed at zero, and the factors may correlate. Cross-loadings that the EFA absorbs become misfit here. The fit is judged with the usual CFA criteria (Hu & Bentler, 1999).

For 3 factors, the structure tested is the `full_UX_3_factors` list of the paper: 25, 18 and 22 items.

## How to run

Run step 01 first. Then open `instrument.Rproj` and knit `03_cfa-structures.Rmd`, or run from the root:

```bash
Rscript -e 'rmarkdown::render("phase2-1-scale-development/03_cfa-structures/03_cfa-structures.Rmd")'
```

R packages: `lavaan` 0.6-21 and `here`. The run takes about 8 minutes.

## Method

- **Data:** `data/prepared/ratings-stimulus_collapsed.csv` (whole sample, 506 participants, 65 items, rare options collapsed). The tools are pooled in a single group.
- **Structures:** read from `01_efa/output/loadings/pa-<k>-factors-agg.csv` (k = 1–6). Each item is assigned to the factor of its largest loading.
- **Two estimators:**
  - **ML** with full-information maximum likelihood for missing answers (`missing = "fiml"`), as in the manual CFA testing of phase 2.2. Starting values come from the listwise solution; without them, the 5-factor model did not finish in 15 minutes.
  - **WLSMV** with the items declared ordinal (`ordered = TRUE`, missing answers handled pairwise). Like the EFA, it is based on polychoric correlations. Its fit indices are the scaled ones.
- **ML fit indices:** CFI, TLI, RMSEA and its 90% CI are computed from the χ² of the model and of the independence model, with the formulas of `lavaan`. With FIML, `lavaan::fitMeasures` takes about 100 s per model for each of these indices. The formulas were checked against `fitMeasures` for the 1-factor model; the values are identical.

## Output (`output/`)

| File | Content |
|---|---|
| `item-assignment.csv` | Factor of each item in the 1–6 factor structures |
| `cfa-fit-by-structure.csv` | χ², df, CFI, TLI, RMSEA (with 90% CI), SRMR and BIC (ML only), for each structure and estimator |
| `efa-vs-cfa-fit.csv` | EFA fit (from `01_efa/output/fit-indices.csv`) next to the CFA fit, by number of factors |
| `table-cfa-fit.tex` | LaTeX table (booktabs) of the CFA fit, ML and WLSMV, for the paper (`tab:cfa-fit`) |
| `factor-correlations-wlsmv.csv` | Smallest and largest correlation between factors (WLSMV) |

The rendered report is `03_cfa-structures.html`.

## Results (2026-11-13)

| Factors | EFA CFI | EFA TLI | EFA RMSEA | EFA RMSR | EFA BIC | CFA ML CFI / TLI | CFA ML RMSEA | CFA ML SRMR | CFA ML BIC | CFA WLSMV CFI / TLI | CFA WLSMV RMSEA | CFA WLSMV SRMR |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | .752 | .744 | .073 | .040 | −5091 | .800 / .794 | .057 | .054 | 81,424 | .924 / .921 | .050 | .058 |
| 2 | .823 | .810 | .063 | .029 | −6301 | .856 / .851 | .049 | .051 | 80,501 | .949 / .947 | .041 | .049 |
| **3** | .848 | .832 | .059 | .025 | **−6534** | .866 / .861 | .047 | .050 | 80,338 | .951 / .950 | .040 | .049 |
| 4 | .862 | .842 | .057 | .023 | −6515 | .868 / .863 | .047 | .050 | 80,323 | .952 / .950 | .040 | .048 |
| 5 | .873 | .850 | .056 | .021 | −6445 | .872 / .867 | .046 | .050 | **80,276** | .953 / .951 | .040 | .048 |
| 6 | .883 | .855 | .055 | .020 | −6333 | .872 / .867 | .046 | .051 | 80,291 | .953 / .951 | .040 | .048 |

- **BIC disagrees between the EFA and the CFA.** The EFA BIC is lowest for **3 factors**. The CFA (ML) BIC is lowest for **5 factors**, although the 3-, 4- and 5-factor values are close (80,338, 80,323 and 80,276).
- **The alternative criterion of Hu and Bentler (SRMR ≤ .08 and RMSEA ≤ .06) is met by every structure, including the 1-factor model** (ML RMSEA .057, SRMR .054). On these data it does not discriminate between the structures.
- **CFI/TLI ≥ .95.** No ML model reaches it; the best is .87. With WLSMV, CFI reaches .95 from 3 factors on; TLI reaches it only from 5 factors on (the .950 shown for 3 and 4 factors is .9498 and .9499).
- **Little gain beyond 3 factors.** From 3 to 6 factors the CFA indices change by less than .01, while from 1 to 3 factors they change markedly.
- **The factors are highly correlated** (WLSMV): .84–.92 in the 3-factor structure. Correlations above about .85 are often read as weak discriminant validity. In the 4–6 factor structures the factor correlations range from .76 to .92.

**Why the EFA and CFA indices differ.** The two sets are computed differently:

- The EFA indices come from `psych::fa`, with a maximum-likelihood formula applied to the polychoric matrix.
- The CFA indices come from `lavaan`, on the raw data (ML) or on the ordinal model (WLSMV).

A CFA index can therefore be better than the EFA one even though the CFA is more restrictive. RMSR (EFA) and SRMR (CFA) are related but not the same statistic.
