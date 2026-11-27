"""Build the anonymised expert-survey data of phase 1 from the LimeSurvey exports.

Inputs (restricted, never committed), in phase1-item-development/restricted-data/limesurvey/:
    results-survey<ID>.xlsx       responses, exported with "Question code & question text"
                                  headers and full answer texts
    limesurvey_survey_<ID>.lss    survey structure
They are listed, with their checksums, in restricted-data/MANIFEST.csv; a warning is printed if a
file differs from the recorded version.

Outputs (committed), in phase1-item-development/data/:
    Expert survey 1 (654492) and its pilot (654491):
        raw/expert-survey-1_ratings.csv            expert x 15 topics (1-5)
        raw/expert-survey-1_participants.csv       expert code, gender, years, expertise levels
        raw/expert-survey-1_comment-counts.csv     number of comments per topic
        raw/expert-survey-1_suggestion-counts.csv  number of missing-topic suggestions per expert (Task 2)
        raw/expert-survey-1-pilot_ratings.csv      pilot expert x 15 topics
        codebook/expert-survey-1_topics.csv        topic code, name, wording shown to the experts
    Expert survey 2 (718131):
        raw/expert-survey-2_ratings.csv            expert x 83 statements (1-5)
        raw/expert-survey-2_participants.csv       expert code, pilot flag, gender, years, expertise levels
        raw/expert-survey-2_comment-counts.csv     number of comments per statement
        codebook/expert-survey-2_statements.csv    statement code, team code, text, display order

Only submitted responses are kept (decision of 2026-11-24). Experts are coded in increasing
LimeSurvey Response ID order (survey 1: A01, A02, ...; pilot of survey 1: AP1, ...; survey 2:
E01, E02, ...). The order matters for survey 2: the 2025 analysis computed the mode with
MODE.SNGL over the experts in this order (see 03_expert-survey-2/README.md). Response IDs,
dates, seeds, names and all free-text answers (comments, suggestions) are dropped.

Run from the repository root:
    python phase1-item-development/data/prepare_expert_data.py
"""

from __future__ import annotations

import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import restricted_data  # noqa: E402  (repository root)

PHASE_DIR = Path(__file__).resolve().parent.parent
EXPORTS_DIR = PHASE_DIR / "restricted-data" / "limesurvey"
DATA_DIR = PHASE_DIR / "data"

RELEVANCE_LEVELS = {
    "Never relevant": 1,
    "Not often relevant": 2,
    "Sometimes relevant": 3,
    "Some of the times relevant": 3,  # wording of level 3 in the pilot of survey 1 (654491)
    "Frequently relevant": 4,
    "Always relevant": 5,
}

PROFILE_COLUMNS = {
    "QGender": "gender",
    "E01Expertise": "years_experience_va",
    "E02Expertise": "expertise_usability_evaluation",
    "E03Expertise": "expertise_va_system_design",
}

# The first two submitted responses of survey 2 (Response IDs 9 and 12, 16 and 19 July 2025)
# are the pilot of that survey; the team kept them (slides of 2025-07-24 and 2025-09-04).
SURVEY_2_PILOT_RESPONSE_IDS = {9, 12}


# --------------------------------------------------------------------------- helpers

def find_input(pattern: str) -> Path:
    """The restricted export matching a glob pattern (exactly one), checked against the manifest."""
    matches = sorted(EXPORTS_DIR.glob(pattern))
    if not matches:
        sys.exit(f"No file matching {pattern!r} in {EXPORTS_DIR}\n"
                 f"See {EXPORTS_DIR.parent / 'README.md'}.")
    if len(matches) > 1:
        sys.exit(f"More than one file matches {pattern!r} in {EXPORTS_DIR}: keep only the one in MANIFEST.csv.")
    return restricted_data.require(PHASE_DIR, f"limesurvey/{matches[0].name}")


def read_export(pattern: str) -> pd.DataFrame:
    """Submitted responses of a LimeSurvey export, columns renamed to the question codes."""
    df = pd.read_excel(find_input(pattern))
    df.columns = [str(c).split(". ", 1)[0] for c in df.columns]
    if "submitdate" not in df.columns:
        sys.exit(f"{pattern}: export without question codes; re-export with 'Question code & question text'.")
    return df[df["submitdate"].notna()].sort_values("id").reset_index(drop=True)


