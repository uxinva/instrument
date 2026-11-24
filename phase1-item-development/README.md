# Phase 1: Item development

> **Status:** started on 2026-11-24. The steps are being documented.

This phase produces the **65 items** rated in the exploratory survey of [phase 2.1](../phase2-1-scale-development/README.md); step 04 follows the items further, to the 49 items of the item-reduction screening and the 13 items of the validated scale. It covers the generation of the item pool from the literature, two surveys with experts, the cognitive interviews and the item revisions made between these stages.

- **Data:** anonymised expert-survey data in [`data/`](data/README.md). Original exports (with names or e-mails) stay in `tmp-data/`, which is never committed (see `.gitignore`).

## Steps

From the repository root: `data/prepare_expert_data.py` and `data/prepare_item_sources.py` (only if the inputs change), then steps 02, 03 and 04 (step 04 checks its counts against the output of step 03).

| Step | Content | Status |
|---|---|---|
| [`01_literature-search/`](01_literature-search/README.md) | Keyword search in the full texts of IEEE VIS papers (GROBID XML) and word tree of "experience" (Python) | To be documented |
| [`02_expert-survey-1/`](02_expert-survey-1/README.md) | First expert survey and its pilot: relevance of 15 UEQ+ topics, Kendall's W with stepwise exclusion, the 10 relevant topics (mean ≥ 4), Task 2 answers (Python) | Reproduces the 2025 slides and spreadsheet (2026-11-24) |
| [`03_expert-survey-2/`](03_expert-survey-2/README.md) | Second expert survey: relevance of 83 statements, agreement (ICC), the 18 statements removed (mode ≤ 3) (Python) | Reproduces the 2025 spreadsheet (2026-11-24) |
| [`04_item-flow/`](04_item-flow/README.md) | Sources of the item pool (P0 experts, P1 UEQ+, P2 other questionnaires, P3 VA literature) and number of items at each stage, 95 → 65 (Python) | Reproduces the item history (2026-11-24) |

The steps follow the layout of the other phases: a `data/` folder and numbered steps `NN_step-name/`, each with a README, a notebook or scripts, the rendered report (R notebooks) and an `output/` folder.

## Looking up an item

The history of every candidate item can be browsed in the page [`04_item-flow/output/item-history.html`](https://uxinva.github.io/instrument/phase1-item-development/04_item-flow/output/item-history.html) (search by code or words; a link such as `item-history.html?q=P0-26` opens one item). The same information is available from the command line:

`item_lookup.py` finds items by code or by words and shows, for each one, its source, topic and concept, the stage at which it entered, whether it was present at each of the 10 stages (with the wording when it changed and the team's decision), the expert survey 2 ratings, the EFA loading and screening decision, and whether it is in the validated scale. Run from the repository root, after the two `data/prepare_*.py` scripts:

```
python phase1-item-development/item_lookup.py P0-26             # a code, with or without hyphens (P026)
python phase1-item-development/item_lookup.py "easy to use"     # words in the item texts, topics, concepts
python phase1-item-development/item_lookup.py trust --brief     # one line per item
python phase1-item-development/item_lookup.py --final           # the 13 items of the validated scale
python phase1-item-development/item_lookup.py --all --brief     # all candidate items
```
