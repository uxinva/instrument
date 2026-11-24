# Step 04: Sources of the item pool and item flow

This step describes how the candidate items were produced from four sources and how many items remained at each stage: from the merged pool (95 items) to the 65 items of the exploratory survey (phase 2.1), the 49 items kept by the EFA screening (phase 2.2) and the 13 items of the validated scale (phase 3).

| Code | Source | How it was used |
|---|---|---|
| P0 | Experts' suggestions (Task 2 of [expert survey 1](../02_expert-survey-1/README.md)) | Answers coded into topic and concept; one item written per topic-concept |
| P1 | UEQ+ items of the 15 topics of Task 1 | Each item compared with P0: related, irrelevant, ignore or new concept/topic |
| P2 | Items of other standardized questionnaires (SUS, UEQ, AttrakDiff, SUMI, meCUE, PSSUQ, PREVis, BEAUVis, …) | Compared with P0+P1: include, maybe or exclude |
| P3 | Terms and excerpts extracted from the VA literature (systematic review) | Classified into the topic-concepts of P0+P1+P2 (first by an AI model, then reviewed) |
| P4 | Items added in the cognitive interviews | P40-26-A, P40-26-B (derived from P0-26) |
| P9 | Attention checks | P9-01, P9-02 (not counted as scale items) |

## Data

From [`../data/raw/`](../data/README.md), built by `data/prepare_item_sources.py` from the team Google Sheets "Items Historic" and "Task2SuggestedItemsAnalysis250127" (downloaded as .xlsx into `tmp-data/old-analysis/`): `item-history.csv`, `item-pool.csv`, `source-p0-suggestions.csv`, `source-p1-ueqplus.csv`, `source-p2-scales.csv`, `source-p3-literature.csv`, `concept-occurrences.csv`. The texts of the scale items, the paper excerpts, the expert suggestions and the expert comments are not copied.

The last two stages are read from files of the other phases: `phase2-2-item-reduction/00-efa-screening/output/efa-screening-items.csv` and `items-after-screening.csv` (49 items, with the EFA loadings and the screening decisions) and `phase3-validation/data/codebook/items.csv` (13 items). Codes are matched without hyphens (P0-26 = P026, P40-26-A = P4026A). The shared code is in `item_tracking.py`.

## Run

From the repository root (step 03 first, for the check):

```
python phase1-item-development/data/prepare_item_sources.py     # only if the spreadsheets change
python phase1-item-development/04_item-flow/item_flow.py --check
python phase1-item-development/04_item-flow/item_history_page.py   # the HTML page of the item histories
```

`--check` compares the number of scale items per stage with the counts recorded from "Items Historic" on 2026-11-17 (and 49 and 13 for the last two stages), and the 18 items removed after expert survey 2 with the output of step 03.

## Outputs (`output/`)

| File | Content |
|---|---|
| `sources-summary.csv` | Per source: material reviewed, classification counts, items in the pool |
| `source-p0-by-topic.csv` | P0: coded suggestions per topic and their outcome (item, optional item, removed) |
| `source-p2-by-scale.csv` | P2: items reviewed per questionnaire and their classification |
| `source-p3-by-topic.csv` | P3: literature terms per final topic |
| `concept-coverage.csv` | Topic-concepts: occurrences in P0–P3 and items in the pool |
| `item-flow.csv` | Items per stage and source |
| `item-flow-changes.csv` | Items removed and added between consecutive stages, number reworded, the team's labels |
| `items-by-topic.csv` | Items per topic in the pool, after expert survey 2, in the exploratory survey, after the screening and in the validated scale |
| `item-trajectory.csv` | One row per item: source, topic, concept, presence at each of the 10 stages, first and last stage, expert survey 2 statistics, EFA loading, screening decision, validation factor |
| `final-items.csv` | The 13 items of the validated scale: team code, source, topic, concept, EFA factor and loading, expert survey 2 mode and mean, validation factor, short name, wording |
| `item-history.html` | Interactive page with the history of the 99 candidate items (search by code or words, filters by source and result, details per stage); written by `item_history_page.py`, self-contained, published on the repository site |
| `table-item-flow-changes.tex` | LaTeX table for the appendix (`tab:item-flow-changes`): for each stage, the items removed and added, the number reworded, and the reason (short reasons in `TRANSITION_REASONS` in `item_flow.py`) |
| `table-final-items-history.tex` | LaTeX table for the appendix (`tab:final-items-history`): the 13 items of the validated scale by factor, with source, topic and concept, first and final wording, expert survey 2 mean and EFA loading |
| `table-item-flow.tex` | LaTeX table of the item flow, with a column "Section" (`\ref` to the section of the paper that describes each stage; the labels are set in `STAGE_SECTIONS` at the top of `item_flow.py`, and the script prints the labels the paper must define) |

## Results

**Sources of the pool (95 items, 6 marked optional):**

- P0: 105 Task 2 answers coded into 136 topic-concept assignments (26 topics); 62 became items, 6 optional items, 68 were not used → **68 items**.
- P1: 62 UEQ+ items of the 15 scales; related to P0 29, irrelevant 20, ignore 8, new concept or topic 5 → **6 items**.
- P2: 472 items of 23 questionnaires; include 341, maybe 79, exclude 52 → **16 items**.
- P3: 2,072 literature terms classified into 90 topic-concepts → **5 items**.

**Item flow (scale items; attention checks not counted):**

| Stage | P0 | P1 | P2 | P3 | P4 | Total | Change |
|---|---|---|---|---|---|---|---|
| Merged pool P0+P1+P2+P3 | 68 | 6 | 16 | 5 | – | 95 | |
| After internal review (pilot) | 58 | 6 | 16 | 4 | – | 84 | 11 removed (incl. 5 optional) |
| After pilot (expert survey 2) | 58 | 6 | 15 | 4 | – | 83 | P2-10 removed |
| After expert survey 2 (interview round 1) | 46 | 5 | 11 | 3 | – | 65 | 18 removed (mode ≤ 3, step 03) |
| After interview round 1 | 45 | 5 | 12 | 3 | 2 | 67 | P0-87 removed; P2-09 back; P40-26-A, P40-26-B added |
| After interview round 2 | 43 | 5 | 11 | 3 | 2 | 64 | P0-31, P0-42, P2-08 removed |
| After round 3 (final revision) | 44 | 5 | 12 | 3 | 2 | 66 | P0-31, P2-08 back |
| Exploratory survey (Prolific, EFA) | 43 | 5 | 12 | 3 | 2 | 65 | P0-15 not shown (error) |
| After EFA screening (item reduction) | 37 | 1 | 7 | 2 | 2 | 49 | 11 cross-loadings > .32, 5 missing data |
| Selected scale (validation) | 10 | 1 | 0 | 1 | 1 | 13 | combinatorial search (phase 2.2) |

In the sheet "Items Historic", the stage columns of the interview rounds have their own item-code column; the script uses it, because in those columns the text of P3-05 is on the row of P3-03.

**The 13 items of the validated scale** come from P0 (10: P0-22-A, P0-26, P0-27, P0-60, P0-64, P0-67, P0-88, P0-89, P0-97, P0-98), P1 (P1-06), P3 (P3-01) and P4 (P40-26-A, derived from P0-26 in the interviews). No P2 item reached the final scale.

## Looking up one item

[`../item_lookup.py`](../item_lookup.py) shows the path of any item through the 10 stages (see the phase README).
