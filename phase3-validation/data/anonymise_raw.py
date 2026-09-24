"""Anonymise the LimeSurvey exports.

Reads the original exports from   data/private/limesurvey-exports/*.xlsx
writes anonymised copies to       data/raw/*.csv
and keeps the pseudonym map in    data/private/id_map.csv

data/private/ is git-ignored and must never be committed. The anonymised
files in data/raw/ are the ones used by prepare_data.py and kept in git.

What is replaced (Prolific survey only):
  PROLIFICID  -> P0001, P0002, ...   (one code per participant; a participant
                                      who started the survey twice keeps the
                                      same code)
  SESSIONID   -> S0001, S0002, ...   (one code per Prolific session)
It also applies the text redactions listed in data/private/redactions.csv
(columns: file, id, column, find, replace), used to hide details in free-text
answers that could identify a participant. The list is private because it
contains the original text. Every `find` must occur in its cell, otherwise the
script stops, so a redaction can never be skipped silently.

All other columns are copied unchanged.

The map is reused on later runs, so codes never change: new IDs get the next
free number. Run from the repository root:

    python phase3-validation/data/anonymise_raw.py
"""

from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parent
EXPORTS_DIR = DATA_DIR / "private" / "limesurvey-exports"
MAP_FILE = DATA_DIR / "private" / "id_map.csv"
REDACTIONS_FILE = DATA_DIR / "private" / "redactions.csv"
RAW_DIR = DATA_DIR / "raw"

# column -> prefix of its pseudonyms
PSEUDONYMISED = {"PROLIFICID": "P", "SESSIONID": "S"}


def load_map() -> pd.DataFrame:
    if MAP_FILE.exists():
        return pd.read_csv(MAP_FILE, dtype=str)
    return pd.DataFrame(columns=["field", "original", "pseudonym"])


def pseudonymise(values: pd.Series, field: str, id_map: pd.DataFrame) -> tuple[pd.Series, pd.DataFrame]:
    prefix = PSEUDONYMISED[field]
    known = id_map[id_map["field"] == field]
    lookup = dict(zip(known["original"], known["pseudonym"]))
    next_number = len(lookup) + 1
    new_rows = []
    for value in values.dropna().unique():  # order of first appearance
        if value not in lookup:
            code = f"{prefix}{next_number:04d}"
            lookup[value] = code
            new_rows.append({"field": field, "original": value, "pseudonym": code})
            next_number += 1
    if new_rows:
        id_map = pd.concat([id_map, pd.DataFrame(new_rows)], ignore_index=True)
    return values.map(lookup), id_map


def redact(df: pd.DataFrame, file_stem: str, redactions: pd.DataFrame) -> pd.DataFrame:
    for r in redactions[redactions["file"] == file_stem].itertuples(index=False):
        rows = df.index[df["id"] == r.id]
        if len(rows) != 1 or r.column not in df.columns:
            raise SystemExit(f"ERROR: redaction target not found: {r.file} id={r.id} {r.column}")
        cell = df.at[rows[0], r.column]
        if not isinstance(cell, str) or r.find not in cell:
            raise SystemExit(f"ERROR: text to redact not found in {r.file} id={r.id} {r.column}")
        df.at[rows[0], r.column] = cell.replace(r.find, r.replace)
    return df


def main() -> None:
    RAW_DIR.mkdir(exist_ok=True)
    id_map = load_map()
    originals = set()
    redactions = (pd.read_csv(REDACTIONS_FILE, dtype=str, keep_default_na=False)
                  if REDACTIONS_FILE.exists() else pd.DataFrame(columns=["file", "id", "column", "find", "replace"]))

    for xlsx in sorted(EXPORTS_DIR.glob("results-survey*.xlsx")):
        df = pd.read_excel(xlsx, dtype=str)
        for field in PSEUDONYMISED:
            if field in df.columns:
                originals.update(df[field].dropna())
                df[field], id_map = pseudonymise(df[field], field, id_map)
        df = redact(df, xlsx.stem, redactions)
        out = RAW_DIR / (xlsx.stem + ".csv")
        df.to_csv(out, index=False, lineterminator="\n")
        print(f"{xlsx.name} -> {out.relative_to(DATA_DIR)} ({len(df)} rows)")

    MAP_FILE.parent.mkdir(exist_ok=True)
    id_map.to_csv(MAP_FILE, index=False, lineterminator="\n")
    print(f"Pseudonym map: {MAP_FILE.relative_to(DATA_DIR)} ({len(id_map)} entries)")

    # Safety check: no original ID may be left in the anonymised files
    for csv in RAW_DIR.glob("*.csv"):
        text = csv.read_text(encoding="utf-8")
        leaked = [o for o in originals if o in text]
        if leaked:
            raise SystemExit(f"ERROR: {len(leaked)} original IDs still present in {csv.name}")
    print("Check passed: no original Prolific or session IDs in data/raw/")
    print(f"Redactions applied: {len(redactions)}")


if __name__ == "__main__":
    main()
