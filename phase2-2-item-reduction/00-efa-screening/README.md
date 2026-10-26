# 00 EFA screening: from 65 to 49 items

**Script:** [`screen-efa-items.py`](screen-efa-items.py) (Python ≥ 3.11 with `pandas`)

This is the starting point of the item reduction. The 3-factor EFA solution has **65 items**: Task_cognition 25, System 18, Visualization 22. This step reduces them to the **49 items** used by the following steps: Task_cognition 19, System 14, Visualization 16. These 49 are `Version_A` `Model_1` in `item_versions_config.R`, and steps 03 (IRT) and 04 (ranking) use them.

## Rules

The rules were reconstructed on 2026-10-18 and confirmed against two exports in `Gdrive_files/Exploratory Factor Analysis - temp/`:
- `3 factors selected Items - Comparison_3_4_5_factors.xlsx`: the EFA workbook. Its tab *PA1 Stimuli 3 factors – Agg* has the columns "0.32 threshold" and "Missing Data"; its tab *3_factors_items* has the selection (`Yes` / `No-crossloading` / `No-Missing`).
- `Items Historic - Items Historic.csv`: the item history. Its column "Item - Fator loading, reliability and IRT Analysis" lists the 49 retained items, and the next column gives the reason for each exclusion.

1. **Cross-loading.** An item is excluded when its **second-highest loading is above 0.32**. This is the column "0.32 threshold" of the EFA spreadsheet (tab *PA1 Stimuli 3 factors – Agg*). The script applies the rule to the loadings. **11 items** were excluded:
   - Task_cognition: P092, P095, P209, P213, P102, P201
   - System: P207, P06
   - Visualization: P105, P104, P103
2. **Missing data, reviewed with the three-factor solution and the item content.** The team excluded **5 items**: **P049, P031, P212, P09 and P305**. Missing answers were not a reason on their own. Items not already excluded for cross-loading and with **more than 3% missing answers in at least one system** were reviewed, and an item was excluded when it also had at least one of:
   1. a **weak primary loading** in the three-factor solution (λ < 0.40): P031 (0.27), P212 (0.39);
   2. **redundancy** with another item: P049, with P041;
   3. **content tied to a feature that only some tools offer, or to a particular kind of data**, so that the missing answers probably reflect non-applicability: P031 (latency), P212 (overview/detail), P09 (sharing results), P305 (focusing on the information of interest).

   Three reviewed items were retained because none of these applied: P067 (trial and error, λ = 0.43) and P203 (error recovery, λ = 0.41) refer to general aspects of the interaction, and the team read P096 ("link information across different visualizations", λ = 0.42) as a general characteristic of the system rather than a predefined link between views. Criterion 3 was discussed in several team meetings; this compilation of the rule dates from 2026-10-22. `review-missing-data.py` applies the rule and confirms that it reproduces every decision (`output/missing-data-review.xlsx`, column `rule_matches`). They are listed in [`input/manual-exclusions.csv`](input/manual-exclusions.csv), all confirmed:
   - the item history says "Missing data threshold" for each of them;
   - the EFA workbook has "Missing Data = TRUE" for each of them.

   The decision was not a fixed cut-off. Four items have "Missing Data = MAYBE" and were kept: P067 (3.0% missing), P203 (2.8%), P096 (1.4%) and P097 (0.6%). P4026A (2.0%) was also kept.

   **Missing-data review** ([`review-missing-data.py`](review-missing-data.py), added on 2026-10-21). The team analysed the missing answers per system in the sheet *summary_missing_data_UX* (`input/summary-missing-data-ux.csv`): the rate in each of the five systems and, for the six items with the most missing answers, the factor they load on in the 4-, 5- and 6-factor EFA solutions. A rate concentrated in one system suggests that the item asks about a feature that not every system has. This was one criterion among others, not a rule on its own. The script joins this sheet, the rates recomputed from the data (they agree with the sheet), the EFA flags and the decisions in `output/missing-data-review.xlsx`. **No combination of the recorded criteria separates the excluded items from the retained ones.** For example, P09 (excluded) and P203 (retained) have similar overall rates (2.6% and 2.8%), the same peak (4.8% in Gephi) and a stable factor in the 4–6 factor solutions. For P049, the meeting notes record a second reason (redundancy with P041); for the other items no further reason is recorded.

**History of the missing-data decision.**

| Date | Record | What it shows |
|---|---|---|
| 2026-03-12 to 03-18 | EFA workbook, tab *All Measures of Sampling* | Little's test rejects MCAR in every system (p ≤ 0.011); missing answers 0.5–1.6% per system |
| 2026-03-19 | Meeting slide and sheet *summary_missing_data_UX* | "There are some concentration in some NA by system => maybe due to this, our data are no MCAR." Removing P209 might affect the 6-factor solution; removing P212, P067 and P09 might change PA3, "not a very big deal"; P031 is the one to be most wary of removing, because it loads highly on a factor found across solutions. Anne-Flore: "I wouldn't remove any of them based on the missingness argument. The bad ones will get dropped later anyway because they have weak or moderate loadings." |
| by 2026-03-31 | IRT run `260331` | Three-factor solution chosen; still 65 items |
| 2026-03-31 to 04-08 | IRT rankings of 2026-04-08 (history PDF) | The 16 exclusions are made: the rankings use the 49 items |

