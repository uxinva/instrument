# Restricted data of phase 3 (validation)

The records from which [`../data/anonymise_raw.py`](../data/anonymise_raw.py) builds the anonymised exports in `data/raw/`. Until 2026-11-27 they were in `data/private/`.

| File | Content |
|---|---|
| `limesurvey-exports/results-survey349675.xlsx` | Validation survey, User Forums: original export |
| `limesurvey-exports/results-survey127653.xlsx` | Validation survey, Students: original export |
| `limesurvey-exports/results-survey372164.xlsx` | Validation survey, Prolific: original export (Prolific and session IDs) |
| `id_map.csv` | Pseudonym map: original IDs ↔ codes `P0001`, `S0001` (written and reused by `anonymise_raw.py`) |
| `redactions.csv` | Free-text redactions: original text ↔ placeholder |

`MANIFEST.csv` lists these files with their checksums. They are the files of Emanuele's former `data/private/` folder (received on 2026-11-27): with them, `anonymise_raw.py` rebuilds `data/raw/` byte for byte. A new export from LimeSurvey is **not** equivalent: the Forum survey (349675) now also contains two incomplete responses started after the original export (IDs 33 and 34, September and November 2026), and the files carry a different export timestamp.

## Rules

- **Never commit these files.** `.gitignore` excludes everything in this folder except this README and `MANIFEST.csv`.
- **Do not edit them.** If a file has to be replaced (for example a new export), keep the old one in the Drive archive, put the new one here, run `python restricted_data.py update phase3-validation` from the repository root to record its new checksum, and note the change in the commit message.
- **Check them** with `python restricted_data.py verify phase3-validation`. The preparation scripts also stop if a file is missing and warn if it differs from the manifest.
- **Back-up:** a copy of this folder is kept in the project's Google Drive (registered in the "Project Map and Records" sheet). At publication it is deposited with restricted access.