def to_levels(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.apply(lambda col: col.map(RELEVANCE_LEVELS))
    unknown = frame.notna() & out.isna()
    if unknown.any().any():
        sys.exit(f"Answer labels not in RELEVANCE_LEVELS: {sorted(set(frame.values[unknown.values]))}")
    return out


def count_text(series: pd.Series) -> int:
    return int(series.dropna().astype(str).str.strip().ne("").sum())


def clean_html(text: str | None) -> str:
    text = re.sub(r"<[^>]+>", " ", text or "")
    text = text.replace("&nbsp;", " ").replace("\xa0", " ").replace("&amp;", "&")
    return re.sub(r"\s+", " ", text).strip()


class Structure:
    """Questions and subquestions of a .lss file."""

    def __init__(self, pattern: str):
        root = ET.parse(find_input(pattern)).getroot()

        def rows(section):
            node = root.find(section)
            return [] if node is None else list(node.find("rows"))

        def field(row, name):
            el = row.find(name)
            return el.text if el is not None else None

        texts = {field(r, "qid"): field(r, "question") for r in rows("question_l10ns")
                 if field(r, "language") in (None, "en")}
        self.questions = {field(r, "title"): {"qid": field(r, "qid"), "text": texts.get(field(r, "qid"), ""),
                                              "order": int(field(r, "question_order") or 0)}
                          for r in rows("questions")}
        self.subquestions = [{"parent_qid": field(r, "parent_qid"), "title": field(r, "title"),
                              "text": texts.get(field(r, "qid"), ""),
                              "order": int(field(r, "question_order") or 0)} for r in rows("subquestions")]

    def children(self, parent_title: str) -> list[dict]:
        qid = self.questions[parent_title]["qid"]
        return sorted((s for s in self.subquestions if s["parent_qid"] == qid), key=lambda s: s["order"])


def team_code(limesurvey_code: str) -> str:
    """P012A -> P0-12-A, P06 -> P0-6, P209 -> P2-09 (codes used in the team spreadsheets)."""
    m = re.fullmatch(r"P(\d)(\d+)([A-Z]?)", limesurvey_code)
    if not m:
        raise ValueError(f"Unexpected statement code: {limesurvey_code}")
    pool, number, letter = m.groups()
    return f"P{pool}-{number}" + (f"-{letter}" if letter else "")


def profile(df: pd.DataFrame, codes: list[str]) -> pd.DataFrame:
    out = pd.DataFrame({"expert": codes})
    for src, dst in PROFILE_COLUMNS.items():
        if src in df.columns:
            out[dst] = df[src].values
    out["gender"] = out["gender"].str.replace(r"\s*\(including trans (wo)?man\)", "", regex=True)
    return out


def write(frame: pd.DataFrame, relative: str) -> None:
    path = DATA_DIR / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, index=False)


# --------------------------------------------------------------------------- survey 1

def topic_codebook() -> pd.DataFrame:
    """The 15 topics (UEQ+ scales) of Task 1 of survey 1, with the wording shown to the experts."""
    st = Structure("limesurvey_survey_654492*.lss")
    rows = []
    for title, q in st.questions.items():
        m = re.fullmatch(r"S(\d\d)\w+", title)
        if not m:
            continue
        text = clean_html(q["text"])
        name, _, wording = text.partition("ℹ️")
        rows.append({"topic": f"S{m.group(1)}", "limesurvey_code": title, "name": name.strip(),
                     "wording": wording.strip(), "display_order": q["order"]})
    return pd.DataFrame(rows).sort_values("topic").reset_index(drop=True)


