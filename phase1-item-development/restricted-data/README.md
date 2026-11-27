# Restricted data of phase 1 (item development)

The records from which the anonymised files in [`../data/`](../data/README.md) are built. They cannot be published: the survey exports contain free-text comments and suggestions of the experts (and, in the pilot of survey 1, a name or pseudonym field), and the team spreadsheets contain the texts of copyrighted questionnaire items, excerpts of papers and the experts' suggestions.

`MANIFEST.csv` lists every file with its description, origin (LimeSurvey survey ID or Google Drive file ID), date of export or download, the scripts that read it, its size and its SHA-256 checksum.

| Folder | Content | Read by |
|---|---|---|
| `limesurvey/` | Exports of the pilot of expert survey 1 (654491), expert survey 1 (654492) and expert survey 2 (718131): responses (`results-survey<ID>.xlsx`, headers "question code. question text", answers as text, all responses) and survey structure (`limesurvey_survey_<ID>.lss`) | `data/prepare_expert_data.py`; `02_expert-survey-1/expert_survey_1.py` (response summary) |
| `team-sheets/` | The team Google Sheets downloaded as .xlsx on 2026-11-24: "Items Historic", "Task2SuggestedItemsAnalysis250127", "Task 1 - CommentsAnalysis250127" (sources of `data/raw/`), "2nd_survey_results_complete_answers" (`--check` of step 03), and two sheets kept as references of manual checks | `data/prepare_item_sources.py`; `--check` of steps 02 and 03 |

The Google Sheets keep changing (some columns are `IMPORTRANGE` formulas), so the copies here, not the live sheets, are the versions that produced the published results.

## Rules

- **Never commit these files.** `.gitignore` excludes everything in this folder except this README and `MANIFEST.csv`.
- **Do not edit them.** If a file has to be replaced (for example a new export), keep the old one in the Drive archive, put the new one here, run `python restricted_data.py update phase1-item-development` from the repository root to record its new checksum, and note the change in the commit message.
- **Check them** with `python restricted_data.py verify phase1-item-development`. The preparation scripts also stop if a file is missing and warn if it differs from the manifest.
- **Back-up:** a copy of this folder is kept in the project's Google Drive (registered in the "Project Map and Records" sheet). At publication it is deposited with restricted access.
