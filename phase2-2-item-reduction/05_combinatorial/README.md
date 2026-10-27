# 05 Automated combinatorial reduction: history of the May 2026 runs

**Notebook:** [`05_combinatorial.Rmd`](05_combinatorial.Rmd) · **Report (final run):** [`05_combinatorial.html`](https://uxinva.github.io/instrument/phase2-2-item-reduction/05_combinatorial/05_combinatorial.html) · **Scripts:** [`generate_combinations.py`](generate_combinations.py), [`run-all-thresholds.R`](run-all-thresholds.R), [`build_runs_table.py`](build_runs_table.py)

This folder records **what was run** for the paper section "Automated Combinatorial Reduction Pipeline" (which files, settings and results the text is based on), and has a **recovered, runnable copy of the pipeline**. The numbers below were recomputed on 2026-10-16 from the output files of the May runs.

## How to run the recovered pipeline

| Step | File | What it does |
|---|---|---|
| 1 (Python) | [`generate_combinations.py`](generate_combinations.py) | Reads `input/candidate_pool.csv` and writes `input/combinations_<vis>-<task>-<sys>.csv`. Tested on 2026-10-16: the 6/3/3 and 6/4/3 files are **identical** to the May files |
| 2–3 (R) | [`05_combinatorial.Rmd`](05_combinatorial.Rmd) | Reliability prefilter, CFA for every combination, ranking. Writes CSVs to `output/<run_name>/` |
| All runs (R) | [`run-all-thresholds.R`](run-all-thresholds.R) | Runs `05_combinatorial.Rmd` for every threshold, **with no limit on the number of models**: 6/3/3 at 0.79–0.72 and 6/4/3 at 0.79–0.78. Runs already done are skipped, so the script can be stopped and restarted. It logs the time of each run in `output/run-all-thresholds-log.csv`. About 1.5 h in total |
| Summary (Python) | [`build_runs_table.py`](build_runs_table.py) | Reads the run folders (default: the repository runs in `output/rel0XX_…/`; `--may` for the May folders) and writes to `output/`: `runs_summary.csv` and `table_combinatorial_runs.tex` (all runs); `final_reliability_sets.csv` / `table_final_reliability_sets.tex` and `final_item_frequency.csv` / `table_final_item_frequency.tex` (final run, `--final`). Thresholds that were not run, such as 0.80, are derived from the subset reliabilities when no model can be formed; this is marked in the table |

```bash
python phase2-2-item-reduction/05_combinatorial/generate_combinations.py        # 6/4/3 (default); "6 3 3" for the first runs
```
To repeat the whole search (decision of 2026-10-21, so that every run in the paper is exhaustive):

```r
source("phase2-2-item-reduction/05_combinatorial/run-all-thresholds.R")
```
```bash
python phase2-2-item-reduction/05_combinatorial/build_runs_table.py
```
The summary then uses the repository runs, and `output/checks-vs-may.txt` compares each one with the May run of the same threshold. They should be identical, except the 0.72 run, which May cut at 1,000 models. The search stops at 0.72; the May runs at 0.70 and 0.71, also cut at 1,000 models, are not repeated.

To run a single configuration, knit `05_combinatorial.Rmd` in RStudio. With its defaults, it repeats the final May run: threshold 0.78, 6/4/3, single group, uncollapsed data. At the end it compares its approved models with the May file; the expected result is 144 candidate models and 118 approved. Use **Knit with Parameters…** to change the threshold, the data (`data/prepared/ratings-stimulus_collapsed.csv`), the grouping (`group_col: "stimulus"` for multigroup) or `run_name`.

The analysis code is the May code, unchanged. Only the paths, the parameters and two settings changed:
- `group_col: ""` makes the single-group CFA explicit;
- `max_models: 0` means no limit.

The output files are the same as in May:
- `combinations_of_items_by_scale_with_reliability.csv`;
- `tested_reliability_sets.csv`;
- `kept_reliability_sets_for_cfa.csv`;
- `all_reliability_cfa_results.csv`;
- `passing_reliability_cfa_results.csv`;
- `top_100_reliability_cfa_results.csv`;
- `passing_reliability_cfa_model_syntax.txt`.

The run also writes `run_info.txt` and `sessionInfo.txt`.

Check of the reliability stage, done in Python without R: α recomputed for every set of the final run differs from the May values by at most 0.0005, which changes no pass/fail decision. ω (`psych::omega`) can only be checked in R.

## Runs of 2026-10-21

All runs were repeated in the repository with `run-all-thresholds.R`, with no limit on the number of models. Each run has its folder in `output/` and its HTML report. The final run (threshold 0.78, 4/6/3 items) was knitted directly from `05_combinatorial.Rmd` on 2026-10-18, so its report is the one next to the notebook.

| Items (Task / Vis / Sys) | Reliability threshold | Report |
|---|---|---|
| 3 / 6 / 3 | 0.79 | [report](https://uxinva.github.io/instrument/phase2-2-item-reduction/05_combinatorial/output/rel079_6-3-3_singlegroup_uncollapsed/rel079_6-3-3_singlegroup_uncollapsed.html) |
| 3 / 6 / 3 | 0.78 | [report](https://uxinva.github.io/instrument/phase2-2-item-reduction/05_combinatorial/output/rel078_6-3-3_singlegroup_uncollapsed/rel078_6-3-3_singlegroup_uncollapsed.html) |
| 3 / 6 / 3 | 0.77 | [report](https://uxinva.github.io/instrument/phase2-2-item-reduction/05_combinatorial/output/rel077_6-3-3_singlegroup_uncollapsed/rel077_6-3-3_singlegroup_uncollapsed.html) |
| 3 / 6 / 3 | 0.76 | [report](https://uxinva.github.io/instrument/phase2-2-item-reduction/05_combinatorial/output/rel076_6-3-3_singlegroup_uncollapsed/rel076_6-3-3_singlegroup_uncollapsed.html) |
| 3 / 6 / 3 | 0.75 | [report](https://uxinva.github.io/instrument/phase2-2-item-reduction/05_combinatorial/output/rel075_6-3-3_singlegroup_uncollapsed/rel075_6-3-3_singlegroup_uncollapsed.html) |
| 3 / 6 / 3 | 0.74 | [report](https://uxinva.github.io/instrument/phase2-2-item-reduction/05_combinatorial/output/rel074_6-3-3_singlegroup_uncollapsed/rel074_6-3-3_singlegroup_uncollapsed.html) |
| 3 / 6 / 3 | 0.73 | [report](https://uxinva.github.io/instrument/phase2-2-item-reduction/05_combinatorial/output/rel073_6-3-3_singlegroup_uncollapsed/rel073_6-3-3_singlegroup_uncollapsed.html) |
| 3 / 6 / 3 | 0.72 | [report](https://uxinva.github.io/instrument/phase2-2-item-reduction/05_combinatorial/output/rel072_6-3-3_singlegroup_uncollapsed/rel072_6-3-3_singlegroup_uncollapsed.html) |
| 4 / 6 / 3 | 0.79 | [report](https://uxinva.github.io/instrument/phase2-2-item-reduction/05_combinatorial/output/rel079_6-4-3_singlegroup_uncollapsed/rel079_6-4-3_singlegroup_uncollapsed.html) |
| 4 / 6 / 3 | 0.78 | [report](https://uxinva.github.io/instrument/phase2-2-item-reduction/05_combinatorial/05_combinatorial.html) (final run) |

The summary of the runs and the comparison with the May runs are in `output/runs_summary.csv` and `output/checks-vs-may.txt`.

## Appendix tables: step by step

| Appendix table | File | Made from |
|---|---|---|
| Search by threshold (subsets passing reliability, CFA models fitted, models passing model fit) | `output/table_combinatorial_runs.tex` | every run folder |
| Subsets passing reliability in the final run, with α and ω | `output/table_final_reliability_sets.tex` | `tested_reliability_sets.csv` of the final run |
| How often each item appears in the models passing model fit | `output/table_final_item_frequency.tex` | `passing_reliability_cfa_results.csv` of the final run |
| Selected 13-item instrument: items, wording, α/ω per scale, fit and rank, compared with the alternative that had P214 | `output/table-selected-model.tex` (data: `output/selected-model.csv`) | `input/selected-models.csv` (the models to show), `data/codebook/items.csv` and `passing_reliability_cfa_results.csv` of the final run |

**Step 1 – combinations (Python).** From the repository root, run `python phase2-2-item-reduction/05_combinatorial/generate_combinations.py 6 3 3` and `… generate_combinations.py 6 4 3`. Input: `input/candidate_pool.csv`. Output: `input/combinations_6-3-3.csv` and `input/combinations_6-4-3.csv`.

**Step 2 – one R run per threshold.** Knit `05_combinatorial.Rmd` with **Knit with Parameters…**, setting for each run:
- `combination_file`;
- `reliability_threshold`;
- `run_name`, a different one for each run, e.g. `rel079_6-3-3`.

The data file is `data/raw/ratings-stimulus_original.csv`, single group, as in May. Each run writes its folder `output/<run_name>/`, with `tested_reliability_sets.csv`, `all_reliability_cfa_results.csv`, `passing_reliability_cfa_results.csv` and `run_info.txt`, among others. The May runs are already in `Gdrive_files/Item Reduction/Reliability_CFA_Analysis/`, so this step is only needed to re-run them.

**Step 3 – summary and tables (Python).**
- For the May runs: `python phase2-2-item-reduction/05_combinatorial/build_runs_table.py`.
- For new runs: `python phase2-2-item-reduction/05_combinatorial/build_runs_table.py --runs phase2-2-item-reduction/05_combinatorial/output/rel*/ --final phase2-2-item-reduction/05_combinatorial/output/<final run_name>/`.

Output: the four tables above, `output/runs_summary.csv`, `output/final_reliability_sets.csv` and `output/final_item_frequency.csv`.

## Where the files are

| What | File |
|---|---|
| Candidate pool (stage 1 input) | `phase2-2-itemreduction/Data/Reproduce8_Data/models_list.csv`, the same content as `Gdrive_files/Item Reduction/handpicked_items_list_by_factor.csv` (and its copy in `Reliability_CFA_Analysis/`), handpicked by Petra Isenberg and Anne-Flore Cabouat |
| Stage 1: combinations (Python) | `…/Notebooks/Reproduce8_Notebooks/Reproduce8-reliability-filter-for-cfa_exploration.ipynb`. It writes `combinations_of_items_by_scale.csv` |
| Combinations, 6/3/3 runs | `Gdrive_files/Item Reduction/Reliability_CFA_Analysis/combinations_of_items_by_scale.csv` (48 sets) |
| Combinations, 6/4/3 runs | `phase2-2-itemreduction/Data/Reproduce8_Data/combinations_of_items_by_scale.csv` (43 sets) |
| Stages 2 and 3 (R) | `…/Notebooks/Reproduce8_Notebooks/Reproduce8-reliability_CFA_exploration.Rmd`. The copies in `phase2-2-itemreduction/` and `Gdrive_files/` are identical |
| Data | `phase2-2-itemreduction/Data/Reproduce8_Data/rating-data.csv`, identical to `data/raw/ratings-stimulus_original.csv` (**uncollapsed**) |
| Results, 3 task_cognition items | `Gdrive_files/Item Reduction/Reliability_CFA_Analysis/2605*Reliability0XXCFAExploration-100best/` (thresholds 0.70 … 0.79) |
| Results, 4 task_cognition items | `Gdrive_files/Item Reduction/Reliability_CFA_Analysis/4_factors_task_cognition/2605*Reliability078-4task…`, `…079-4task…` |
| Earlier attempts | `Reliability_CFA_Analysis/OLD/` (2026-05-02 and 05-04) |

Each results folder has:
- `tested_reliability_sets.csv`: every item set, with α, ω and pass/fail;
- `kept_reliability_sets_for_cfa.csv`: the sets that passed reliability;
- `all_reliability_cfa_results.csv`: every fitted model;
- `passing_reliability_cfa_results.csv`: the approved models;
- `top_100_…csv`: the 100 best models;
- `passing_…_model_syntax.txt`: the lavaan syntax of the approved models.

## Candidate pool

| Factor | Items in the pool | Items per set | Sets |
|---|---|---|---|
| Visualization | P022A, P05, P067, P068, P089, P097, P098, P106 (8) | 6 | C(8,6) = 28 |
| Task_cognition | P027, P060, P062, P064, P301 (5) | 3, then 4 | C(5,3) = 10, then C(5,4) = 5 |
| System | P214, P088, P074, P4026A, P026 (5) | 3 | C(5,3) = 10 |

## Settings actually used (from the notebook and the results)

- **Reliability rule:** a set passes if **α ≥ threshold or ω ≥ threshold**. Here ω is `psych::omega(nfactors = 1)` on the raw data, i.e. on Pearson correlations.
- **Fit rule:** a model passes if **(CFI ≥ 0.95 or TLI ≥ 0.95) and (SRMR ≤ 0.08 or RMSEA ≤ 0.06)**. Every set in the model must also pass the reliability rule, and the model must converge.
- **CFA:** `lavaan::cfa` with estimator **MLR**, `missing = "fiml"`, `std.lv = TRUE`.
- **One group, not multigroup.** The notebook asks for groups by a column `SYSTEM`. The data file has no such column (it is called `stimulus`), so the notebook silently fitted a single-group CFA. The degrees of freedom confirm it: 51 for 6/3/3 and 62 for 6/4/3, which is what a single-group model with a mean structure has.
- **Data:** uncollapsed. The α values in the results match `ratings-stimulus_original.csv` exactly. The tool labels play no role, because there is no grouping.
- **Limit of 1000 models:** `max_models = 1000` keeps only the first 1000 candidates. The cut is made **before** fitting: the candidate list is ordered by the ID of the visualization set, then task_cognition, then system, and only its first 1000 rows are fitted; the others are neither fitted nor saved. In the runs at 0.70–0.72 there were 1,960–2,800 candidates, so those runs were **not exhaustive**: the first 10 (0.70), 11 (0.71) and 14 (0.72) of the 28 visualization sets were fitted with all their combinations, plus part of the next one. `run-all-thresholds.R` repeats 0.72 without the limit. All runs from 0.73 up, including the final one, were exhaustive.

## The runs

The runs of 2026-10-21 (`run-all-thresholds.R`) reproduce every May run exactly (`output/checks-vs-may.txt`), except 0.72, which is now exhaustive. The full table is in [`output/runs_summary.csv`](output/runs_summary.csv), made by `build_runs_table.py`. Item sets are written as visualization / task_cognition / system.

| Threshold | Items | Sets passing reliability | Candidate models | Fitted | Approved | Task_cognition sets in approved models |
|---|---|---|---|---|---|---|
| 0.70 (May only) | 6/3/3 | 28/10/10 | 2,800 | 1,000 (cut) | 545 | 7 sets, including P062 and P064 |
| 0.71 (May only) | 6/3/3 | 28/9/10 | 2,520 | 1,000 (cut) | 538 | 7 sets |
| 0.72 (May) | 6/3/3 | 28/7/10 | 1,960 | 1,000 (cut) | 461 | 5 sets |
| **0.72 (2026-10-21, all)** | 6/3/3 | 28/7/10 | 1,960 | **all** | **855** | 5 sets: P027-P060-P301 (244), P027-P060-P062 (240), P027-P062-P301 (185), P060-P062-P301 (172), P062-P064-P301 (14) |
| 0.73–0.76 | 6/3/3 | 28/2–1/10 | 560–280 | all | 244 | only **P027-P060-P301** |
| 0.77 | 6/3/3 | 22/1/10 | 220 | all | 197 | only P027-P060-P301 |
| 0.78 | 6/3/3 | 8/1/9 | 72 | all | 67 | only P027-P060-P301 |
| 0.79 | 6/3/3 | 2/1/8 | 16 | all | 16 | only P027-P060-P301 |
| **0.78** | **6/4/3** | **8/2/9** | **144** | **all** | **118** | P027-P060-P062-P301 (55), P027-P060-P064-P301 (63) |
| 0.79 | 6/4/3 | 2/1/8 | 16 | all | 13 | P027-P060-P062-P301 |

In the final run (0.78, 6/4/3), the 118 approved models have:
- CFI 0.950–0.970, TLI 0.937–0.963, RMSEA 0.046–0.062, SRMR 0.033–0.043;
- minimum reliability per scale 0.784.

69 of the 118 have **TLI < 0.95** and pass on CFI. The TLI and CFI rule is an "or".

## Points to check in the paper text

1. **The 3-item task_cognition result is reversed in the text.** The text says the sets failed at thresholds ≥ 0.78 and that lowering the threshold to 0.72 gave approved but only functional sets. The results show the opposite:
   - From 0.73 up, the only 3-item task_cognition set that passed was **P027 (efficiency), P060 (enjoyment) and P301 (usefulness)**: the functional set without a cognitive item. It still gave approved models: 67 at 0.78 and 16 at 0.79.
   - The sets with cognitive items (P062 "explore my data", P064 "think deeply") have α 0.70–0.72 and ω 0.72–0.73. One of them (P060-P062-P064, ω 0.730) passes the prefilter at 0.73 but gives no approved model; they appear in approved models only at 0.72 (611 of 855, all with P062).
2. **The fit criteria.** Write them as "(CFI or TLI ≥ 0.95) and (SRMR ≤ 0.08 or RMSEA ≤ 0.06)". Most of the 118 models pass on CFI only.
3. **Reliability.** Write it as "α or ω ≥ 0.78". In one of the two task_cognition sets of the final run (P027-P060-P064-P301), α is 0.769 and ω is 0.784.
4. **Exhaustive.** This holds for the final run. In May it did not hold for the 0.70–0.72 runs because of the 1000-model limit; after `run-all-thresholds.R`, every run in the paper table (0.72–0.80) is exhaustive.
5. **Single-group CFA, MLR, uncollapsed data.** The rest of the phase uses multigroup CFA on collapsed data, so the text should say how this step differs.
6. **Origin of the candidate pool.** The pool was chosen by hand by Petra Isenberg and Anne-Flore Cabouat in May 2026 (`Gdrive_files/Item Reduction/handpicked_items_list_by_factor.csv`; discussion in `Historic of handpicked_items_list_by_factor.pdf`). It is the top of the **final priority** of the triangulation ranking (`Ranking revisited 2 - AfterHandpickedItemsbyAFandP- … .xlsx`; see `04_ranking/README.md`):
   - visualization = priorities 1–7. P05 and P067 were added, and P045A was removed for its low loading (.31);
   - task_cognition = priorities 1–5;
   - system = priorities 1–5. P074 replaced P024.

   `04_ranking/build_ranking_table.py` checks this. The same items appear in the Version B models (visualization: Models 1–3 without P045A; task_cognition: Model_3; system: Model_1).