The criteria and rationale for each reviewed item are in `input/missing-data-review-notes.csv` and `input/manual-exclusions.csv` (column `note`).

**A low primary loading was not a reason for exclusion.** P033 (0.320) and P045A (0.308) were kept with primary loadings just below 0.32. The script flags them in `low_primary_flag`.

The result matches `Version_A` `Model_1` exactly (see `output/check.txt`).

**Notes on the source files.**
- **P049 may have been removed earlier.** The notes of the meeting of 2025-11-25 record a separate reason: "Remove because it is redundant with *I found the system's components worked seamlessly together*" (P041). The removal may have been decided after the cognitive interviews, before the EFA. It is recorded here as missing data, as in the item history, until this is checked in the EFA phase.
- **Tab *3_factors_items* lists P049 as "Yes" (50 items selected).** The tab *PA1 Stimuli 3 factors – Agg* and the item history both exclude it, and so does `Version_A` `Model_1`, so this tab was probably not updated.
- **The 0.25 label versus the 0.32 cut-off.** In the item history, the note for the 11 cross-loading items says "2nd loading bigger than 0.25". The cut-off that reproduces the selection is 0.32. With 0.25, most retained items (e.g. P060, P027) would also be flagged.

## Inputs

| File | Content |
|---|---|
| `input/efa-pa-3-factors-agg.csv` | EFA loadings (principal axis, 3 factors, polychoric correlations, all tools together, ratings collapsed at 2.5%). Copied on 2026-10-18 from `UXVis/Replication - UXVis development figures/Data_Analysis_by_date_focus/260318Data_Analysis-PolyCorr-2_5_Collapsed/generatedData-EFA/Agg/PA1 Stimuli 3 factors - Agg.csv` (MD5 2f937169c9d566d693c9ba1c2a43ef53). PA1 = Task_cognition, PA2 = System, PA3 = Visualization |
| `input/summary-missing-data-ux.csv` | Team sheet *summary_missing_data_UX* (Google Sheets `1gYWB2ORfyswcoRk0LHK93KOrwwC7Djommcr1tGN6TUw`, gid 1590052030), exported on 2026-10-21: missing % per system, and the factor in the 4-, 5- and 6-factor solutions of the six items with most missing answers |
| `input/missing-data-review-notes.csv` | For the items reviewed (more than 3% missing in a system): content scope (`feature-specific` / `general` / `not assessed`), a short description of the content and the rationale of the decision |
| `input/efa-missing-data-flags.csv` | Column "Missing Data" (TRUE / MAYBE) of the EFA workbook, tab *PA1 Stimuli 3 factors – Agg* |
| `input/manual-exclusions.csv` | Items excluded by the team in the missing-data review, with the status (`confirmed` / `inferred`), the source and a note on what else is recorded for the item |
| `../item_versions_config.R` | `full_3_factors` (65 items) and `Version_A` `Model_1` (49 items), used for the check |
| `../data/raw/ratings-stimulus_original.csv` | Used to report the percentage of missing answers per item |

## Outputs (`output/`)

| File | Content |
|---|---|
| `efa-screening-items.csv` | One row per item: factor, the three loadings, primary and second loading, low-primary flag, % missing, decision, reason, reason status and source |
| `items-after-screening.csv` | The 49 retained items per factor, with their primary loading |
| `check.txt` | Counts and comparison with `Version_A` `Model_1` |
| `missing-data-review.csv` / `.xlsx` | Missing-data review: per item, missing % overall and per system, the system with the highest rate, the factor in the 4–6 factor solutions, the EFA flag and the decision. The xlsx has the sheets *Items*, *Decision cases* (items with ≥ 2% missing or a flag) and *Notes* |
| `table-screening-decisions.tex` | **Appendix table** (`tab:screening-decisions`, `table*`): the 16 excluded items and the 3 items retained after the missing-data review, with loadings, missing % and the rule applied. Made by [`build-screening-table.py`](build-screening-table.py) |
| `table-items-after-screening.tex` | LaTeX table (`longtable`) of the 49 items by factor, with wording and loading (wording from `../data/codebook/items.csv`) |

## How to run

```bash
python phase2-2-item-reduction/00-efa-screening/screen-efa-items.py
python phase2-2-item-reduction/00-efa-screening/review-missing-data.py
python phase2-2-item-reduction/00-efa-screening/build-screening-table.py
```

## Pending

- **Check in the EFA phase when and why P049 was removed** (missing data or redundancy with P041; see the 2025-11-25 meeting notes).
- **Rule compiled on 2026-10-22** from the records and the team's account; check it with Petra and Anne-Flore when the EFA phase is documented.
- **Move the EFA files into the repository.** The EFA input comes from the UXVis folder, and the confirming exports are in the temporary folder `Gdrive_files/Exploratory Factor Analysis - temp/`. When the Exploratory Factor Analysis phase is moved into the repository, `input/efa-pa-3-factors-agg.csv` and the sources in `manual-exclusions.csv` should point to its files there.
