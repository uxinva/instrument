# 01 Gold-standard reliability

**Notebook:** [`01_gold-standard-reliability.Rmd`](01_gold-standard-reliability.Rmd) · **Report:** [`01_gold-standard-reliability.html`](https://uxinva.github.io/instrument/phase3-validation/01_gold-standard-reliability/01_gold-standard-reliability.html)

## What it does

Checks the reliability of the two gold-standard questionnaires in our sample. The notebook reads the SUS and UEQ-S answers and reverse-scores the negatively worded SUS items (the even ones). Then it computes, for:

- SUS (one dimension),
- UEQ-S Pragmatic quality (`UEQ_1`–`UEQ_4`) and Hedonic quality (`UEQ_5`–`UEQ_8`),
- UEQ-S overall,

these values:

- Cronbach's α (raw and standardised)
- McDonald's ω (total)
- α if each item is dropped

## Inputs

| File | From |
|---|---|
| `sus_ratings.csv` | [`data/prepared/`](../data/README.md) |
| `ueqs_ratings.csv` | [`data/prepared/`](../data/README.md) |

## Outputs (`output/`)

| File | Content |
|---|---|
| `unified_reliability_results.csv` | Reliability for each scale, factor and item |
