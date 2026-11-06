# 08 Stability of the factor structure across samples

**Notebook:** [`08_cross-sample-stability.Rmd`](08_cross-sample-stability.Rmd)

## What it does

Tests whether the instability of the scale lies in the visualization items, by comparing the
**exploratory sample** (phase 2.2, 506 participants) with the **validation sample** (phase 3).
Structures: `3_Factor_A` (final model) and `4_Factor_C` (EFA of the validation sample).

1. **Measurement invariance across samples:** multi-group CFA with the sample as the group,
   configural → metric → scalar. A level holds when ΔCFI ≤ 0.010 and ΔRMSEA ≤ 0.015
   (Chen, 2007); the LRT is reported too. When a level fails, the constraint with the largest
   score test (`lavTestScore`) is freed, one at a time, until the level holds (partial
   invariance). The freed constraints show which items differ between the samples.
2. **Standardized loadings by sample:** the same CFA in each sample, item by item, with the
   change (flagged when |Δλ| ≥ 0.10) and a summary by content block.
3. **The same EFA in both samples:** 13 items, smoothed polychoric correlations, MinRes,
   Promax, 3 and 4 factors (as step 06). Factors are matched with Tucker's congruence (φ), and
   each item's primary factor is compared.

4. **Follow-up A, item distributions** (added 2026-11-05): mean, skew, kurtosis, % of
   answers 6–7 and options left, per item and sample. Tests whether the effectiveness items of
   `4_Factor_C` are the ones with the strongest ceiling in validation (a possible "difficulty
   factor").
5. **Follow-up B, modification indices** of `3_Factor_A` in each sample: residual covariances
   and cross-loadings, summed by pair of content blocks, to see where the worse fit of the
   validation sample comes from.

CFA specification as steps 05–07: ML, `missing = "fiml"`, collapsed data. The exploratory
scale (−3 … +3) is recoded to 1 … 7 so intercepts are comparable.

Reading notes:

- Metric invariance concerns **unstandardized** loadings. If all loadings of a factor change by
  the same proportion, the change is absorbed by the factor variance and metric invariance
  still holds, while the **standardized** loadings of test 2 can differ. The two tests answer
  different questions.
- Rare options were collapsed within each sample; the `Answer_options` sheet shows where the
  options left differ, which can affect intercepts.
- The samples differ in tools and population; non-invariance does not say which difference
  causes it.

## Inputs

| File | From |
|---|---|
| `phase2-2-item-reduction/data/prepared/ratings-stimulus_collapsed.csv` | phase 2.2 `data/prepare_data.py` |
| `00_collapse-categories/output/multigroup_ratings.csv` | [step 00](../00_collapse-categories/README.md) |
| `data/codebook/items.csv` | item code, short name, content block |

## Outputs (`output/`)

| File | Content |
|---|---|
| `Cross_Sample_Stability.xlsx` | Sheets `1_Invariance`, `1_LRT`, `1_Partial_invariance`, `1_Freed_constraints`, `2_Loadings_by_sample`, `2_Loadings_CI`, `3_EFA_congruence`, `3_EFA_primary_factor`, `3_EFA_loadings`, `Answer_options`, `A_Distributions`, `A_Distributions_wide`, `B_Modification_idx` |
| `run_info.txt`, `sessionInfo.txt` | Data files, MD5, run time; R session |
