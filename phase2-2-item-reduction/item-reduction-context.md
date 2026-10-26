# Item reduction (phase 2.2): context document

Context for the project that brings together all the development phases of the **UX in visual analytics scale (UXVis)**. This document covers **phase 2.2, item reduction**: its goal, data, pipeline, decisions, reference results, software versions and open points. Validation is a separate phase (`phase3-validation/`); this document gives only its link to item reduction.

Repository: `GitInstrument/phase2-2-item-reduction/` (local path on Eliane's computer: `C:\Users\Eliane\My_codes\GitInstrument\`). State as of **2026-10-26**.

---

## 1. Goal

Reduce the item pool of the scale to a short instrument with good reliability, a stable factor structure and conceptual coherence.

- **From:** the 3-factor EFA solution with **65 items**.
- **Step 00 screening:** it keeps **49 items**: 19 Task_cognition, 14 System, 16 Visualization.
- **End:** a **13-item, 3-factor instrument**:

| Factor (validation name) | Items |
|---|---|
| Visualization | P022A, P067, P089, P097, P098, P106 |
| Task_cognition (*Cognitive value*) | P027, P060, P064, P301 |
| System (*Intuitiveness*) | P026, P088, P4026A |

This is model `3_Factor_A` in `phase3-validation/06_alternative-structures`. Validation fits it again on an independent sample.

The phase rebuilt and documented work that had first been done by hand in March–May 2026, with notebooks, spreadsheets and Google Sheets. Every number in the paper should now come from a script in the repository, or from a documented manual decision.

---

## 2. Data

| File | Content |
|---|---|
| `data/raw/ratings-stimulus_original.csv` | 65 items rated by **506 participants** on a −3 … +3 scale, **uncollapsed**. MD5 `2e967d9c37a6f2f1d2d7e79505a3dbb3` |
| `data/prepared/ratings-stimulus_collapsed.csv` | The same ratings with **rare answer options collapsed**: an option chosen by ≤ 2.5% of answers is merged into the neighbouring option with more answers. There are 111 merges, all at the negative end. MD5 `eb83954b17ac6ef2149f63f4f7c0c572`. Built by `data/prepare_data.py` |
| `data/codebook/items.csv` | Item code, wording, factor in the 3- and 4-factor structures |

- **Tools (stimulus):** Gephi 104, Power BI 102, Qlik 101, Tableau 100, JMP 99.
- **Attention checks** P901 and P902 were removed earlier and are not in the data.
- **Tool labels:** the old collapsed file used in April 2026 had Tableau ↔ Power BI and Gephi ↔ JMP swapped. The corrected file was checked against the survey export: all 506 labels agree.
  - Overall results are not affected.
  - Results per tool are affected.
- **Which data each step uses:**

| Data | Steps |
|---|---|
| Collapsed | 01 reliability, 02 CFA; the EFA loadings (step 00 and the ranking) |
| Uncollapsed | 03 IRT, as in the April plots that were scored; 05 combinatorial search, as in the May runs; the α if dropped of the ranking |

---

## 3. Pipeline (steps)

All item lists are in **one file**, `item_versions_config.R`, which the R notebooks read. Python scripts run from the repository root. R notebooks are knitted in RStudio from `instrument.Rproj` (package `here`).

| Step | Scripts | What it does | Main outputs (paper label) |
|---|---|---|---|
| 00 EFA screening | `screen-efa-items.py`, `review-missing-data.py`, `build-screening-table.py` | 65 → 49 items: cross-loading rule, and missing-data review | `table-items-after-screening.tex` (`tab:items-after-screening`), `table-screening-decisions.tex` (`tab:screening-decisions`), `missing-data-review.xlsx` |
| Data | `data/prepare_data.py` | Checks the tool labels; collapses rare options | `data/prepared/` |
| 01 Reliability | `01_reliability.Rmd` | α and ω for every factor, model and version; α if item dropped | `reliability-summary-table.tex` (`tab:reliability-summary`), `item_drop_table.tex` (`tab:item-drop`) |
| 02 Multi-group CFA | `02_cfa.Rmd` | Multi-group CFA by tool (ML, FIML, collapsed), measurement invariance | `fit-summary-table.tex` (`tab:fit-summary`) |
| 03 IRT | `03_irt.Rmd` | Graded response model per factor (`mirt`), trace plots | `irt_traces_<factor>.pdf/png` (no title), item parameters |
| 04 Ranking | `extract_ranking_criteria.py`, `build_ranking_table.py`, `build-irt-ranking-table.py` | Documents the multi-criteria triangulation ranking. It does not compute it: the ranking was a team decision | `ranking_table_main.tex` (`tab:triangulation-ranking`), `irt-ranking-table.tex` (`tab:IRT-ranking`), `ranking_table_full.csv` |
| 05 Combinatorial | `generate_combinations.py`, `05_combinatorial.Rmd`, `run-all-thresholds.R`, `build_runs_table.py` | Automated search: reliability prefilter, then a CFA for every combination | `table_combinatorial_runs.tex` (`tab:combinatorial-search`), `table_final_reliability_sets.tex` (`tab:combinatorial-reliability-sets`), `table_final_item_frequency.tex` (`tab:combinatorial-item-frequency`), `table-selected-model.tex` (`tab:selected-model`) |

**Order to reproduce:**
1. Run `00` (Python).
2. Run `data/prepare_data.py` (only if the raw data change).
3. Knit `01`, `02` and `03` (independent of each other).
4. Run `04` (Python).
5. Run `05/run-all-thresholds.R`, then `05/build_runs_table.py`.

Each step has a README with inputs, outputs and the step-by-step.

---

## 4. Decisions

### 4.1 Screening, 65 → 49 items (step 00)

1. **Cross-loading:** 11 items were excluded because their second-highest loading was > 0.32 in the 3-factor EFA (collapsed):
   - Task_cognition: P092, P095, P209, P213, P102, P201;
   - System: P207, P06;
   - Visualization: P105, P104, P103.

   The item history says "0.25", but 0.32 is the cut-off that reproduces the selection.
2. **Missing-data review:** 5 items were excluded: P049, P031, P212, P09, P305.
   - **Not** a rule on missingness alone (team meeting of 2026-03-19). Little's test rejected MCAR in every tool.
   - **Rule (compiled on 2026-10-22):** items with > 3% missing answers in at least one tool, and not already excluded for cross-loading, were reviewed. An item was excluded if it also had at least one of:
     1. a weak primary loading (λ < 0.40): P031 (0.27), P212 (0.39);
     2. redundancy: P049, with P041;
     3. content tied to a feature that only some tools offer, or to a particular kind of data (non-applicability): P031 latency, P212 overview/detail, P09 sharing results, P305 focusing on the information of interest.
   - **Retained** because none applied: P067 (trial and error), P203 (error recovery) and P096 ("link information across visualizations", read as a general characteristic of the system).
   - `review-missing-data.py` confirms that the rule reproduces every decision.
3. **A low primary loading alone was not a reason for exclusion:** P033 (0.32) and P045A (0.31) were kept.
4. **Timeline:**
   - EFA run of 2026-03-18;
   - missing-data discussion on 2026-03-19;
   - 3-factor solution chosen by 2026-03-31;
   - exclusions made between 2026-03-31 and 2026-04-08.

### 4.2 Versions and models (steps 01–02, manual testing)

- **Versions A, B, B2, C and D** use the 3-factor structure, with the **49 screened items as baseline**:

| Version | Items per factor |
|---|---|
| A | Model_1 = the 49 items, identical to the baseline; Models 2–3: 5 |
| B | 5 |
| B2 | 5 (as B, with P072 instead of P027 in Model_3 task_cognition) |
| C | 4 |
| D | 3 |

- **Models:**
  - Model_1 = highest loadings;
  - Model_2 = IRT rank;
  - Model_3 = triangulated priority (first, April version).
- **Versions C and D, Model_1:** use **P089**, the highest loading (decision of 2026-10-15). The April run used P022A by mistake.
- **Version E** uses the **4-factor** structure:
  - baseline of 61 items (`full_4_factors`); P012, P041, P201 and P212 are left out;
  - only Model_1, with 5 items per factor = the 5 highest loadings in the 4-factor solution (collapsed);
  - **exception:** on the 4th (*reliability*) factor, P014 (λ 0.30) was used instead of P103 (0.34). The reason is not recorded.
- **CFA specification (manual testing):** multi-group by tool, ML (lavaan default), `missing = "fiml"`, collapsed data.
- **Fit rule** (used in both manual and automated testing): **(CFI or TLI ≥ 0.95) and (SRMR ≤ 0.08 or RMSEA ≤ 0.06)**.

### 4.3 Multi-criteria triangulation ranking (step 04)

- **Three criteria** rank the 49 items within each factor:
  - **reliability:** α of the factor if the item is dropped. Computed within the 65-item EFA factors, on uncollapsed data; lowest first;
  - **factor loading:** λ, collapsed EFA; highest first;
  - **IRT:** a rubric of 0–3 per trace plot for monotonicity, discrimination, neutral-point centering and latent-trace coverage, plus a rank agreed by the team.
- **The IRT rank is not the sum of the scores.** Spearman correlation between rank and total: Task_cognition 0.43, System 0.81, Visualization 0.72.
- **The IRT scores were given on the uncollapsed plots of 2026-04-12.** `03_irt.Rmd` now uses uncollapsed data by default and reproduces those plots (checked visually on 2026-10-21; only the colours and the panel order differ).
- **The priority is a team judgement**, recorded in spreadsheets. **The paper shows a single ranking: the final priority.**
  - It was revised in May 2026 by Petra Isenberg and Anne-Flore Cabouat when they chose the combinatorial candidate pool.
  - Changes from April: System P074 in at 3rd, P024 out; Visualization P05 (6th) and P067 (7th) added.
  - The April priority is kept in `ranking_criteria.csv` (column `priority`).
  - Model_3 of Versions A–D was built from the April priority. A footnote in the paper says this.
- **System loading order (collapsed EFA):** P088 0.892 > P026 0.884 > P214 0.870 > P4026A 0.793 > P074 0.727 > P086 0.726.

### 4.4 Automated combinatorial search (step 05)

- **Candidate pool:** the top of the final priority.

| Factor | Pool |
|---|---|
| Visualization (priorities 1–7, 8 items) | P022A, P05, P067, P068, P089, P097, P098, P106 |
| Task_cognition (priorities 1–5) | P027, P060, P062, P064, P301 |
| System (priorities 1–5) | P214, P088, P074, P4026A, P026 |

- **Reliability prefilter:** α **or** ω ≥ threshold.
- **CFA specification:** **single-group** (all tools pooled), **MLR**, FIML, **uncollapsed** data. This differs from the manual testing.
  - It was accidental in May: the notebook grouped by a column `SYSTEM` that does not exist.
  - It is kept and stated in the paper as a broad filter. The selected model is evaluated multi-group in validation.
- **Thresholds:**
  - first 6/3/3 items (Vis/Task/Sys) at 0.72–0.79, then 6/4/3 at 0.78–0.79;
  - **0.80** cannot form any model (derived row);
  - the search **stops at 0.72**, the highest threshold at which subsets with the cognitive items P062/P064 reach approved models.
- **May 2026 runs at 0.70–0.72 were cut at 1,000 models.** All runs were repeated **exhaustively** on 2026-10-21. They reproduce May exactly except at 0.72 (now 1,960 fitted, 855 approved).
- **Ranking of approved models:** by CFI, with ties broken by TLI, RMSEA, SRMR and minimum reliability. All 118 approved models are admissible. The final model was chosen by balancing fit, reliability and conceptual coherence.

### 4.5 Conventions

- New files use hyphens (`-`), not underscores. Older files keep their names.
- No bold in tables.
- Generated tables carry "do not edit by hand"; change the script instead.
- Supplementary-material pointers in the paper use `\suppmat{}` (blue).

---

## 5. Reference results

Use these to check a re-run.

**Step 00:**
- 65 → 49 items (19 / 14 / 16);
- 11 cross-loading + 5 missing-data exclusions;
- `check.txt`: "Result matches Version_A Model_1" and "matches screened_3_factors".

**Step 01, Cronbach's α (collapsed data):**

| Factor | Model | A | B | B2 | C | D | E |
|---|---|---|---|---|---|---|---|
| System | Baseline | 0.929 | 0.929 | 0.929 | 0.929 | 0.929 | 0.933 |
| | Model 1 | 0.929 | 0.868 | 0.868 | 0.847 | 0.821 | 0.865 |
| | Model 2 | 0.863 | 0.863 | 0.863 | 0.826 | 0.784 | – |
| | Model 3 | 0.863 | 0.863 | 0.863 | 0.826 | 0.784 | – |
| Task_cognition | Baseline | 0.935 | 0.935 | 0.935 | 0.935 | 0.935 | 0.936 |
| | Model 1 | 0.935 | 0.814 | 0.814 | 0.764 | 0.711 | 0.814 |
| | Model 2 | 0.800 | 0.798 | 0.798 | 0.755 | 0.690 | – |
| | Model 3 | 0.806 | 0.806 | 0.806 | 0.768 | 0.720 | – |
| Visualization | Baseline | 0.894 | 0.894 | 0.894 | 0.894 | 0.894 | 0.901 |
| | Model 1 | 0.894 | 0.726 | 0.726 | 0.659 | 0.623 | 0.722 |
| | Model 2 | 0.761 | 0.761 | 0.761 | 0.737 | 0.689 | – |
| | Model 3 | 0.774 | 0.777 | 0.777 | 0.732 | 0.670 | – |
| Reliability (E) | Baseline / Model 1 | – | – | – | – | – | 0.803 / 0.748 |

**Step 02, multi-group CFA fit (CFI / TLI / RMSEA / SRMR):**
- **Baseline:**

| | CFI | TLI | RMSEA | SRMR |
|---|---|---|---|---|
| A–D (49 items) | 0.724 | 0.711 | 0.088 | 0.081 |
| E (61 items) | 0.661 | 0.648 | 0.089 | 0.082 |

- **Best manual model, Version D Model_2:**
  - CFI 0.955, TLI 0.932, RMSEA 0.077, SRMR 0.052;
  - meets the fit rule, but α is below 0.70 for Task_cognition (0.690) and Visualization (0.689);
  - the vis–Task latent correlation is > 1 (1.003), so the solution is inadmissible.
- **No manual model reaches RMSEA ≤ 0.06** (lowest 0.077).
- **Degrees of freedom:** Version E baseline 8,815, Model_1 820 (5 groups).

**Step 03, IRT (uncollapsed):**

| Factor | Items | N used | M2 | df | RMSEA | SRMSR | CFI |
|---|---|---|---|---|---|---|---|
| Task_cognition | 19 | 483 | 220.6 | 75 | 0.063 | 0.054 | 0.634 |
| System | 14 | 473 | 23.4 | 7 | 0.070 | 0.044 | 0.635 |
| Visualization | 16 | 468 | 59.4 | 38 | 0.035 | 0.056 | 0.800 |

**Step 04:**
- `checks.txt`: all ranks follow their values;
- reduced models = top 5 of each criterion. The one NOTE: P022A and P089 are tied at priority 2 in Visualization;
- the candidate pool = top of the final priority in every factor.

**Step 05, exhaustive runs of 2026-10-21:**

| Items (T/V/S) | Threshold | Subsets passing (T/V/S) | Models fitted | Approved |
|---|---|---|---|---|
| 3/6/3 | 0.79 | 1/2/8 | 16 | 16 |
| 3/6/3 | 0.78 | 1/8/9 | 72 | 67 |
| 3/6/3 | 0.77 | 1/22/10 | 220 | 197 |
| 3/6/3 | 0.76–0.74 | 1/28/10 | 280 | 244 |
| 3/6/3 | 0.73 | 2/28/10 | 560 | 244 |
| 3/6/3 | 0.72 | 7/28/10 | 1,960 | 855 |
| 4/6/3 | 0.79 | 1/2/8 | 16 | 13 |
| **4/6/3** | **0.78** | **2/8/9** | **144** | **118** |

- From 0.73 up, every approved 3/6/3 model uses Task_cognition P027-P060-P301.
- Cognitive subsets (with P062 or P064) have α 0.70–0.72 and ω 0.72–0.73. They reach approved models only at 0.72: 611 of 855, all with P062.
- **Final run (0.78, 4/6/3):** the 118 approved models have CFI 0.950–0.970, TLI 0.937–0.963, RMSEA 0.046–0.062 and SRMR 0.033–0.043, with α or ω ≥ 0.784 in every scale.
- **Selected model: rank 23 of 118:**
  - CFI 0.964, TLI 0.955, RMSEA 0.052, SRMR 0.038;
  - α (ω): Task_cognition 0.769 (0.784), Visualization 0.784 (0.790), System 0.812 (0.817).
- **Alternative with P214** instead of P088 in System (P026, P214, P4026A): rank 2, CFI 0.970, TLI 0.963, RMSEA 0.046, SRMR 0.035.
- `checks-vs-may.txt`: every run identical to May, except 0.72 (May was cut at 1,000).

---

## 6. Software

**R** (from each step's `sessionInfo.txt`):
- R **4.5.2** (2025-10-31 ucrt), Windows 11 x64, RStudio. Package versions are also recorded in `renv.lock` at the repository root (`renv::restore()`).

| Package | Version | Steps |
|---|---|---|
| here | 1.0.2 | all |
| psych | 2.6.1 | 01, 05 |
| lavaan | 0.6-21 | 02, 03, 05 |
| mirt | 1.48 | 03 |
| dplyr | 1.2.0 | all |
| tidyr | 1.3.2 | 01, 02, 05 |
| lattice | 0.22-7 | 03 |
| gridExtra | 2.3 | 03 |
| readr | 2.2.0 | 05 |
| purrr | 1.2.1 | 05 |
| stringr | 1.6.0 | 05 |
| tibble | 3.3.1 | 05 |
| knitr | 1.51 | 05 |
| rmarkdown | 2.30 | all |

**Python:**
- Python ≥ 3.11 with `pandas`, and `openpyxl` for reading the spreadsheets: steps 00, data, 04 and 05.
- Exact versions are **not recorded** yet (see pending).

**Combinatorial run times** (on Eliane's computer):
- about 1.5 s per CFA model;
- the 0.72 run (1,960 models) takes 49 min;
- all runs together take about 1.5 h.

---

## 7. Relation to other phases

- **Before (EFA phase, phase 2.1):**
  - the 3-factor EFA (2026-03-18, polychoric, principal axis, collapsed 2.5%) and the item history live outside the repository for now: `UXVis/Replication…` and `Gdrive_files/Exploratory Factor Analysis - temp/`;
  - step 00 copies the loadings it needs (`00-efa-screening/input/efa-pa-3-factors-agg.csv`, MD5 `2f937169c9d566d693c9ba1c2a43ef53`);
  - when the EFA phase enters the repository, these inputs should point there.
- **After (validation, `phase3-validation/`):**
  - new sample (students, user forums, Prolific), tools Power BI, Tableau, JMP, Excel and Data Studio;
  - the 13-item model is `3_Factor_A`;
  - `05_cfa-multigroup` fits it multi-group with invariance tests; `06_alternative-structures` compares 11 structures, among them `4_Factor_C`;
  - same CFA specification as the manual testing: multi-group, ML, FIML, collapsed.
- **Item names in validation:** task_cognition → *Cognitive value*; system → *Intuitiveness*.

---

## 8. Pending

**Data and decisions to confirm with the team:**
- Confirm with Petra and Anne-Flore the missing-data rule compiled on 2026-10-22, especially criterion 3 for P09 and P305, and P096 being retained.
- Find out why P014 replaced P103 in Version E Model_1 (reliability factor), and why P212 is left out of the Version E baseline.
- P049: confirm whether it was removed for redundancy with P041 (meeting of 2025-11-25) before the EFA, or in the missing-data review.
- Version E baseline (61 items) still contains 13 items excluded in the 3-factor screening. Decide whether that is intended.
- System loading order quoted in the paper ("#2 P088, #5 P086, #6 P026"): check which ranking it refers to (see §4.3).
- P088 wording: the paper uses "I could easily understand the system"; the codebook has "I found the system simple to understand".
- P305 wording in the codebook has "informtaion": check whether the typo was in the survey.

**Repository:**
- Commit to Git after each change. Several files were reverted on the computer on 2026-10-20 and 21, and the RStudio open-tab problem also caused reverts.
- The phase `README.md` is out of date on three points:
  - step 03 now uses uncollapsed data by default;
  - step 05 now has `run-all-thresholds.R` and exhaustive runs;
  - step 00 now has the missing-data review.
- Record Python package versions (`requirements.txt`).
- Move the EFA inputs into the repository when the EFA phase is documented.

**Paper (Overleaf):**
- Replace stale table copies with the generated `.tex` files:
  - `ranking_table_main.tex`: the Overleaf version still shows P024;
  - `table_combinatorial_runs.tex`, `fit-summary-table.tex`, `irt-ranking-table.tex`, `table-screening-decisions.tex`.
- Section texts revised in this work:
  - 1.1 missing data;
  - triangulation, with a single final ranking;
  - manual testing, with the "or" fit rule and the Model_3 footnote;
  - combinatorial search: pool, single-group note, α vs ω for the cognitive subsets, exhaustive runs;
  - selection: ranking by CFI, rank 23, conceptual reasons.

  Check that the reasons given for not choosing higher-ranked models (P068, P214) are the ones the team actually gave.