def prepare_survey_1(topics: pd.DataFrame) -> None:
    df = read_export("results-survey654492*.xlsx")
    codes = [f"A{i:02d}" for i in range(1, len(df) + 1)]

    ratings = to_levels(df[list(topics["limesurvey_code"])])
    ratings.columns = list(topics["topic"])
    ratings.insert(0, "expert", codes)

    comments = pd.DataFrame({"topic": topics["topic"],
                             "n_comments": [count_text(df[f"{c}[comment]"]) for c in topics["limesurvey_code"]]})

    missing_cols = [c for c in df.columns if re.fullmatch(r"Missing1\[S\d\d\]", c)]
    suggestions = pd.DataFrame({"expert": codes,
                                "n_suggestions": [count_text(row) for _, row in df[missing_cols].iterrows()]})

    write(ratings, "raw/expert-survey-1_ratings.csv")
    write(profile(df, codes), "raw/expert-survey-1_participants.csv")
    write(comments, "raw/expert-survey-1_comment-counts.csv")
    write(suggestions, "raw/expert-survey-1_suggestion-counts.csv")
    print(f"Survey 1 (654492): {len(df)} submitted responses, {len(topics)} topics, "
          f"{int(ratings.iloc[:, 1:].isna().sum().sum())} missing ratings, "
          f"{int(comments['n_comments'].sum())} comments, {int(suggestions['n_suggestions'].sum())} suggestion fields filled.")


def prepare_survey_1_pilot(topics: pd.DataFrame) -> None:
    df = read_export("results-survey654491*.xlsx")
    cols = {f"S{m.group(1)}": c for c in df.columns
            if (m := re.fullmatch(r"QTopicsRelevance\[S(\d\d)\w+\]", c))}
    if sorted(cols) != list(topics["topic"]):
        sys.exit(f"Pilot topics differ from survey 1: {sorted(cols)}")
    ratings = to_levels(df[[cols[t] for t in topics["topic"]]])
    ratings.columns = list(topics["topic"])
    ratings.insert(0, "expert", [f"AP{i}" for i in range(1, len(df) + 1)])
    write(ratings, "raw/expert-survey-1-pilot_ratings.csv")
    print(f"Pilot of survey 1 (654491): {len(df)} submitted responses.")


# --------------------------------------------------------------------------- survey 2

def prepare_survey_2() -> None:
    df = read_export("results-survey718131*.xlsx")
    st = Structure("limesurvey_survey_718131*.lss")
    statements = pd.DataFrame([{"statement": s["title"], "team_code": team_code(s["title"]),
                                "text": clean_html(s["text"]), "display_order": s["order"]}
                               for s in st.children("rating")])

    rating_cols = [f"rating[{s}]" for s in statements["statement"]]
    missing = [c for c in rating_cols if c not in df.columns]
    if missing:
        sys.exit(f"Columns missing in the export: {missing}")
    ratings = to_levels(df[rating_cols])
    ratings.columns = list(statements["statement"])
    codes = [f"E{i:02d}" for i in range(1, len(df) + 1)]
    ratings.insert(0, "expert", codes)

    participants = profile(df, codes)
    participants.insert(1, "pilot", df["id"].isin(SURVEY_2_PILOT_RESPONSE_IDS).astype(int).values)
    found = set(df.loc[participants["pilot"] == 1, "id"])
    if found != SURVEY_2_PILOT_RESPONSE_IDS:
        sys.exit(f"Pilot Response IDs not found among submitted responses: {SURVEY_2_PILOT_RESPONSE_IDS - found}")

    counts = pd.DataFrame({"statement": statements["statement"],
                           "n_comments": [count_text(df[f"comments{s}"]) if f"comments{s}" in df.columns else 0
                                          for s in statements["statement"]]})

    write(ratings, "raw/expert-survey-2_ratings.csv")
    write(participants, "raw/expert-survey-2_participants.csv")
    write(counts, "raw/expert-survey-2_comment-counts.csv")
    write(statements, "codebook/expert-survey-2_statements.csv")
    print(f"Survey 2 (718131): {len(df)} submitted responses, {len(statements)} statements, "
          f"{int(ratings.iloc[:, 1:].isna().sum().sum())} missing ratings, "
          f"{int(participants['pilot'].sum())} pilot responses, {int(counts['n_comments'].sum())} comments.")


if __name__ == "__main__":
    topics = topic_codebook()
    write(topics, "codebook/expert-survey-1_topics.csv")
    prepare_survey_1(topics)
    prepare_survey_1_pilot(topics)
    prepare_survey_2()
