# Phase 1 data

Anonymised data of the expert surveys and the item sources, built by two scripts. Their inputs stay in `../tmp-data/`, which is never committed:

- [`prepare_expert_data.py`](prepare_expert_data.py) reads the LimeSurvey exports (`results-survey<ID>.xlsx`, `limesurvey_survey_<ID>.lss`). They contain dates, Response IDs, a name or pseudonym field (pilot of survey 1) and free-text comments and suggestions; none of these are copied.
- [`prepare_item_sources.py`](prepare_item_sources.py) reads the team Google Sheets "Items Historic", "Task2SuggestedItemsAnalysis250127" and "Task 1 - CommentsAnalysis250127", downloaded as .xlsx into `../tmp-data/old-analysis/`. The texts of the scale items (P1, P2), the paper excerpts (P3), the expert suggestions and comments are not copied.

Only submitted survey responses are kept. Experts are coded in increasing Response ID order: `A01`… (survey 1), `AP1`… (pilot of survey 1), `E01`… (survey 2). The order is kept because the 2025 analysis of survey 2 computed the mode in that order (see [`../03_expert-survey-2/README.md`](../03_expert-survey-2/README.md)).

| Survey | LimeSurvey ID | Dates | Submitted |
|---|---|---|---|
| Pilot of expert survey 1 | 654491 | 8–12 Dec 2024 | 4 |
| Expert survey 1 (topic relevance; missing topics) | 654492 | 16–23 Jan 2025 | 37 |
| Expert survey 2 (statement relevance; includes its pilot) | 718131 | 16 Jul – 1 Sep 2025 | 32 |

## Files

| File | Content |
|---|---|
| `codebook/expert-survey-1_topics.csv` | `topic` (S01–S15), LimeSurvey code, `name`, the wording shown to the experts |
| `raw/expert-survey-1_ratings.csv` | `expert` and one column per topic, 1 = never … 5 = always relevant |
| `raw/expert-survey-1_participants.csv` | `expert`, `gender`, `years_experience_va`, `expertise_usability_evaluation`, `expertise_va_system_design` |
| `raw/expert-survey-1_comment-counts.csv` | comments per topic (texts not included) |
| `raw/expert-survey-1_suggestion-counts.csv` | Task 2 answers per expert (texts not included) |
| `raw/expert-survey-1_comment-coding.csv` | `comment_id`, `topic`, `topic_name`, `rating`, and 0/1 per code (specific item, reason for importance, reason for irrelevance, trade-off, depends on context, interpretation, difficulty in rating, overlap with another topic, new item suggested); one row per coded segment; from "Task 1 - CommentsAnalysis250127" (texts not included) |
| `raw/expert-survey-1_task2-coding.csv` | `segment`, `task2_answer`, item-or-topic and concept of coder A and coder B, consolidation `status`; from the same workbook (texts not included) |
| `raw/expert-survey-1-pilot_ratings.csv` | pilot: `expert` and one column per topic |
| `codebook/expert-survey-2_statements.csv` | `statement` (LimeSurvey code), `team_code` (e.g. `P0-12-A`), `text`, `display_order` |
| `raw/expert-survey-2_ratings.csv` | `expert` and one column per statement, 1–5 |
| `raw/expert-survey-2_participants.csv` | `expert`, `pilot` (1 = pilot reviewer, kept), profile columns as in survey 1 |
| `raw/expert-survey-2_comment-counts.csv` | comments per statement (texts not included) |
| `raw/item-history.csv` | `item`, `stage_order`, `stage`, `present`, `optional`, `text`, `decision` (team label) |
| `raw/item-pool.csv` | the 95 items of the merged pool: `item`, `source` (P0–P3), `topic`, `concept`, `optional` |
| `raw/source-p0-suggestions.csv` | P0: `item`, Task 2 answer number, `concept`, `topic`, `status`, `outcome` |
| `raw/source-p1-ueqplus.csv` | P1: UEQ+ scale, recommendation, new concept, related P0 topic and concept |
| `raw/source-p2-scales.csv` | P2: questionnaire, subscale, classification, topic and concept mapping |
| `raw/source-p3-literature.csv` | P3: term id, term, final topic-concept, AI topic-concept, review status |
| `raw/concept-occurrences.csv` | occurrences of each topic-concept in P0, P1, P2, P3 |

## Run

From the repository root, after placing the inputs in `phase1-item-development/tmp-data/`:

```
python phase1-item-development/data/prepare_expert_data.py
python phase1-item-development/data/prepare_item_sources.py
```
