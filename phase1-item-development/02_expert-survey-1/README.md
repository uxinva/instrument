# Step 02: First expert survey (topic relevance and missing topics)

The first expert survey (LimeSurvey 654492, "User Experience in VA systems – 1st Experts Survey", 16 to 23 January 2025) had two tasks:

- **Task 1:** rate the relevance of 15 topics of an existing UX questionnaire framework (the UEQ+ scales: Attractiveness, Perspicuity, Efficiency, Dependability, Stimulation, Novelty, Trust, Clarity, Usefulness, Adaptability, Intuitive use, Visual aesthetics, Value, Trustworthiness of content, Quality of content) for evaluating UX in visual analytics, from 1 = never relevant to 5 = always relevant, with an optional comment per topic. The adjective pairs of each scale were shown with the topic.
- **Task 2:** name up to ten topics, adjective pairs or statements that were missing (free text). The coding of these answers into items (pool P0) is summarised in [step 04](../04_item-flow/README.md).

Its pilot (LimeSurvey 654491, 8 to 12 December 2024, 4 submitted responses) used the same 15 topics; level 3 was worded "Some of the times relevant".

## Data

From [`../data/`](../data/README.md): `raw/expert-survey-1_ratings.csv` (37 experts × 15 topics, no missing ratings), `raw/expert-survey-1_participants.csv`, `raw/expert-survey-1_comment-counts.csv` (52 comments), `raw/expert-survey-1_suggestion-counts.csv` (Task 2), `raw/expert-survey-1-pilot_ratings.csv`, `codebook/expert-survey-1_topics.csv` (topic names and the wording shown), `raw/expert-survey-1_comment-coding.csv` (team coding of the 52 comments, without the texts) and `raw/expert-survey-1_task2-coding.csv` (the two coders' classification of the Task 2 answers, without the texts). Only submitted responses were analysed.

## Run

From the repository root:

```
python phase1-item-development/data/prepare_expert_data.py      # only if the exports change
python phase1-item-development/02_expert-survey-1/expert_survey_1.py --check
```

`--check` compares the results with the values on the 2025 slides (topic table, participants, Kendall's W, pilot counts) and the 37 × 15 ratings with the sheet "Ratings" of a local copy of the Google Sheet "Task 1 - CommentsAnalysis250127" (`restricted-data/team-sheets/`). `response-summary.csv` is written only when the raw export is in `restricted-data/limesurvey/`.

## Outputs (`output/`)

| File | Content |
|---|---|
| `participants-profile.csv` | Gender, years of experience with VA, expertise in usability evaluation and in VA system design |
| `response-summary.csv` | Responses started, submitted and incomplete; completion time |
| `topic-relevance.csv` | Per topic: n, rank, median, mean, variance, SD, counts per level, comments, `relevant` (mean ≥ 4) |
| `rating-counts.csv` | Ratings at each level, survey 1 and pilot |
| `agreement-kendall.csv` | Kendall's W of the 15 topics, the stepwise exclusion and the pilot |
| `pilot-topic-relevance.csv` | Topic table of the pilot |
| `task2-suggestions.csv` | Number of Task 2 answers |
| `agreement-icc.csv` | ICC two-way, average of the 37 raters (consistency and absolute agreement), with 95% CI (McGraw & Wong, as `irr::icc`) |
| `comment-coding-by-topic.csv` | Comments and coded segments per topic and per code |
| `task2-coding-agreement.csv` | Agreement of the two coders of Task 2 (item vs topic: % and Cohen's κ) and the consolidation status of the answers |
| `table-topic-relevance.tex` | LaTeX table `tab:topic-relevance`: median, mean, variance, % rated 4–5, Kendall's W without the topic, comments, kept |
| `table-comment-coding.tex` | LaTeX table `tab:comment-coding`: comment codes per topic (needs `graphicx` for `\rotatebox`) |
| `table-removed-topics.tex` | LaTeX table `tab:removed-topics` (`table*`): the 5 topics not kept, main codes and reason (`REMOVAL_REASONS` in the script) |
| `figure-topic-relevance.pdf` / `.png` | Diverging bar chart of the ratings per topic, sorted by mean; × marks the topics not kept |

The comments of the removed topics are written to `tmp-data/expert-survey-1_comments-of-removed-topics.csv` (not versioned) for choosing short quotes for the paper.

## Results

- **Responses:** 50 started, 37 submitted, 13 incomplete (5 of them with all Task 1 ratings). Completion time of the submitted responses: median 11.9 min, mean 20.9 min. The slide of 30 January 2025 says "average total time 11.9 minutes": that value is the median.
- **Experts (37):** 24 men, 13 women; years of experience with VA: mean 12.9. Usability evaluation: Expert 18, Competent 15, Limited 4. VA system design: Expert 14, Competent 20, Limited 3.
- **Topic relevance** (median / mean / variance): Perspicuity 5 / 4.76 / 0.24; Usefulness 5 / 4.76 / 0.36; Trustworthiness of content 5 / 4.41 / 0.53; Clarity 5 / 4.38 / 0.52; Trust 5 / 4.24 / 0.80; Intuitive use 4 / 4.30 / 0.55; Efficiency 4 / 4.22 / 0.56; Dependability 4 / 4.11 / 0.82; Quality of content 4 / 4.05 / 0.61; Attractiveness 4 / 4.00 / 0.94; Visual aesthetics 4 / 3.70 / 0.77; Value 4 / 3.54 / 1.20; Adaptability 3 / 3.24 / 0.74; Stimulation 3 / 3.22 / 0.90; Novelty 3 / 3.00 / 0.56.
- **Relevant topics (mean ≥ 4, meeting of 6 February 2025): 10**, from Perspicuity to Attractiveness. Visual aesthetics, Value, Adaptability, Stimulation and Novelty were not kept.
- **Agreement:** Kendall's W (corrected for ties) for the 15 topics = 0.358, χ²(14) = 185.5, p < .001. Stepwise exclusion (script by Emanuele; at each step the topic whose exclusion gives the highest W is removed, until W > 0.4): without Attractiveness W = 0.382; without Attractiveness and Dependability W = **0.407**. The team expected W > 0.4 (meeting of 16 January 2025).
- **ICC** (two-way, average of 37 raters): absolute agreement ICC(A,37) = 0.939, 95% CI [0.886, 0.976]; consistency ICC(C,37) = 0.949 [0.903, 0.979]; F(14, 504) = 19.4, p < .001. The slide value 0.939 is ICC(A,k).
- **Comments:** 52 comments (on 14 topics; none on Usefulness), split into 90 coded segments. Most frequent codes: reason for irrelevance 28, depends on context 19, reason for importance 18, comment on a specific item 18, overlap with another topic 10, trade-off 10, difficulty in rating 9. Novelty had the most segments (15; 7 reasons for irrelevance).
- **Pilot (4 experts):** ratings never 0, not often 5, sometimes 15, frequently 26, always 14; W = 0.567.
- **Task 2:** 118 answer fields filled by the 37 experts (most gave three answers). 14 of them are not suggestions ("-", "not available", "A", "B", "C", apologies). The team coded the answers into topic-concepts and wrote the P0 items (step 04). Two coders first classified each answer as an item or a topic: they agreed on 81.2% of the 96 segments both classified (Cohen's κ = 0.385); differences were resolved by consensus.

All values above agree with the 2025 slides; the ratings agree with the 2025 spreadsheet. Perspicuity and Usefulness have the same median and mean (4.757); the slide lists Usefulness first.
