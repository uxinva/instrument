# Phase 2.2: Item reduction

This phase reduces the item pool of the UX in visual analytics scale. The 3-factor EFA solution has 65 items; after the screening of step 00 (cross-loadings and missing data), the phase starts with **49 items** (19 Task_cognition, 14 System, 16 Visualization). Several reduced **versions** of the item lists are compared on reliability and model fit:

- **Versions A, B, B2, C and D** start from the **3-factor** structure: `task_cognition`, `system` and `visualization`.
- **Version E** starts from a different **4-factor** structure, which adds a `reliability` factor.

The responses come from **506 participants**, each rating one of five visual analytics tools (the **stimulus**): **Gephi** (104), **Power BI** (102), **Qlik** (101), **Tableau** (100) and **JMP** (99).

> **Status:** reproducible pipeline rebuilt on 2026-10-15 and completed on 2026-10-26. It replaces the hand-run notebooks in `phase2-2-itemreduction/` (see [Relation to the old files](#relation-to-the-old-files)). A summary of the phase (goal, data, decisions, reference results, software versions and open points) is in [`item-reduction-context.md`](item-reduction-context.md).

The phase ends with a **13-item, 3-factor instrument**: Visualization P022A, P067, P089, P097, P098, P106; Task_cognition P027, P060, P064, P301; System P026, P088, P4026A. It is selected in step 05 and evaluated again on an independent sample in `phase3-validation/` (model `3_Factor_A`).

## Versions and models

Each version has a **full** item list, the complete structure used as the baseline. It also has up to three reduced **models**:

| Model | How the items were chosen |
|---|---|
| `full_data` / `full_model` | Baseline: the 49 screened items (`screened_3_factors`) for Versions A–D; the 61 items of the 4-factor structure for Version E |
| `Model_1` | Items with the highest factor loadings |
| `Model_2` | Items selected in the IRT analysis |
| `Model_3` | Items selected in the model-definition analysis (mixed parameters) |

| Version | Structure | Items per factor | Models |
|---|---|---|---|
| A | 3 factors | Model_1: the 49 screened items (identical to the baseline); Models 2–3: 5 | 1, 2, 3 |
| B | 3 factors | 5 | 1, 2, 3 |
| B2 | 3 factors | 5 (as B, but Model_3 task_cognition uses P072 instead of P027) | 1, 2, 3 |
| C | 3 factors | 4 | 1, 2, 3 |
| D | 3 factors | 3 | 1, 2, 3 |
| E | 4 factors | 5 | 1 only |

All item lists are defined in **one file**, [`item_versions_config.R`](item_versions_config.R). Both notebooks read it. To change an item, edit only that file.

## Steps

| Step | What it does | Reads | Writes |
|---|---|---|---|
| [00 EFA screening](00-efa-screening/README.md) | From the 65 items of the 3-factor EFA solution to the 49 items used in the following steps: cross-loading > 0.32 (11 items) and the missing-data review (5 items). `screen-efa-items.py`, `review-missing-data.py` and `build-screening-table.py` (Python) | `00-efa-screening/input/`, `item_versions_config.R`, `data/raw/ratings-stimulus_original.csv` | `00-efa-screening/output/` (`tab:items-after-screening`, `tab:screening-decisions`, `missing-data-review.xlsx`) |
| [Data](data/README.md) | Checks the tool labels against the survey export and collapses rare answer options (`prepare_data.py`, Python) | `data/raw/` | `data/prepared/` |
| [01 Reliability](01_reliability/README.md) | Cronbach's α and McDonald's ω for every factor, model and version, overall and per stimulus; α if item dropped | `data/prepared/ratings-stimulus_collapsed.csv`, `item_versions_config.R` | `01_reliability/output/` (`tab:reliability-summary`, `tab:item-drop`) |
| [02 Multi-group CFA](02_cfa/README.md) | Multi-group CFA fit for every model and version (ML, FIML), plus measurement invariance | the same two files | `02_cfa/output/` (`tab:fit-summary`) |
| [03 IRT](03_irt/README.md) | Graded response model per factor (all tools together): item parameters, fit, trace-plot figures. Uses the **uncollapsed** data, as the April 2026 plots on which the IRT rubric scores were given | `data/raw/ratings-stimulus_original.csv`, `item_versions_config.R` | `03_irt/output/` |
| [04 Ranking](04_ranking/README.md) | Documents the multi-criteria triangulation ranking (reliability, loadings, IRT): extraction from the team spreadsheets, consistency checks, paper tables (`extract_ranking_criteria.py`, `build_ranking_table.py`, `build-irt-ranking-table.py`, Python). The ranking itself was a team decision | `04_ranking/ranking_criteria.csv`, `data/codebook/items.csv`, `05_combinatorial/input/candidate_pool.csv` | `04_ranking/output/` (`tab:triangulation-ranking`, `tab:IRT-ranking`, `ranking_table_full.csv`) |
| [05 Combinatorial](05_combinatorial/README.md) | Automated combinatorial reduction: reliability prefilter and one single-group CFA (MLR, uncollapsed data) per combination. `generate_combinations.py`, `05_combinatorial.Rmd`, `run-all-thresholds.R` (all thresholds, exhaustive), `build_runs_table.py` | `05_combinatorial/input/`, `data/raw/ratings-stimulus_original.csv` | `05_combinatorial/output/` (`<run_name>/`, `runs_summary.csv`, `checks-vs-may.txt`, `tab:combinatorial-search`, `tab:combinatorial-reliability-sets`, `tab:combinatorial-item-frequency`, `tab:selected-model`) |

Steps 01, 02 and 03 are independent: each one reads only the data and the configuration file. Step 04 needs the candidate pool of step 05 for one of its checks, and step 05 uses the final priority of step 04 as its candidate pool.

## How to reproduce

0. The prepared data is in the repository. To rebuild it from the raw data, run `python phase2-2-item-reduction/data/prepare_data.py`.
1. Step 00 (Python ≥ 3.11 with `pandas`), from the repository root:

   ```bash
   python phase2-2-item-reduction/00-efa-screening/screen-efa-items.py
   python phase2-2-item-reduction/00-efa-screening/review-missing-data.py
   python phase2-2-item-reduction/00-efa-screening/build-screening-table.py
   ```
2. Open `instrument.Rproj` (at the repository root) in RStudio. All paths start from the repository root (package `here`). Install the recorded package versions with `renv::restore()`.
3. Steps 01–03: run `source("phase2-2-item-reduction/render_all.R")`, or knit each notebook in RStudio.
4. Step 04 (Python; `openpyxl` only for the extraction, which needs the spreadsheets in `Gdrive_files/`):

   ```bash
   python phase2-2-item-reduction/04_ranking/extract_ranking_criteria.py   # only if the spreadsheets change
   python phase2-2-item-reduction/04_ranking/build_ranking_table.py
   python phase2-2-item-reduction/04_ranking/build-irt-ranking-table.py
   ```
5. Step 05: in the RStudio console run `source("phase2-2-item-reduction/05_combinatorial/run-all-thresholds.R")` (about 1.5 h; runs already done are skipped), then `python phase2-2-item-reduction/05_combinatorial/build_runs_table.py`.
6. Commit the updated `.html` reports, `output/` folders and scripts together. If a notebook is open in RStudio, reload it before knitting, so that RStudio does not save an older version over the file.

### R packages

`here`, `rmarkdown`, `knitr`, `dplyr`, `tidyr`, `psych`, `lavaan`, `mirt`, `lattice`, `gridExtra`; step 05 also `readr`, `purrr`, `stringr`, `tibble`. Versions used (R 4.5.2, Windows 11) are listed in `item-reduction-context.md` and in each step's `sessionInfo.txt`.

### Python packages

`pandas`; `openpyxl` (reading the spreadsheets in steps 00, 04 and 05). Python ≥ 3.11.

## Decisions recorded on 2026-10-15

- **Data.** Steps 01 and 02 use the **low-frequency collapsed** ratings: answer options chosen by ≤ 2.5% of participants are merged into the neighbouring category with more answers. The reliability values in the first draft of the paper table were computed on uncollapsed data, so the new α values differ slightly (mostly < 0.01). Steps 03 and 05 use the **uncollapsed** data (decisions of 2026-10-21, below).
- **Versions C and D.** Model_1 uses **P089**, the item with the highest factor loading. Models 2 and 3 use **P022A**. The April 2026 reliability run had P022A in Model_1 by mistake.
- **Tool labels.** The old collapsed data file had Tableau ↔ Power BI and Gephi ↔ JMP swapped. The prepared file is rebuilt from the original data, with the labels checked against the survey export (see [data](data/README.md#correction-of-the-tool-labels-2026-10-15)). Overall results do not change; per-tool results do.
- **Version E.** It is a different 4-factor model, so it has only Model_1, computed on all 4 factors. It has no Model_2 or Model_3. Model_1 has the five items with the highest loadings on each factor of the 4-factor solution, except on the reliability factor, where P014 was used instead of P103 (reason not recorded).

## Later decisions (2026-10-18 to 2026-10-26)

- **Baseline of 49 items** (2026-10-18). The phase starts after the screening of step 00, not with the 65 items of the EFA.
- **Missing-data review** (2026-10-21/22). Items with more than 3% missing answers in a system were excluded only with a weak loading, redundancy or feature-specific content (see [step 00](00-efa-screening/README.md)).
- **Fit rule** (2026-10-20). Manual and automated testing use the same rule: (CFI or TLI ≥ 0.95) and (SRMR ≤ 0.08 or RMSEA ≤ 0.06).
- **Single ranking in the paper** (2026-10-20). The triangulation table shows the final priority, revised when the combinatorial candidate pool was chosen; Model_3 of Versions A–D was built from the first priority.
- **IRT on uncollapsed data** (2026-10-21). The trace plots must match the April plots that were scored.
- **Exhaustive combinatorial search, stopping at 0.72** (2026-10-21). The May runs at 0.70–0.72 were cut at 1,000 models; the repeated runs reproduce May exactly except at 0.72.
- **Single-group CFA in the combinatorial search** (2026-10-20). Kept as in May and stated in the paper as a broad filter; the selected model is evaluated multi-group in the validation phase.

## Relation to the old files

| Old (hand-run, `phase2-2-itemreduction/` and `Gdrive_files/Item Reduction/`) | New |
|---|---|
| `02-reliability/Reproduce2-reliability.Rmd`, run once per version by commenting item lists in and out | `01_reliability/01_reliability.Rmd` (all versions in one run) |
| `Notebooks/Reproduce3_Notebooks/Reproduce3-MG-CFA-Model_1/2/3.Rmd` | `02_cfa/02_cfa.Rmd` |
| `Notebooks/Reproduce7_Notebooks/Reproduce7-IRT-graded.Rmd`, run once per factor on the uncollapsed `Data/Reproduce7_Data/ratings-stimulus_<factor>.csv` | `03_irt/03_irt.Rmd` (all factors in one run, uncollapsed data) |
| Item lists copied in each notebook and in the Excel tab *Models and Versions of Items* | `item_versions_config.R` |
| `Data/Reproduce2_Data/ratings-stimulus.csv` (and identical copies in Reproduce3/4), with wrong tool labels | `data/prepared/ratings-stimulus_collapsed.csv` (same values, corrected labels), rebuilt by `data/prepare_data.py` from `data/raw/ratings-stimulus_original.csv` |
| `Ranking revisited considering reliabitiy- loadings- and IRT.xlsx` (tab *3 fators merged*) | `04_ranking/ranking_criteria.csv` and the tables in `04_ranking/output/` |
| `Reliability/260429V?_Reliability.xlsx`, `ModelFit-CFA/260429CompleteModelFit.xlsx` (built by hand in Google Sheets) | `01_reliability/output/reliability_summary_wide.csv`, `02_cfa/output/fit_summary_wide.csv` |
| `Notebooks/Reproduce8_Notebooks/Reproduce8-reliability_CFA_exploration.Rmd` and the May run folders in `Gdrive_files/Item Reduction/Reliability_CFA_Analysis/` | `05_combinatorial/05_combinatorial.Rmd`, `run-all-thresholds.R` and the run folders in `05_combinatorial/output/` |
| EFA workbook and item history (`Gdrive_files/Exploratory Factor Analysis - temp/`) | `00-efa-screening/` |

The trace of the old *Results Summary* table, and the errors found in it, are documented in `Gdrive_files/Item Reduction/Results_Summary_PROVENANCE.md`.
