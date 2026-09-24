# Data preparation

The raw LimeSurvey exports are turned into the files used by the analysis steps in two stages, each done by a script:

```
data/
├── private/                    NOT in git (personal data)
│   ├── limesurvey-exports/     original exports (.xlsx)
│   ├── id_map.csv              pseudonym map: original Prolific IDs ↔ codes
│   └── redactions.csv          free-text redactions (original text ↔ replacement)
├── raw/                        anonymised exports (.csv)          ← anonymise_raw.py
├── prepared/                   cleaned and merged files (.csv)    ← prepare_data.py
├── codebook/items.csv          item codes, short names, factors and wording
├── anonymise_raw.py            private/limesurvey-exports/ → raw/
└── prepare_data.py             raw/ → prepared/
```

Run both from the repository root (Python ≥ 3.11 with pandas and openpyxl):

```bash
python phase3-validation/data/anonymise_raw.py   # only needed when the exports change
python phase3-validation/data/prepare_data.py
```

## 1. Anonymisation (`anonymise_raw.py`)

The original exports stay in `data/private/`, which is listed in `.gitignore` and must never be committed. The script writes an anonymised copy of each export to `data/raw/`:

- `PROLIFICID` is replaced by a code `P0001`, `P0002`, … There is one code per participant: someone who started the survey more than once keeps the same code.
- `SESSIONID` is replaced by a code `S0001`, `S0002`, …
- Details in free-text answers that could identify a participant are replaced by a placeholder in square brackets, e.g. `[university]`, `[employer]`, `[custom research tool]`. The replacements are listed in `data/private/redactions.csv`, which is private because it contains the original text. If a listed text is not found, the script stops, so a redaction is never skipped silently.
- All other columns are copied unchanged. `STUDYID` identifies the Prolific study, not a person, so it is kept.

The link between codes and original IDs is kept only in `data/private/id_map.csv`. The script reuses this map, so the codes stay the same every time it runs. At the end it checks that no original ID is left in `data/raw/`.

**Free-text review.** All free-text answers were read before publication (gender and age are covered by the ethics approval). In the Student survey, where the group is small, four responses mentioned details that could identify the participant: an institution and an employer, a custom-built research tool and its topic, and teaching the course. These details were redacted. The Forum and Prolific answers mention at most an occupation or a country, which is not enough to identify anyone in these samples. **Any new data must be reviewed the same way before it is committed.**

## 2. Preparation (`prepare_data.py`)

The script applies the steps A–E below. Its results were checked against the files prepared by hand: all 226 valid responses and every answer match. There are three differences:

- The `id` column is now unique across the three surveys: survey prefix + LimeSurvey id, e.g. `FOR-0014`, `STU-0010`, `PRO-0058`. The LimeSurvey ids alone repeat between surveys.
- One stimulus name is redacted (`[custom research tool]`, response `STU-0016`). It is not one of the five systems used in the multi-group analyses.
- `ratings_complete.csv` now also has the 35 Student responses that were not finished. Before, it kept only the finished Student responses, while keeping every Forum and Prolific response.

### Input: anonymised exports (`raw/`)

| File | Survey | Participant group | id prefix |
|---|---|---|---|
| `results-survey349675.csv` | User Experience with Visual Analytics – Validation Survey (User Forums) | Forum | `FOR` |
| `results-survey127653.csv` | User Experience with Visual Analytics – Validation Survey | Student | `STU` |
| `results-survey372164.csv` | User Experience with Visual Data Analysis Tools (Prolific) | Prolific | `PRO` |

Export settings in LimeSurvey: format **Microsoft Excel**, responses as **answer codes**, headings as **question codes**.

### Output: prepared files (`prepared/`)

| File | Content |
|---|---|
| `ratings_complete.csv` | All responses from the three surveys, merged, with the columns kept in step B |
| `ratings_grades.csv` | Valid responses only; metadata and item answers as numbers |
| `ux_ratings.csv` | `id`, `seed`, `stimulus` and the UXVis items (`P…`) |
| `sus_ratings.csv` | `id`, `seed`, `stimulus` and `SUS_1`–`SUS_10` |
| `ueqs_ratings.csv` | `id`, `seed`, `stimulus` and `UEQ_1`–`UEQ_8` |

### A. Corrections to individual files

#### A1. Completion code of wrongly screened-out participants (Prolific)

A survey error screened out some participants by mistake.

- File: `results-survey372164`
- Rows: `id` = 58, 65, 147, 253, 380, 400
- Set `CompletionCode` from `C1LYP9HZ` to `C15VDVOL`

#### A2. System S10 (Prolific)

In the first rounds, system code `S10` meant SuperSet; it was later replaced by Excel. Two answers given for SuperSet are moved to "other".

- File: `results-survey372164`
- Rows: `id` = 352, 826
- Set `VASys` from `S10` to `-oth-`

#### A3. Harmonise system names typed in "other"

Some participants typed the name of a listed system in the "other" field. For the rows below, set `VASys` to the code, clear `VASys[other]`, and set `SYSTEM` to the name.

