"""Participant flow of the exploratory survey (phase 2.1): count the survey sessions by the completion
code they received, and check that the valid sessions are exactly the 506 participants of the data.

Run from the repository root:
    python phase2-1-scale-development/data/participant_flow.py

Input (personal information, NOT in Git; see .gitignore)
    tmp-data/results-survey686728.xlsx    LimeSurvey export of round 1 (all responses, all columns)
    tmp-data/results-survey378394.xlsx    LimeSurvey export of round 2
    raw/ratings-stimulus_original.csv     the 506 participants of the analysis (seed, stimulus, 65 items)

Output (no Prolific IDs; can be committed)
    prepared/participant-flow.csv         number of sessions per round and outcome, with the codes
    prepared/participant-sessions.csv     one row per session that received a code: round, LimeSurvey response
                                          ID, seed, system, code, outcome, whether the seed is in the data, and
                                          whether the same Prolific participant has another valid session
                                          (flag only; the Prolific ID is not written)

A session counts as a submission when the survey assigned it a completion code (end of the survey,
screen-out or consent refusal). Sessions without a code were abandoned before reaching an exit page and
are not submissions. The code is the value of the equation question that computes {CompletionCode}; the
export has its formula as column header, so the column is found by its values.

Codes (Prolific completion codes; round 2 used two Prolific code sets):
    valid completion     C15VDVOL, C8M1PIH2
    screened out         C1LYP9HZ, CXD3AJQH   (system not used, workspace image not recognised,
                                               last interaction not remembered)
    no consent           C13OIWSR, CNZ48DF4
"""
from pathlib import Path
import sys
import pandas as pd

HERE = Path(__file__).resolve().parent
PHASE = HERE.parent
TMP = PHASE / "tmp-data"
RAW = HERE / "raw"
PREPARED = HERE / "prepared"

ROUNDS = {1: ("686728", TMP / "results-survey686728.xlsx"),
          2: ("378394", TMP / "results-survey378394.xlsx")}
OUTCOME = {"C15VDVOL": "valid", "C8M1PIH2": "valid",
           "C1LYP9HZ": "screened out", "CXD3AJQH": "screened out",
           "C13OIWSR": "no consent", "CNZ48DF4": "no consent"}
ORDER = ["no consent", "screened out", "valid"]


def clean(series):
    """Strip spaces (including non-breaking ones) and return None for empty cells."""
    s = series.map(lambda v: None if pd.isna(v) else str(v).replace("\xa0", " ").strip())
    return s.map(lambda v: v if v else None)


def code_column(df):
    """The column whose values are completion codes (the equation question)."""
    best, best_n = None, 0
    for col in df.columns:
        n = clean(df[col]).isin(OUTCOME).sum()
        if n > best_n:
            best, best_n = col, n
    if best is None:
        sys.exit("No column with completion codes found")
    return best


def read_round(rnd, survey, path):
    if not path.exists():
        sys.exit(f"Missing {path}: export survey {survey} from LimeSurvey (all responses) into tmp-data/")
    df = pd.read_excel(path)
    # LimeSurvey puts the Prolific URL parameters right after 'Referrer URL':
    # PROLIFIC_PID, STUDY_ID, SESSION_ID, SYSTEM (headers are empty in the export).
    start = list(df.columns).index("Referrer URL") + 1
    pid, system = df.columns[start], df.columns[start + 3]
    out = pd.DataFrame({
        "round": rnd,
        "survey": survey,
        "response_id": df["Response ID"],
        "seed": df["Seed"],
        "system": clean(df[system]),
        "code": clean(df[code_column(df)]),
        "_pid": clean(df[pid]),
    })
    return out


def main():
    sessions = pd.concat([read_round(r, s, p) for r, (s, p) in ROUNDS.items()], ignore_index=True)
    all_rows = len(sessions)
    unknown = sessions["code"].notna() & ~sessions["code"].isin(OUTCOME)
    if unknown.any():
        sys.exit(f"Unknown codes: {sorted(sessions.loc[unknown, 'code'].unique())}")
    sessions = sessions[sessions["code"].notna()].copy()
    sessions["outcome"] = sessions["code"].map(OUTCOME)

    data = pd.read_csv(RAW / "ratings-stimulus_original.csv", encoding="utf-8-sig")
    data_seeds = set(data["seed"])
    sessions["in_data"] = sessions["seed"].isin(data_seeds)

    valid = sessions[sessions["outcome"] == "valid"]
    repeated = valid["_pid"].notna() & valid["_pid"].duplicated(keep=False)
    sessions["repeated_valid_participant"] = False
    sessions.loc[valid.index[repeated], "repeated_valid_participant"] = True

    # Checks against the analysis data
    problems = []
    if set(valid["seed"]) != data_seeds:
        problems.append(f"valid seeds differ from the data: {len(set(valid['seed']) ^ data_seeds)} seeds")
    if sessions.loc[sessions["outcome"] != "valid", "in_data"].any():
        problems.append("a non-valid session is in the data")
    merged = valid.merge(data[["seed", "stimulus"]], on="seed")
    if (merged["system"] != merged["stimulus"]).any():
        problems.append("system in the export differs from the data label")

    # Counts
    flow = (sessions.groupby(["round", "survey", "outcome"])
            .agg(sessions=("code", "size"), codes=("code", lambda c: " + ".join(f"{k} {v}" for k, v in c.value_counts().sort_index().items())))
            .reset_index())
    total = sessions.groupby("outcome").size().reindex(ORDER).rename("sessions").reset_index()
    total.insert(0, "survey", "both")
    total.insert(0, "round", "total")
    total["codes"] = ""
    flow = pd.concat([flow, total, pd.DataFrame([{
        "round": "total", "survey": "both", "outcome": "submissions", "sessions": len(sessions), "codes": ""}])],
        ignore_index=True)

    PREPARED.mkdir(exist_ok=True)
    flow.to_csv(PREPARED / "participant-flow.csv", index=False)
    sessions.drop(columns="_pid").sort_values(["round", "response_id"]).to_csv(
        PREPARED / "participant-sessions.csv", index=False)

    n_people = valid["_pid"].nunique()
    print(flow.to_string(index=False))
    print(f"\nRows in the exports: {all_rows}; with a completion code (submissions): {len(sessions)}")
    print(f"Valid sessions: {len(valid)}, from {n_people} Prolific participants; "
          f"{int(repeated.sum()) // 2} participants have two valid sessions (each for a different system)"
          if repeated.any() else f"Valid sessions: {len(valid)}, all from different participants")
    if problems:
        sys.exit("CHECK FAILED: " + "; ".join(problems))
    print("Check: the valid sessions are exactly the 506 participants of the data, with the same system labels")


if __name__ == "__main__":
    main()
