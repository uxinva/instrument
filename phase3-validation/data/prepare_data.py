"""Prepare the validation-phase data from the anonymised survey exports.

Implements the procedure described in data/README.md:

    data/raw/results-survey*.csv  ->  data/prepared/ratings_complete.csv
                                      data/prepared/ratings_grades.csv
                                      data/prepared/ux_ratings.csv
                                      data/prepared/sus_ratings.csv
                                      data/prepared/ueqs_ratings.csv

Run from the repository root (after anonymise_raw.py):

    python phase3-validation/data/prepare_data.py

The section letters (A1, A2, ... E) refer to data/README.md.
"""

from pathlib import Path

import numpy as np
import pandas as pd

DATA_DIR = Path(__file__).resolve().parent
RAW_DIR = DATA_DIR / "raw"
OUT_DIR = DATA_DIR / "prepared"

# The three surveys, in the order they are merged (section C).
# `prefix` is used to build an id that is unique across the surveys.
SURVEYS = [
    {"file": "results-survey349675.csv", "group": "Forum",    "prefix": "FOR"},
    {"file": "results-survey127653.csv", "group": "Student",  "prefix": "STU"},
    {"file": "results-survey372164.csv", "group": "Prolific", "prefix": "PRO"},
]
PROLIFIC = "results-survey372164.csv"

# Invalid responses, removed before merging (original LimeSurvey ids).
# Student responses 25 and 59: asked to evaluate a visual analytics system, these
# participants answered about the Python language ("Uso Python", "Python Plotly"),
# so their answers do not refer to a visual analytics system and are not valid.
EXCLUDED = {"results-survey127653.csv": ["25", "59"]}

VALID_COMPLETION_CODE = "C15VDVOL"
ATTENTION_ITEM = "P902"      # attention check: participants were asked to answer 2
ATTENTION_ANSWER = "2"
NOT_APPLICABLE = "8"         # TO CONFIRM: meaning of answer option 8 in the UXVis items


# --- A. Corrections to individual files -------------------------------------

def correct(df: pd.DataFrame, file: str) -> pd.DataFrame:
    df = df.copy()

    if file == PROLIFIC:
        # A1. Participants wrongly screened out by a survey error
        rows = df["id"].isin(["58", "65", "147", "253", "380", "400"])
        df.loc[rows & (df["CompletionCode"] == "C1LYP9HZ"), "CompletionCode"] = VALID_COMPLETION_CODE
        # A2. System S10 was SuperSet in the first rounds (later Excel)
        rows = df["id"].isin(["352", "826"])
        df.loc[rows & (df["VASys"] == "S10"), "VASys"] = "-oth-"

    # A3. System names typed in "other" that correspond to a listed system
    def harmonise(condition, code, name):
        df.loc[condition, "VASys"] = code
        df.loc[condition, "VASys[other]"] = np.nan
        df.loc[condition, "SYSTEM"] = name

    other = df["VASys[other]"].fillna("").str.strip()
    if file in ("results-survey127653.csv", PROLIFIC):
        harmonise(other.isin(["Excel, Python", "Excel and Odoo", "excel", "Excel"]), "S10", "Excel")
    if file == "results-survey127653.csv":
        harmonise(other == "AWS QuickSight", "S09", "Quick Sight")
        harmonise(df["SYSTEM"].fillna("").str.strip() == "Looker", "S08", "Data Studio")
        harmonise(other == "PowerBI, QlikView", "S01", "Power BI")
    if file == PROLIFIC:
        harmonise(other == "Data Studio (Looker)", "S08", "Data Studio")

    # A4. Inverted UEQ-S item in the Student and Forum surveys
    if file in ("results-survey349675.csv", "results-survey127653.csv"):
        inversion = {f"AO0{k}": f"AO0{8 - k}" for k in range(1, 8)}
        df["UEQS1[SQ004]"] = df["UEQS1[SQ004]"].replace(inversion)

    return df


# --- B. Harmonise the three files --------------------------------------------

COMMENTS_RENAME = {"EComments": "EComIntuit", "EComments2": "EComVis", "EComments3": "EComCog"}


