# 00 Collapse categories

**Notebook:** [`00_collapse-categories.Rmd`](00_collapse-categories.Rmd) · **Report:** [`00_collapse-categories.html`](https://uxinva.github.io/instrument/phase3-validation/00_collapse-categories/00_collapse-categories.html)

## What it does

Some answer options of the UXVis items (7-point scale) were chosen by very few participants. For each item, the notebook repeatedly merges any option chosen by at most 2.5 % of the participants (`threshold_val <- 0.025`) into its most frequent neighbouring option. Every merge is logged.

Only the 13 UXVis items are collapsed. The metadata (`id`, `seed`, `stimulus`) and the SUS and UEQ-S answers are left unchanged.

The notebook then writes the two combined files used by later steps (these used to be made by hand):

- the collapsed UXVis items joined with the uncollapsed SUS and UEQ-S answers (used by step 03);
- the collapsed UXVis items with the item codes replaced by their short names from the [codebook](../data/codebook/items.csv) (used by steps 05 and 06).

## Inputs

| File | From |
|---|---|
| `ux_ratings.csv` | [`data/prepared/`](../data/README.md) |
| `sus_ratings.csv` | [`data/prepared/`](../data/README.md) |
| `ueqs_ratings.csv` | [`data/prepared/`](../data/README.md) |
| `items.csv` | [`data/codebook/`](../data/codebook/) |

## Outputs (`output/`)

| File | Content | Used by |
|---|---|---|
| `ux_ratings_lowfreqcollapsed.csv` | UXVis items after merging rare options | — |
| `ux_ratings_changes_made.csv` | Log of merges: item, from, to, proportion, number of cases | — |
| `uxColaps_sus_ueqs_ratings.csv` | Collapsed UXVis items + uncollapsed SUS and UEQ-S | step 03 |
| `multigroup_ratings.csv` | Collapsed UXVis items, named with their short names | steps 05, 06 |
