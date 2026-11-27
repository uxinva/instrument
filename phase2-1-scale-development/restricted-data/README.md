# Restricted data of phase 2.1 (scale development)

The full LimeSurvey exports of the two rounds of the exploratory survey (all responses and all columns, including incomplete sessions). They cannot be published because they contain Prolific IDs.

| File | Content | Read by |
|---|---|---|
| `limesurvey/results-survey686728.xlsx` | Round 1, exported 2026-11-17 | `data/participant_flow.py` |
| `limesurvey/results-survey378394.xlsx` | Round 2, exported 2026-11-17 | `data/participant_flow.py` |

`MANIFEST.csv` lists both files with their origin, date, size and SHA-256 checksum.

The anonymised ratings `data/raw/ratings-stimulus_original.csv` and the seed/system exports `data/raw/survey_seed_system/` are in Git (see [`../data/README.md`](../data/README.md)).

## Rules

- **Never commit these files.** `.gitignore` excludes everything in this folder except this README and `MANIFEST.csv`.
- **Do not edit them.** If a file has to be replaced (for example a new export), keep the old one in the Drive archive, put the new one here, run `python restricted_data.py update phase2-1-scale-development` from the repository root to record its new checksum, and note the change in the commit message.
- **Check them** with `python restricted_data.py verify phase2-1-scale-development`. The preparation scripts also stop if a file is missing and warn if it differs from the manifest.
- **Back-up:** a copy of this folder is kept in the project's Google Drive (registered in the "Project Map and Records" sheet). At publication it is deposited with restricted access.
