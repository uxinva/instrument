"""Extract the item sources and the item history of phase 1 from the team spreadsheets.

Inputs (Google Sheets downloaded as .xlsx into phase1-item-development/tmp-data/old-analysis/;
not versioned):
    Items Historic.xlsx                       Google Sheet "Items Historic"
    Task2SuggestedItemsAnalysis250127.xlsx    Google Sheet "Task2SuggestedItemsAnalysis250127"
    Task 1 - CommentsAnalysis250127.xlsx      Google Sheet "Task 1 - CommentsAnalysis250127"

Outputs (committed), in phase1-item-development/data/raw/:
    item-history.csv            one row per item and stage: item, stage, present, text, decision
    item-pool.csv               the 95 items of the merged pool P0+P1+P2+P3: source, topic, concept
    source-p0-suggestions.csv   expert suggestions (Task 2 of survey 1) coded into topic and concept,
                                and their outcome (item, optional item, removed); texts not included
    source-p1-ueqplus.csv       UEQ+ items of the 15 topics compared with P0 (P1<>P0)
    source-p2-scales.csv        items of other standardized scales compared with P0+P1 (P2<>P1+P0)
    source-p3-literature.csv    terms extracted from the VA literature and their final topic-concept
    concept-occurrences.csv     number of occurrences of each topic-concept in P0, P1, P2 and P3
    expert-survey-1_comment-coding.csv   open coding of the Task 1 comments of expert survey 1: one row
                                per coded segment, topic, rating, one 0/1 column per code category
                                (comment texts not included)
    expert-survey-1_task2-coding.csv     the two independent codings of the Task 2 answers: whether
                                each answer names an item or a topic (coder A, coder B) and the
                                consolidation status (texts and concept labels not included)

Item texts of the scales (P1, P2), the excerpts of the papers (P3), the expert suggestions and
the experts' comments are not copied. Item codes follow the team spreadsheets (P0-12-A).

Run from the repository root:
    python phase1-item-development/data/prepare_item_sources.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pandas as pd

PHASE_DIR = Path(__file__).resolve().parent.parent
OLD_DIR = PHASE_DIR / "tmp-data" / "old-analysis"
RAW_DIR = PHASE_DIR / "data" / "raw"
ITEMS_HISTORIC = OLD_DIR / "Items Historic.xlsx"
TASK2 = OLD_DIR / "Task2SuggestedItemsAnalysis250127.xlsx"
TASK1 = OLD_DIR / "Task 1 - CommentsAnalysis250127.xlsx"
TOPICS = PHASE_DIR / "data" / "codebook" / "expert-survey-1_topics.csv"

# Code categories of the open coding of the Task 1 comments (columns G-P of the sheet
# "Comments & Ratings - Task1 Open"), with the names used in the outputs.
COMMENT_CODES = {
    "Specific item commented on": "specific_item",
    "Reason for importance": "reason_importance",
    "Reason for irrelvance": "reason_irrelevance",
    "Tradeoffs to consider": "tradeoff",
    "Dependence of the topic on other factors": "context_dependence",
    "Interpretation of the topic (concept)": "interpretation",
    "problem rating this topic": "rating_problem",
    "Similarity to other items/topics": "overlap_other_topic",
    "Suggesting new items": "new_item_suggested",
}

# Sheet "Items Historic": one row per item; the stages are pairs of columns (item code, text),
# oldest on the right. Zero-based column indexes; the decision column holds the team's label.
STAGES = [
    # order, stage, label used in the tables, code col, text col, decision col
    (1, "pool", "Merged pool P0+P1+P2+P3", 60, 61, None),
    (2, "internal-review", "After internal review (pilot version)", 56, 57, 58),
    (3, "pilot", "After pilot (expert survey 2 version)", 52, 53, 54),
    (4, "expert-survey-2", "After expert survey 2 (cognitive interview round 1)", 46, 47, None),
    (5, "interview-round-1", "After cognitive interview round 1", 40, 41, 42),
    (6, "interview-round-2", "After cognitive interview round 2", 34, 35, 36),
    (7, "round-3", "After round 3 (final team revision)", 29, 30, 31),
    (8, "prolific", "Exploratory survey (Prolific)", 24, 25, 26),
]
COL_ID, COL_TOPIC, COL_CONCEPT = 1, 2, 3


def need(path: Path) -> None:
    if not path.exists():
        sys.exit(f"Missing input: {path}\nDownload the Google Sheet as .xlsx into {OLD_DIR}.")


_WORKBOOKS: dict = {}


def sheet(path: Path, name: str) -> list[tuple]:
    """Rows of one sheet, padded to the same width. Each workbook is opened only once."""
    import openpyxl
    if path not in _WORKBOOKS:
        print(f"Reading {path.name} ...", flush=True)
        _WORKBOOKS[path] = openpyxl.load_workbook(path, data_only=True)
    ws = _WORKBOOKS[path][name]
    rows = [tuple(r) for r in ws.iter_rows(values_only=True)]
    width = max((len(r) for r in rows), default=0)
    return [r + (None,) * (width - len(r)) for r in rows]


def text(v) -> str:
    return "" if v is None else re.sub(r"\s+", " ", str(v)).strip()


def present(item_text: str, decision: str) -> bool:
    """An item is in a stage when the stage has a text that is not '----' and not a removal."""
    if item_text in ("", "----", "-") or item_text.upper().startswith("REMOVE"):
        return False
    return not decision.lower().startswith("remove")


def normalise_code(code: str) -> str:
    """Codes of the round columns drop the hyphen before a final letter (P0-22A); restore it (P0-22-A)."""
    code = text(code)
    m = re.fullmatch(r"(P\d+-\d+)-?([A-Z])", code)
    return f"{m.group(1)}-{m.group(2)}" if m else code


def item_history() -> pd.DataFrame:
    rows = [r for r in sheet(ITEMS_HISTORIC, "Items Historic")[1:] if any(r[c] for _, _, _, c, _, _ in STAGES)]
    out = []
    for r in rows:
        for order, stage, _, c_id, c_text, c_dec in STAGES:
            # The code of the stage column is used, not the code of the row: in the interview
            # rounds the text of P3-05 sits on the row of P3-03.
            code = normalise_code(r[c_id] or r[COL_ID])
            if not code:
                continue
            t, d = text(r[c_text]), text(r[c_dec]) if c_dec is not None else ""
            t = re.sub(r"^P\d+[A-Z]?-(?=\S)", "", t)  # Prolific column: "P026-I found it ..." -> "I found it ..."
            out.append({"item": code, "stage_order": order, "stage": stage, "present": present(t, d),
                        "optional": t.upper().startswith("OPTIONAL"), "text": t if present(t, d) else "",
                        "decision": d})
    df = pd.DataFrame(out)
    pres = df[df["present"]]
    dup = pres[pres.duplicated(["item", "stage"], keep=False)]
    if not dup.empty:
        sys.exit(f"Item present twice in the same stage: {dup[['item', 'stage']].values.tolist()}")
    # keep one row per item and stage (prefer the row where the item is present)
    return (df.sort_values(["item", "stage_order", "present"], ascending=[True, True, False])
              .drop_duplicates(["item", "stage"]).sort_values(["stage_order", "item"]).reset_index(drop=True))


def item_pool() -> pd.DataFrame:
    rows = [r for r in sheet(ITEMS_HISTORIC, "Items Historic")[1:] if r[60]]
    return pd.DataFrame([{"item": normalise_code(r[60]), "source": text(r[60])[:2],
                          "topic": text(r[COL_TOPIC]), "concept": text(r[COL_CONCEPT]),
                          "optional": text(r[61]).upper().startswith("OPTIONAL")} for r in rows])


def p0_suggestions() -> pd.DataFrame:
    rows = [r for r in sheet(TASK2, "ItemGeneration")[1:] if r[0] is not None]
    out = []
    for r in rows:
        final = text(r[7])
        outcome = ("removed" if final.upper().startswith("REMOVE") else
                   "optional item" if final.upper().startswith("OPTIONAL") else
                   "item" if final else "no decision")
        number = text(r[0])[:-2] if text(r[0]).endswith(".0") else text(r[0])
        out.append({"item": f"P0-{number}", "task2_answer": int(float(r[1])) if r[1] else None,
                    "concept": text(r[3]), "topic": text(r[4]), "status": text(r[5]), "outcome": outcome})
    return pd.DataFrame(out)


def p1_ueqplus() -> pd.DataFrame:
    rows = [r for r in sheet(ITEMS_HISTORIC, "P1<>P0")[1:] if r[2]]
    return pd.DataFrame([{"ueqplus_scale": text(r[0]), "recommendation": text(r[2]),
                          "new_concept": text(r[3]), "p0_topic": text(r[7]), "p0_concept": text(r[8])} for r in rows])


def p2_scales() -> pd.DataFrame:
    rows = sheet(ITEMS_HISTORIC, "P2<>P1+P0")[2:]
    out, scale, sub = [], "", ""
    for r in rows:
        if not r[2] and not r[3]:
            continue
        scale = text(r[0]) or scale  # the scale name is written only on its first row
        sub = text(r[1]) if r[0] or r[1] else sub
        out.append({"scale": scale, "subscale": sub, "classification": text(r[3]) or "not classified",
                    "topic": text(r[4]), "topic_p0_p1": text(r[5]), "new_topic": text(r[6]),
                    "concept": text(r[7]), "concept_p0_p1": text(r[8]), "new_concept": text(r[9])})
    return pd.DataFrame(out)


def p3_literature() -> pd.DataFrame:
    rows = [r for r in sheet(ITEMS_HISTORIC, "P3<>P0+P1+P2")[1:] if r[1] is not None]
    return pd.DataFrame([{"term_id": int(r[1]), "term": text(r[2]), "final_topic_concept": text(r[0]),
                          "ai_topic_concept": text(r[5]), "status": text(r[15])} for r in rows])


def comment_coding() -> pd.DataFrame:
    rows = sheet(TASK1, "Comments & Ratings - Task1 Open")
    header = [text(h) for h in rows[0]]
    col = {h: i for i, h in enumerate(header)}
    names = pd.read_csv(TOPICS).set_index("name")["topic"] if TOPICS.exists() else pd.Series(dtype=str)
    names.index = names.index.str.lower()
    levels = {"Never relevant": 1, "Not often relevant": 2, "Sometimes relevant": 3,
              "Frequently relevant": 4, "Always relevant": 5}
    out = []
    for r in rows[1:]:
        if not r[col["Comment"]]:
            continue
        name = text(r[col["Survey Question"]])
        rec = {"comment_id": int(float(r[col["Comment ID"]])), "topic": names.get(name.lower(), name),
               "topic_name": name, "rating": levels.get(text(r[col["Column 19"]]))}
        for src, dst in COMMENT_CODES.items():
            rec[dst] = int(bool(text(r[col[src]]))) if src in col else 0
        out.append(rec)
    return pd.DataFrame(out)


def task2_coding() -> pd.DataFrame:
    """Coder A: sheet "Task2-Concepts Classification" (columns H-J, consolidation status in V);
    coder B: sheet "Task2-Concepts Emanuele" (columns G-I). Rows are aligned by position and
    checked on the answer number."""
    is_num = lambda v: v is not None and re.fullmatch(r"\d+(\.0)?", str(v).strip())  # noqa: E731
    a = [r for r in sheet(TASK2, "Task2-Concepts Classification") if is_num(r[1])]
    b = [r for r in sheet(TASK2, "Task2-Concepts Emanuele") if is_num(r[0])]
    if [int(float(r[1])) for r in a] != [int(float(r[0])) for r in b]:
        sys.exit("The two Task 2 codings are not in the same order; check the sheets.")
    low = lambda v: text(v).lower()  # noqa: E731
    return pd.DataFrame([{"segment": i + 1, "task2_answer": int(float(ra[1])),
                          "item_or_topic_a": low(ra[9]), "item_or_topic_b": low(rb[8]),
                          "concept_coded_a": int(bool(text(ra[7]))), "concept_coded_b": int(bool(text(rb[6]))),
                          "status": low(ra[21])} for i, (ra, rb) in enumerate(zip(a, b))])


def concept_occurrences() -> pd.DataFrame:
    rows = [r for r in sheet(ITEMS_HISTORIC, "Concept Occurences")[1:] if r[0] not in (None, "")]
    return pd.DataFrame([{"topic_concept": text(r[0]), "p0": int(r[1] or 0), "p1": int(r[2] or 0),
                          "p2": int(r[3] or 0), "p3": int(r[4] or 0), "note": " ".join(text(x) for x in r[5:9] if x)}
                         for r in rows])


def main() -> None:
    need(ITEMS_HISTORIC)
    need(TASK2)
    need(TASK1)
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    builders = {
        "item-history.csv": item_history,
        "item-pool.csv": item_pool,
        "source-p0-suggestions.csv": p0_suggestions,
        "source-p1-ueqplus.csv": p1_ueqplus,
        "source-p2-scales.csv": p2_scales,
        "source-p3-literature.csv": p3_literature,
        "concept-occurrences.csv": concept_occurrences,
        "expert-survey-1_comment-coding.csv": comment_coding,
        "expert-survey-1_task2-coding.csv": task2_coding,
    }
    for name, build in builders.items():
        df = build()
        df.to_csv(RAW_DIR / name, index=False)
        print(f"{name}: {len(df)} rows", flush=True)


if __name__ == "__main__":
    main()
