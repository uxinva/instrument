# Step 02: analysis of the EFA factor loadings

> **Status:** reproduced on 2026-11-13. In its check mode the script gives the outputs of the original notebook (2026-03-23) cell for cell. The default mode also fixes one error of the notebook (see below).

This step reads the principal-axis loadings of [step 01](../01_efa/README.md) for 1–6 factors and the six groups (five tools and the whole sample, `Agg`). For each group and factor it:

1. keeps the loadings above **0.32**;
2. counts the **cross-loadings**: the number of other factors on which the item also loads above 0.32;
3. assigns each item to the factor of its largest loading and **ranks** the items within each factor;
4. gives each item a global **order**: the items of factor 1 first, then those of factor 2, and so on.

Across the six groups it then counts in how many groups an item belongs to each factor (**presence count**). For an item present in all six groups it also gives the **average rank** there.

The cross-loading count is the basis of the screening of [phase 2.2, step 00](../../phase2-2-item-reduction/README.md). With 3 factors on the whole sample, exactly 11 items have a cross-loading: P06, P092, P095, P102, P103, P104, P105, P201, P207, P209 and P213. These are the 11 items excluded there.

## How to run

From the repository root (Python ≥ 3.11 with `pandas`; tested with pandas 3.0.5):

```bash
python phase2-1-scale-development/02_efa-loadings/efa_loadings.py           # corrected analysis -> output/
python phase2-1-scale-development/02_efa-loadings/efa_loadings.py --check   # reproduces the outputs of 2026-03-23
```

Run step 01 first: this step reads `01_efa/output/loadings/`. The check mode reads only the reference files and does not need step 01.

The script prints "It's a tie between factors …" lines. They come from the notebook's own code. In check mode they concern only the rows of the variance table (see below). In the default mode no tie occurs.

## Input

| File | Content |
|---|---|
| `../01_efa/output/loadings/pa-<k>-factors-<group>.csv` | Loadings of step 01 (k = 1–6; group = agg, tableau, qlik, power-bi, gephi, jmp) |
| `../01_efa/input/reference-2026-03-18/<Group>/PA1 Stimuli <k> factors - <Group>.csv` | Loadings of 2026-03-18, the input of the original notebook (check mode only) |
| `input/reference-2026-03-23/All_stimuli_EFA_loadings-<k>_factors.csv` | Outputs of the original notebook, written on 2026-03-23. Copied from the OSF supplemental folder, `Phase 2 - Scale Development/Data/05_Data/260318Data_Analysis-PolyCorr-2_5_Collapsed/generatedData-EFA/` (check mode only) |

## Method and changes from the original

Original: `Notebooks/05_Notebooks/05-EFA factor loading analysis.ipynb` in the OSF folder. The functions `set_of_observation` and `cols_to_int` and the main loop are copied unchanged. The changes:

- **Paths.** The notebook read a folder under `UXVis/Replication…`, and its saved outputs show that it was last run on other folders (`…-FatorRenamed`, `…-PolyCorr-0_Collapsed`). The script reads the files of step 01, or, in check mode, the reference files.
- **Output names.** `all-groups-loadings-<k>-factors.csv` instead of `All_stimuli_EFA_loadings-<k>_factors.csv`, and `agg/agg-loadings-<k>-factors.csv` instead of `Agg/Agg_EFA_loadings-<k>_factors.csv`. Items are named by their code only, without the wording.
- **Whole sample alone.** It is processed for 1–6 factors; the notebook did 1–5.
- **Correction: variance rows are no longer treated as items.** The loadings files end with the variance table: SS loadings, Proportion Var, Cumulative Var, Proportion Explained and Cumulative Proportion. The notebook read these rows as items. Those with values above 0.32 entered the analysis, typically SS loadings, Cumulative Var, Proportion Explained and Cumulative Proportion. They took ranks and positions, and the "tie" messages come from them. The default mode keeps only item rows.

## Effect of the correction

The script reproduces the old outputs exactly (check mode). The outputs of the default mode were then compared with them item by item (65 items, 1–6 factors, six groups):

| Columns | Effect of removing the variance rows |
|---|---|
| Loadings | none |
| Cross-loadings | none |
| Presence count (in how many groups an item belongs to each factor) | none |
| Factor rank | ranks are 0–2 positions lower; the order of the items within each group and factor is unchanged |
| Global order | positions shift by 0–7; the order of the items is unchanged |
| Average rank | values up to 2 positions lower; the order of the items within each factor is unchanged |

The variance rows therefore **changed no decision**: the same items load on the same factors, with the same cross-loadings and in the same order. Only the rank numbers in the old files are offset.

## Output (`output/`)

| File | Content |
|---|---|
| `all-groups-loadings-<k>-factors.csv` | One row per item (65). Columns: presence count per factor; cross-loadings per group (`Never above threshold` if no loading > 0.32); order per group (`Missing` if not ranked); loadings > 0.32 per factor and group; average rank per factor; factor rank per factor and group |
| `agg/agg-loadings-<k>-factors.csv` | Whole sample only. Items with no loading above 0.32 are left out: P031, P033 (0.3195) and P045A in the 3-factor solution |
| `check-legacy/` | Written by `--check`: outputs of the legacy mode, compared with `input/reference-2026-03-23/` |

## Results (whole sample)

- **3 factors:** 11 items have one cross-loading (listed above). Three items have no loading above 0.32: P031 (largest 0.27), P033 (0.32, just below the threshold) and P045A (0.31).
- **4 factors:** 9 items have a cross-loading: P025, P054, P06, P084, P092, P207, P208, P209 and P213. Five items have no loading above 0.32.
