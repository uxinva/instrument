# Step 01: exploratory factor analysis

> **Status:** reproduced on 2026-11-12. Every loading, polychoric correlation and KMO matches the run of 2026-03-18 to within 1e-6.

This step runs the exploratory factor analysis (EFA) of the exploratory survey: 65 items and 506 participants. It runs once on the whole sample (`Agg`) and once on each of the five tools. The three-factor solution on the whole sample is the starting point of [phase 2.2](../../phase2-2-item-reduction/README.md).

## How to run

Open `instrument.Rproj` (repository root) and knit `01_efa.Rmd`, or run from the root:

```bash
Rscript -e 'rmarkdown::render("phase2-1-scale-development/01_efa/01_efa.Rmd")'
```

You need R 4.5.2 with `psych`, `corrplot`, `naniar`, `here` and `rmarkdown` (see `renv.lock`). The run takes about 1–2 minutes. First run `data/prepare_data.py` once so that `data/prepared/by-tool/` exists (see [`data/README.md`](../data/README.md)).

## Input

| File | Content |
|---|---|
| `../data/prepared/ratings-stimulus_collapsed.csv` | Whole sample (506), rare options collapsed over the whole sample |
| `../data/prepared/by-tool/ratings-<tool>_collapsed.csv` | One file per tool (Tableau 100, Qlik 101, Power BI 102, Gephi 104, JMP 99), rare options collapsed **within** the tool |
| `input/reference-2026-03-18/` | Results of 2026-03-18, used only for the comparison. Copied from the OSF supplemental folder, `Phase 2 - Scale Development/Data/05_Data/260318Data_Analysis-PolyCorr-2_5_Collapsed/generatedData-EFA/`. Contents: PA loadings for 1–6 factors × 6 groups, polychoric matrices and the sampling-adequacy summary. |

## Method

This follows `Notebooks/01_Notebooks/01-EFAFactorLoadings.Rmd` of the OSF folder. For each group:

1. Missing data: the percentage of missing answers and Little's MCAR test (`naniar::mcar_test`). Multivariate normality: Mardia's test.
2. Polychoric correlations (`psych::polychoric`, default settings).
3. Factorability: KMO, Bartlett's test, the determinant, and Cronbach's α (from the data and from the matrix).
4. Parallel analysis (`fa.parallel`, `fa = "fa"`, 100 iterations, seed 257).
5. EFA with principal axis extraction (`fm = "pa"`) on the polychoric matrix: 1 factor unrotated, then 2–6 factors with promax rotation. Loadings are sorted with `fa.sort`.
6. Fit indices for each solution: χ², df, RMSEA with its CI, TLI, BIC and RMSR.

Differences from the original notebook. None of them changes a result:

- The input files are named explicitly. The original read every `.csv` in `Data/` and dropped the 7th. That breaks now that `Data/` also holds `rating-data.csv`.
- Items are named by their code only, without the wording.
- A seed is set before the parallel analysis. The original set no seed.
- The factor weights and the correlation plots in AOE and hclust order are not written.

## Output (`output/`)

| File | Content |
|---|---|
| `loadings/pa-<k>-factors-<group>.csv` | Loadings (k = 1–6; group = agg, tableau, qlik, power-bi, gephi, jmp), then a `--- VARIANCE EXPLAINED ---` row and the variance table. The layout is the same as the old `PA1 Stimuli k factors - Group.csv` files. |
| `correlations/polychoric-<group>.csv` | Polychoric correlation matrix |
| `sampling-adequacy-summary.csv` | n, % missing, MCAR p, KMO, Bartlett, determinant, α, Mardia, number of factors from parallel analysis |
| `fit-indices.csv` | Fit indices of every solution |
| `number-of-factors-criteria-agg.csv` | Whole sample: parallel analysis (factors and components, 20 seeds), MAP, eigenvalues > 1 |
| `plots/scree-<group>.pdf`, `plots/polychoric-agg.pdf` | Scree plots with parallel analysis; whole-sample correlation plot |
| `check-vs-2026-03-18.csv`, `check-kmo-vs-2026-03-18.csv` | Comparison with the reference run |
| `run_info.txt`, `sessionInfo.txt` | Date, MD5 of the inputs, R session |

The rendered report is `01_efa.html`.

## Main results (whole sample, n = 506)

- KMO = 0.964. Bartlett χ²(2080) = 24,037, p < .001. Determinant = 2.3e-22. α = 0.972.
- **Number of factors.** The criteria disagree, from 3 to 5 factors (table below). The first factor dominates: the first eigenvalues are 29.1, 3.1, 1.9, 1.3, 1.2 and 1.1, so the drop flattens after the second or third. Phase 2.2 used the 3-factor and 4-factor solutions.

  | Criterion (same polychoric matrix) | Suggested factors |
  |---|---|
  | Parallel analysis, factors (`fa = "fa"`; the criterion of the original notebook) | **5** (in all 20 seeds; also 5 on 2026-03-18) |
  | Parallel analysis, principal components | **3** (in all 20 seeds) |
  | Velicer's MAP | **4** |
  | Eigenvalues > 1 (Kaiser; known to over-extract) | 9 |

  These criteria were added to the notebook on 2026-11-13 (`output/number-of-factors-criteria-agg.csv`). They do not change any loading. Which criterion supported the 3-factor choice in the original analysis is not recorded in the files of 2026-03-18.
- The three-factor solution explains 50.2% of the variance (SS loadings 12.28, 10.46 and 9.88). Fit: RMSEA = 0.059 [0.057, 0.061], TLI = 0.832, RMSR = 0.025.
- `loadings/pa-3-factors-agg.csv` has the same values as `phase2-2-item-reduction/00-efa-screening/input/efa-pa-3-factors-agg.csv` to within 1e-11. The files are not byte-identical: item names are codes only, and the last digits differ.

Each tool has about 100 participants for 65 items. The per-tool polychoric matrices are therefore not positive definite and `psych` smooths them, which triggers warnings. The per-tool solutions should be read with this in mind.

## Check against 2026-03-18

| Quantity | Largest difference |
|---|---|
| Loadings (36 solutions: 6 groups × 1–6 factors), same item order in all | 1.6e-11 |
| Polychoric correlations (6 groups) | 1.8e-11 |
| KMO, whole sample | 5e-14 |
| KMO, per tool | 6.7e-8 (see below) |
| % missing, Little's MCAR, α, Mardia | identical |

- **Why the per-tool KMO differs slightly more:** KMO inverts the correlation matrix. The smoothed per-tool matrices have a condition number of about 3e11, so differences of 1e-11 in the correlations become about 1e-8 in KMO.
- **Parallel analysis is random.** Each group gets the same number of factors as on 2026-03-18, except JMP. The groups do not agree with each other: Agg 5; Tableau, Qlik and Gephi 2; Power BI 4; JMP 3 (2 on 2026-03-18). Across 20 seeds, JMP gives 3 in 15 runs and 2 in 5; every other group gives the same number in all 20. The 2026-03-18 run set no seed, so the JMP difference is expected. The per-tool samples (about 100 participants) suggest fewer factors than the whole sample, as is usual with small n.
- **Error in the old summary file:** the reference `Summary of Measures of Sampling Adequacy.csv` has the Mardia skewness value in its "Skew p_value" column. `sampling-adequacy-summary.csv` gives the real p-value.
