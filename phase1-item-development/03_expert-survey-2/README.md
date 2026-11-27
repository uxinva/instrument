# Step 03: Second expert survey (statement relevance)

The second expert survey (LimeSurvey 718131, "User experience in visual analytics – Items relevance", 16 July to 1 September 2025) asked experts to rate how relevant each of **83 candidate statements** is to evaluate UX in visual analytics, on a five-point scale (1 = never relevant, 2 = not often, 3 = sometimes, 4 = frequently, 5 = always relevant), with an optional comment per statement. The statements with a mode of 3 or lower were removed, which left the **65 items** of the exploratory survey (phase 2.1).

## Data

Read from [`../data/`](../data/README.md) (built by `data/prepare_expert_data.py` from the LimeSurvey export):

- `raw/expert-survey-2_ratings.csv`: 32 experts × 83 statements, no missing ratings.
- `raw/expert-survey-2_participants.csv`: gender, years of experience with VA, self-rated expertise.
- `raw/expert-survey-2_comment-counts.csv`: number of comments per statement (112 comments; the texts are not in the repository).
- `codebook/expert-survey-2_statements.csv`: LimeSurvey code, team code (e.g. `P012A` = `P0-12-A`), statement text, display order.

Only submitted responses were analysed (32 of 60 started). Two of the 32 are the **pilot reviewers** of this survey (the first two responses, 16 and 19 July 2025, before the invitations of 25 July); the team kept them. Some statements were reworded after the pilot, so these two experts rated part of the statements in their earlier wording. Response ID 8 (a member of the team, test response) is not in the export.

## Run

From the repository root:

```
python phase1-item-development/data/prepare_expert_data.py        # only if the export changes
python phase1-item-development/03_expert-survey-2/expert_survey_2.py --check
```

`--check` compares the results with a local copy of the 2025 spreadsheet (`restricted-data/team-sheets/2nd_survey_results_complete_answers.xlsx`, Google Sheet "2nd_survey_results_complete_answers", sheet "Analysis"); without the copy it only reports that there is nothing to compare.

## Outputs (`output/`)

| File | Content |
|---|---|
| `participants-profile.csv` | Experts, pilot reviewers, gender, years of experience (mean, median, range), expertise in usability evaluation and in VA system design |
| `rating-counts.csv` | Number of ratings at each level over all statements |
| `statement-statistics.csv` | Per statement: n, mode (three tie rules), mean, median, variance, SD, counts per level, number of comments, `removed` |
| `agreement-icc.csv` | Two-way ICC (statements as subjects, experts as raters, average of 32 ratings), consistency and absolute agreement, F test |
| `removed-statements.csv` | The 18 removed statements |
| `table-removed-statements.tex` | LaTeX table of the removed statements |

## Results

- **Experts:** 32 (2 pilot reviewers); 22 men, 10 women; years of experience with VA: mean 15.6, median 14 (3–35). Usability evaluation: Expert 9, Competent 19, Limited 4. VA system design: Expert 12, Competent 19, Limited 1.
- **Ratings (2,656):** always 838, frequently 1,037, sometimes 652, not often 120, never 9.
- **Agreement:** ICC(C,32) = 0.876, ICC(A,32) = 0.851; F(82, 2542) = 8.07, p < .001 (agreement test: F(82, 641)).
- **Removed: 18 statements** with mode ≤ 3: P0-4-B, P0-12-A, P0-19, P0-23, P0-28, P0-39, P0-45, P0-62-A, P0-65, P0-71, P0-73, P0-81, P1-01, P2-02, P2-09, P2-15, P2-16, P3-03. 83 − 18 = 65.
- **Mode 5 and no comment:** 10 statements (discussed in the meeting of 4 September 2025 as candidates to skip in the cognitive interviews).

### Mode rule and ties

The 2025 spreadsheet computed the mode with `MODE.SNGL` over the experts in Response ID order. When two levels have the same count, `MODE.SNGL` returns the level that occurs first in that order. The script reproduces this rule (`mode_first`) and also gives the lower (`mode_low`) and higher (`mode_high`) tied level.

Seven statements have two modes. 14 statements have a single mode ≤ 3. Of the six statements tied between 3 and 4, four were removed because a 3 came first (P0-19, P0-62-A, P0-71, P2-16) and two were kept because a 4 came first (P2-04, P0-67); P0-6 (tie between 4 and 5) is kept under any rule. With the lower tied level 20 statements would have been removed; with the higher tied level, 14.

## Check against the 2025 spreadsheet

Ratings (32 × 83), mode, mean, median, variance and SD agree for all 83 statements. One difference: a comment ("See comments above on simplicity") written in the comment box of **P0-26** ("I found it easy to use this system", LimeSurvey question `commentsP026`) was counted under **P0-25** in the spreadsheet. The script follows the survey. Neither statement was removed.
