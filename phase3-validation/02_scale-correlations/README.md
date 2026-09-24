# 02 Scale correlations

**Notebook:** [`02_scale-correlations.ipynb`](02_scale-correlations.ipynb) (Python) · **Report:** [`02_scale-correlations.html`](https://uxinva.github.io/instrument/phase3-validation/02_scale-correlations/02_scale-correlations.html)

## What it does

Computes one score per scale or factor for each participant, then the Pearson correlations between all pairs of scores. Missing values are handled by pairwise deletion.

| Score | How it is computed |
|---|---|
| SUS | Standard scoring (Brooke, 1996): odd items `score − 1`, even items `5 − score`, sum of the 10 items × 2.5 → 0–100. Requires all 10 answers. |
| UEQ-S Pragmatic | Mean of `UEQ_1`–`UEQ_4`, after subtracting 4 (scale −3 to +3) |
| UEQ-S Hedonic | Mean of `UEQ_5`–`UEQ_8`, after subtracting 4 |
| Cognitive value | Mean of P064, P301, P060, P027 |
| Intuitiveness | Mean of P088, P026, P4026A |
| Visualization | Mean of P106, P089, P098, P097, P022A, P067 |

## How to run

Run the notebook in Jupyter from the repository root, then export the report:

```bash
jupyter nbconvert --to html phase3-validation/02_scale-correlations/02_scale-correlations.ipynb
```

## Inputs

| File | From |
|---|---|
| `ratings_grades.csv` | [`data/prepared/`](../data/README.md) |

## Outputs (`output/`)

| File | Content |
|---|---|
| `correlation_matrix.png` | Heatmap of the correlation matrix |
| `pearson_correlation_matrix.csv` | Correlations computed with `scipy.stats.pearsonr` |
| `pearson_correlation_matrix_r.csv` | Correlations computed with pandas |
| `pearson_correlation_matrix_p.csv` | p-values |