| File(s) | Condition | `VASys` | `SYSTEM` |
|---|---|---|---|
| 127653, 372164 | `VASys[other]` is `Excel, Python`, `Excel and Odoo`, `excel` or `Excel` | `S10` | Excel |
| 127653 | `VASys[other]` is `AWS QuickSight` | `S09` | Quick Sight |
| 127653 | `SYSTEM` is `Looker` | `S08` | Data Studio |
| 372164 | `VASys[other]` is `Data Studio (Looker)` | `S08` | Data Studio |
| 127653 | `VASys[other]` is `PowerBI, QlikView` | `S01` | Power BI |

The spelling `Quick Sight` is used everywhere. An older copy of the data used by step 00 spelled it `QuickSight`.

#### A4. Inverted UEQ-S item (Student and Forum)

In the Student and Forum surveys, item `UEQS1[SQ004]` was shown with its poles swapped. This affects the 36 valid answers up to `seed` = 1748214382. In files `results-survey349675` and `results-survey127653`, recode every value of `UEQS1[SQ004]`:

| From | AO01 | AO02 | AO03 | AO04 | AO05 | AO06 | AO07 |
|---|---|---|---|---|---|---|---|
| **To** | AO07 | AO06 | AO05 | AO04 | AO03 | AO02 | AO01 |

When this was done by hand in Excel, it took three find-and-replace passes with temporary codes, so that values weren't recoded twice: `AO01`–`AO03` → `BO01`–`BO03`, then `AO05`–`AO07` → `AO03`–`AO01`, then `BO01`–`BO03` → `AO07`–`AO05`. A script can do it in one step.

**Check:** in `results-survey349675`, the first values are `AO03, AO03, AO02, AO01, AO04` before the recoding and `AO05, AO05, AO06, AO07, AO04` after it.

### B. Harmonise the three files

0. **Remove invalid responses.** Student responses 25 and 59 are removed. When asked about the visual analytics system they use, these participants answered about the Python language ("Uso Python", "Python Plotly"), so their answers do not refer to a visual analytics system and are not valid.
1. **Add a `Participant` column** (first column): `Forum` (349675), `Prolific` (372164), `Student` (127653).
2. **Add an exit-status column** (second column, named `CompletionCode` in the output):
   - Forum and Student: `OK` when `submitdate` is filled in.
   - Prolific: copy of `CompletionCode`.
3. **Rename columns:**
   - `SYSTEM` → `stimulus`
   - remove every `]` from column names, and the prefixes `EIntuitiveness[`, `EVisualization[`, `ECognitiveValue[`, so that the item columns are named `P026`, `P027`, …
   - `UEQS1[SQ001]`–`UEQS1[SQ008]` → `UEQ_1`–`UEQ_8`
   - `SUS1[SQ001]`–`SUS1[SQ010]` → `SUS_1`–`SUS_10`
4. **Keep only these columns** (drop all others):
   - `Participant`, `ExitOK` (or `CompletionCode`), `id`, `seed`, `stimulus`
   - `E01Expertise`, `SysCharac`, `InteractDesc`
   - `QGender`, `QGender[other`, `QAge2`
   - every column starting with `P`
   - the comment columns `EComments`, `EComments2`, `EComments3` (or `EComIntuit`, `EComVis`, `EComCog`)
   - `UEQ_1`–`UEQ_8`, `SUS_1`–`SUS_10`
5. **Same column order.** In the Forum and Student files, move `QGender`, `QGender[other` and `QAge2` so they come right after `InteractDesc` and before `P026`, as in the Prolific file.

### C. Merge: `ratings_complete.csv`

Stack the three files in this order: Forum (349675), Student (127653), Prolific (372164).

### D. Valid responses: `ratings_grades.csv`

Starting from `ratings_complete.csv`:

1. Keep only rows where `ExitOK` is `OK` or `C15VDVOL`.
2. **Attention check.** `P902` is an attention-check item that asked participants to answer 2. Keep only rows where `P902` = 2, then drop `P902`.
3. Drop the comment columns, `E01Expertise`, `SysCharac`, `InteractDesc`, `QGender`, `QGender[other`, `QAge2`, `Participant` and `ExitOK` / `CompletionCode`.
4. Convert the SUS and UEQ answers from codes to numbers: `AO01` → 1, `AO02` → 2, …, `AO07` → 7.
5. **"I don't know" answers.** The UXVis items (columns starting with `P`) are answered on a 1–7 scale, plus an 8th option, *I don't know*. It is not a position on the scale, so `8` is replaced with `NA` (missing). In the valid data this concerns 5 answers from 5 participants (P106: 2; P067, P027, P064: 1 each).

### E. Split by instrument

From `ratings_grades.csv`, write:

- `ux_ratings.csv`: `id`, `seed`, `stimulus` and the columns starting with `P`
- `sus_ratings.csv`: `id`, `seed`, `stimulus`, `SUS_1`–`SUS_10`
- `ueqs_ratings.csv`: `id`, `seed`, `stimulus`, `UEQ_1`–`UEQ_8`