def harmonise_columns(df: pd.DataFrame, survey: dict) -> pd.DataFrame:
    df = df.copy()
    file = survey["file"]

    # Remove invalid responses (see EXCLUDED above)
    df = df[~df["id"].isin(EXCLUDED.get(file, []))]

    # B1-B2. Participant group and exit status
    if file == PROLIFIC:
        exit_status = df["CompletionCode"]
    else:
        exit_status = np.where(df["submitdate"].notna(), "OK", None)
        exit_status = pd.Series(exit_status, index=df.index)
    # Unique id across the three surveys, e.g. STU-0010
    unique_id = survey["prefix"] + "-" + df["id"].astype(int).map("{:04d}".format)

    # B3. Column names
    renamed = {}
    for col in df.columns:
        new = col
        for prefix in ("EIntuitiveness[", "EVisualization[", "ECognitiveValue["):
            if new.startswith(prefix):
                new = new[len(prefix):]
        if new.startswith("UEQS1[SQ"):
            new = "UEQ_" + str(int(new[len("UEQS1[SQ"):-1]))
        elif new.startswith("SUS1[SQ"):
            new = "SUS_" + str(int(new[len("SUS1[SQ"):-1]))
        new = new.replace("]", "")
        renamed[col] = COMMENTS_RENAME.get(new, new)
    df = df.rename(columns=renamed).rename(columns={"SYSTEM": "stimulus"})

    # B4-B5. Columns to keep, in the same order for every survey
    items_intuitiveness = ["P026", "P088", "P4026A", "P902"]
    items_visualization = ["P022A", "P067", "P089", "P097", "P098", "P106"]
    items_cognitive = ["P027", "P060", "P064", "P301"]
    ueq = [f"UEQ_{k}" for k in range(1, 9)]
    sus = [f"SUS_{k}" for k in range(1, 11)]

    out = pd.DataFrame({"Participant": survey["group"], "CompletionCode": exit_status, "id": unique_id})
    columns = (["seed", "stimulus", "E01Expertise", "SysCharac", "InteractDesc",
                "QGender", "QGender[other", "QAge2"]
               + items_intuitiveness + ["EComIntuit"]
               + items_visualization + ["EComVis"]
               + items_cognitive + ["EComCog"]
               + ueq + sus)
    return pd.concat([out, df[columns]], axis=1)


# --- D. Valid responses -------------------------------------------------------

def valid_grades(complete: pd.DataFrame) -> pd.DataFrame:
    df = complete[complete["CompletionCode"].isin(["OK", VALID_COMPLETION_CODE])]
    # Attention check: keep only participants who gave the requested answer
    df = df[df[ATTENTION_ITEM] == ATTENTION_ANSWER]
    df = df.drop(columns=[ATTENTION_ITEM, "Participant", "CompletionCode",
                          "E01Expertise", "SysCharac", "InteractDesc",
                          "QGender", "QGender[other", "QAge2",
                          "EComIntuit", "EComVis", "EComCog"])

    gold_standard = [c for c in df.columns if c.startswith(("UEQ_", "SUS_"))]
    for col in gold_standard:                      # AO01 -> 1, ..., AO07 -> 7
        df[col] = df[col].str.extract(r"^AO0?(\d+)$", expand=False).astype("Int64")

    uxvis = [c for c in df.columns if c.startswith("P")]
    for col in uxvis:
        df[col] = pd.to_numeric(df[col].where(df[col] != NOT_APPLICABLE), errors="raise").astype("Int64")

    return df.reset_index(drop=True)


def write(df: pd.DataFrame, name: str, na_rep: str = "NA") -> None:
    df.to_csv(OUT_DIR / name, index=False, na_rep=na_rep, lineterminator="\n")
    print(f"{name}: {len(df)} rows, {df.shape[1]} columns")


def main() -> None:
    OUT_DIR.mkdir(exist_ok=True)

    parts = []
    for survey in SURVEYS:
        raw = pd.read_csv(RAW_DIR / survey["file"], dtype=str)
        parts.append(harmonise_columns(correct(raw, survey["file"]), survey))

    # C. Merge
    complete = pd.concat(parts, ignore_index=True)
    assert complete["id"].is_unique
    write(complete, "ratings_complete.csv", na_rep="")

    # D. Valid responses
    grades = valid_grades(complete)
    write(grades, "ratings_grades.csv")

    # E. Split by instrument
    meta = ["id", "seed", "stimulus"]
    write(grades[meta + [c for c in grades.columns if c.startswith("P")]], "ux_ratings.csv")
    write(grades[meta + [f"SUS_{k}" for k in range(1, 11)]], "sus_ratings.csv")
    write(grades[meta + [f"UEQ_{k}" for k in range(1, 9)]], "ueqs_ratings.csv")


if __name__ == "__main__":
    main()
