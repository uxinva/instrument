# 03 Polychoric correlations

**Notebook:** [`03_polychoric-correlations.Rmd`](03_polychoric-correlations.Rmd) · **Reports:** [UXVis items](https://uxinva.github.io/instrument/phase3-validation/03_polychoric-correlations/03_polychoric-correlations_uxvis-scales.html) · [All items](https://uxinva.github.io/instrument/phase3-validation/03_polychoric-correlations/03_polychoric-correlations_all-scales.html)

## What it does

Computes the pairwise polychoric correlations between questionnaire items. It then clusters the items hierarchically, using 1 − r as the distance, to see whether the empirical groups match the theoretical factors.

The notebook runs twice, controlled by the `scales` parameter:

| `scales` | Items | Output folder | Used by |
|---|---|---|---|
| `uxvis` | The 13 UXVis items (Cognitive value, Intuitiveness, Visualization) | `output/uxvis-scales/` | step 04 |
| `all` | UXVis items plus SUS, UEQ-S Pragmatic and UEQ-S Hedonic | `output/all-scales/` | — |

`render_all.R` runs both versions. To run one by hand:

```r
rmarkdown::render("phase3-validation/03_polychoric-correlations/03_polychoric-correlations.Rmd",
                  params = list(scales = "all"),
                  output_file = "03_polychoric-correlations_all-scales.html")
```

> This replaces the old procedure of commenting and uncommenting the definitions of `item_groups` and `group_colors`.

## Inputs

| File | From |
|---|---|
| `uxColaps_sus_ueqs_ratings.csv` | [step 00](../00_collapse-categories/README.md) `output/` |

## Outputs (`output/uxvis-scales/` and `output/all-scales/`)

| File | Content |
|---|---|
| `heatmap_construct.png` | Heatmap with the items ordered by factor |
| `heatmap_empirical_cluster.png` | Heatmap with the items ordered by the clustering |
| `dendrogram.png` | Dendrogram of the item clustering |
| `polychoric_correlation_matrices.pdf` | The two heatmaps and the dendrogram in one PDF |
| `polychoric_correlation_matrix_r.csv` | Correlation coefficients (r) |
| `polychoric_correlation_matrix_p.csv` | Approximate p-values |
| `polychoric_correlation_matrix_n.csv` | Number of valid pairs (N) |
| `polychoric_correlation_long.csv` | One row per item pair: factors, r, p, N |
