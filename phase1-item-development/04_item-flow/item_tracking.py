"""Shared functions: the stages of every candidate item, from the merged pool to the validated scale.

Used by item_flow.py (step 04) and by ../item_lookup.py. Reads only files that are in the
repository:
    phase1-item-development/data/raw/item-history.csv, item-pool.csv          (stages 1-8)
    phase1-item-development/data/raw/expert-survey-2_ratings.csv, codebook    (expert survey 2)
    phase2-2-item-reduction/00-efa-screening/output/efa-screening-items.csv   (EFA loadings, screening)
    phase2-2-item-reduction/00-efa-screening/output/items-after-screening.csv (stage 9: 49 items)
    phase3-validation/data/codebook/items.csv                                 (stage 10: 13 items)

Item codes differ between the phases (P0-26 in the team spreadsheets, P026 in LimeSurvey and
in phases 2 and 3; P40-26-A / P4026A). They are matched on the code without hyphens.
"""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

PHASE_DIR = Path(__file__).resolve().parent.parent
REPO_DIR = PHASE_DIR.parent
RAW = PHASE_DIR / "data" / "raw"
CODEBOOK = PHASE_DIR / "data" / "codebook"
SCREENING_ITEMS = REPO_DIR / "phase2-2-item-reduction" / "00-efa-screening" / "output" / "efa-screening-items.csv"
SCREENED_49 = REPO_DIR / "phase2-2-item-reduction" / "00-efa-screening" / "output" / "items-after-screening.csv"
VALIDATION_ITEMS = REPO_DIR / "phase3-validation" / "data" / "codebook" / "items.csv"

STAGE_LABELS = {
    1: "Merged pool P0+P1+P2+P3",
    2: "After internal review (pilot)",
    3: "After pilot (expert survey 2)",
    4: "After expert survey 2 (interview round 1)",
    5: "After interview round 1 (round 2)",
    6: "After interview round 2",
    7: "After round 3 (final revision)",
    8: "Exploratory survey (Prolific, EFA)",
    9: "After EFA screening (item reduction)",
    10: "Selected scale (validation)",
}
PHASE_OF_STAGE = {**{k: "1 Item development" for k in range(1, 8)}, 8: "2.1 Scale development",
                  9: "2.2 Item reduction", 10: "3 Validation"}
SOURCE_NAMES = {"P0": "experts' suggestions (expert survey 1, Task 2)", "P1": "UEQ+ scales",
                "P2": "other standardized questionnaires", "P3": "VA literature",
                "P4": "added in the cognitive interviews", "P9": "attention check"}
FACTOR_NAMES = {"task_cognition": "Task cognition (validation: Cognitive value)",
                "system": "System (validation: Intuitiveness)", "visualization": "Visualization"}


def key(code) -> str:
    """Code without hyphens or spaces, upper case: P0-26 -> P026, P40-26-A -> P4026A."""
    return re.sub(r"[^A-Z0-9]", "", str(code).upper())


def presence() -> pd.DataFrame:
    """One row per item and stage in which the item is present (stages 1-10)."""
    hist = pd.read_csv(RAW / "item-history.csv")
    pres = hist[hist["present"]][["item", "stage_order", "text", "decision"]].copy()
    team_code = {key(i): i for i in hist["item"].unique()}
    later = []
    if SCREENED_49.exists():
        for c in pd.read_csv(SCREENED_49)["code"]:
            later.append({"item": team_code.get(key(c), c), "stage_order": 9, "text": "", "decision": ""})
    if VALIDATION_ITEMS.exists():
        for _, r in pd.read_csv(VALIDATION_ITEMS).iterrows():
            later.append({"item": team_code.get(key(r["code"]), r["code"]), "stage_order": 10,
                          "text": r["wording"], "decision": ""})
    pres = pd.concat([pres, pd.DataFrame(later)], ignore_index=True)
    pres["source"] = pres["item"].str[:2]
    return pres


def available_stages() -> list[int]:
    stages = list(range(1, 9))
    if SCREENED_49.exists():
        stages.append(9)
    if VALIDATION_ITEMS.exists():
        stages.append(10)
    return stages


def expert_survey_2_stats() -> pd.DataFrame:
    """Mode (first tied value in expert order, as in 2025), mean, median, comments per statement."""
    path = RAW / "expert-survey-2_ratings.csv"
    if not path.exists():
        return pd.DataFrame(columns=["key"])
    ratings = pd.read_csv(path).set_index("expert")
    statements = pd.read_csv(CODEBOOK / "expert-survey-2_statements.csv").set_index("statement")
    comments = pd.read_csv(RAW / "expert-survey-2_comment-counts.csv").set_index("statement")["n_comments"]
    rows = []
    for s in ratings.columns:
        v = ratings[s].dropna().astype(int)
        counts = v.value_counts()
        tied = set(counts[counts == counts.max()].index)
        rows.append({"key": key(s), "es2_wording": statements.at[s, "text"],
                     "es2_mode": next(x for x in v if x in tied), "es2_mode_tie": len(tied) > 1,
                     "es2_mean": round(v.mean(), 2), "es2_median": v.median(), "es2_comments": int(comments.get(s, 0))})
    return pd.DataFrame(rows)


def trajectory() -> pd.DataFrame:
    """One row per item: source, topic, concept, stages, first and last stage, later-phase results."""
    pres = presence()
    hist = pd.read_csv(RAW / "item-history.csv")
    pool = pd.read_csv(RAW / "item-pool.csv").set_index("item")
    stages = available_stages()
    items = sorted(set(hist["item"]) | set(pres["item"]), key=lambda i: (i[:2], key(i)))
    in_stage = {s: set(pres.loc[pres["stage_order"] == s, "item"]) for s in stages}

    rows = []
    for item in items:
        present_in = [s for s in stages if item in in_stage[s]]
        row = {"item": item, "key": key(item), "source": item[:2],
               "topic": pool["topic"].get(item, ""), "concept": pool["concept"].get(item, ""),
               "optional_in_pool": bool(pool["optional"].get(item, False))}
        for s in stages:
            row[f"stage_{s}"] = item in in_stage[s]
        row["first_stage"] = present_in[0] if present_in else None
        row["last_stage"] = present_in[-1] if present_in else None
        row["in_final_scale"] = bool(10 in present_in)
        rows.append(row)
    out = pd.DataFrame(rows)

    out = out.merge(expert_survey_2_stats(), on="key", how="left")
    if SCREENING_ITEMS.exists():
        scr = pd.read_csv(SCREENING_ITEMS)
        scr = pd.DataFrame({"key": scr["code"].map(key), "efa_factor": scr["factor"],
                            "efa_loading": scr["primary_loading"], "efa_second_loading": scr["second_loading"],
                            "efa_second_factor": scr["second_factor"], "missing_pct": scr["missing_pct"],
                            "screening_decision": scr["decision"],
                            "screening_reason": scr["reason"].fillna("").str.replace(r"\s+", " ", regex=True)})
        out = out.merge(scr, on="key", how="left")
    if VALIDATION_ITEMS.exists():
        val = pd.read_csv(VALIDATION_ITEMS)
        val = pd.DataFrame({"key": val["code"].map(key), "validation_factor": val["factor"],
                            "validation_short_name": val["short_name"], "validation_wording": val["wording"]})
        out = out.merge(val, on="key", how="left")
    return out
