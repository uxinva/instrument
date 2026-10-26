# Data

## Files

| File | Content |
|---|---|
| `raw/ratings-stimulus_original.csv` | Ratings of the 65 items by 506 participants, **uncollapsed** (−3 … +3), with the tool each participant rated |
| `raw/survey_seed_system/SeedSystem1.xlsx`, `SeedSystem2.xlsx` | Exported from the survey tool on 2026-10-16: `Response ID`, `Seed` and `SYSTEM` (the tool rated) of **all** responses, including incomplete ones (3,140 seeds). Used to check the tool labels. |
| `prepare_data.py` | Checks the tool labels and collapses rare answer options (see below) |
| `prepared/ratings-stimulus_collapsed.csv` | **Input of steps 01 and 02**: the same ratings with rare answer options collapsed |
| `prepared/collapse_changes.csv` | Every merge that was made: item, original option, new option, number of answers, size of the left and right neighbours |
| `prepared/label_check.csv` | Tool label in the data vs. in the survey export (and which export file), per participant |
| `codebook/items.csv` | Item code, wording, and factor in the 3-factor and the 4-factor structures |

## How to rebuild `prepared/`

From the repository root (Python ≥ 3.11 with `pandas` and `openpyxl`):

```bash
python phase2-2-item-reduction/data/prepare_data.py
```

The script does two things:

1. **Checks the tool labels.** It compares the `stimulus` column with the survey exports and stops if any label disagrees, or if a seed has more than one tool in the exports. All **506** participants are in the exports, and all 506 labels agree.
2. **Collapses rare answer options.** For each item, an answer option chosen by **≤ 2.5%** of the non-missing answers is merged into the **neighbouring option with more answers** (left or right; on a tie, the left one). The merge repeats until no option is below the threshold. This is the rule of `phase2-2-itemreduction/Notebooks/Reproduce4_Notebooks/04_Colapsing_Low-Frequency_Categories-toMoreFrequent.R`. The script made 111 merges in 64 items, all of them to the right: the rare options are at the negative end of the scale, where the left neighbour is empty or already merged. The result is therefore identical to the "toRight" variant of the script. `collapse_changes.csv` records the size of both neighbours for every merge.

## `prepared/ratings-stimulus_collapsed.csv`

| Column | Content |
|---|---|
| `seed` | Participant identifier (anonymous) |
| `stimulus` | Tool the participant rated: Gephi (104), Power BI (102), Qlik (101), Tableau (100), JMP (99) |
| `P012` … `P305` | 65 item ratings. Empty cells are missing answers. |

The attention checks P901 and P902 are not in the data; they were removed earlier.

MD5 of the prepared file: `eb83954b17ac6ef2149f63f4f7c0c572`.

## Correction of the tool labels (2026-10-15)

The collapsed file used in the April 2026 analyses (`phase2-2-itemreduction/Data/Reproduce2_Data/ratings-stimulus.csv`, with identical copies in Reproduce3 and Reproduce4) had **wrong tool labels** for four of the five tools:

| Label in the old collapsed file | Correct label (survey export) |
|---|---|
| Tableau | Power BI |
| Power BI | Tableau |
| Gephi | JMP |
| JMP | Gephi |
| Qlik | Qlik |

The answer values were correct: the new prepared file has exactly the same values for every participant and item. Only the labels changed.

- **Not affected:** overall α and ω, and the overall fit of the multi-group CFA. The groups are the same; only their names were swapped.
- **Affected:** every result reported per tool. This covers per-stimulus reliability files and per-group loadings from any analysis that read the old collapsed file.

The uncollapsed file (`raw/ratings-stimulus_original.csv`, from `UXVis/Replication - UXVis development figures/Data/Ratings-stimulus/ratings-stimulus.csv`) and the IRT files (`Reproduce7_Data`) have the correct labels.

## Relation to the old files

- **The source of the first-draft paper tables.** `raw/ratings-stimulus_original.csv` reproduces exactly the reliability values in the first draft of the paper table. Those values were computed on uncollapsed data.
- **The misleading `RatingsOriginal` folder.** In `UXVis/…/Data/`, `RatingsOriginal/ratings-stimulus.csv` is in fact **collapsed**, with the wrong labels, despite its folder name.
