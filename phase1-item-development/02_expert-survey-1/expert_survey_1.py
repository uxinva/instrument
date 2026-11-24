"""Step 02: analysis of the first expert survey (LimeSurvey 654492) and its pilot (654491).

Task 1: relevance of 15 topics of an existing UX questionnaire framework (UEQ+ scales), rated
from 1 = never relevant to 5 = always relevant, with an optional comment per topic.
Task 2: up to ten topics, adjective pairs or statements the experts missed (free text; only
the number of answers is in the repository; their coding into items is in step 04).

Reads the anonymised data in phase1-item-development/data/ and writes, to output/:
    participants-profile.csv      gender, years of experience, expertise levels (survey 1)
    response-summary.csv          started, submitted and incomplete responses; completion time
    topic-relevance.csv           per topic: n, median, mean, variance, SD, counts per level,
                                  comments, rank, relevant (mean >= 4)
    rating-counts.csv             number of ratings at each level (survey 1 and pilot)
    agreement-kendall.csv         Kendall's W of the 15 topics and of the stepwise exclusion
    pilot-topic-relevance.csv     the same topic table for the pilot (4 experts)
    task2-suggestions.csv         answers to Task 2: experts, fields filled, invalid answers
    table-topic-relevance.tex     LaTeX table of the topic relevance

Choices reproduced from the 2025 analysis (slides of 30 January and 6 February 2025):
- variance and SD with n - 1;
- a topic is kept as relevant when its mean is >= 4 (10 topics);
- Kendall's W with the correction for ties; agreement was considered acceptable above 0.4;
  the stepwise procedure (script by Emanuele) removes, at each step, the topic whose exclusion
  gives the highest W, until W > 0.4 (Attractiveness, then Dependability: W = 0.407).

--check compares the results with the values on the 2025 slides and with the ratings in a
local copy of the spreadsheet "Task 1 - CommentsAnalysis250127" (tmp-data/old-analysis/).

Run from the repository root:
    python phase1-item-development/02_expert-survey-1/expert_survey_1.py [--check]
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

STEP_DIR = Path(__file__).resolve().parent
PHASE_DIR = STEP_DIR.parent
DATA_DIR = PHASE_DIR / "data"
TMP_DIR = PHASE_DIR / "tmp-data"
OUT_DIR = STEP_DIR / "output"
OLD_TASK1 = TMP_DIR / "old-analysis" / "Task 1 - CommentsAnalysis250127.xlsx"

LEVELS = {1: "Never relevant", 2: "Not often relevant", 3: "Sometimes relevant",
          4: "Frequently relevant", 5: "Always relevant"}
RELEVANCE_THRESHOLD = 4.0   # topic kept when mean >= 4
KENDALL_TARGET = 0.4        # stepwise exclusion until W > 0.4

# Values on the 2025 slides (meeting of 30 January 2025, pp. 817-819 of the PDF export;
# meeting of 6 February 2025, p. 809; pilot, meeting of 16 January 2025, p. 841).
SLIDE_TOPICS = {  # name: (median, mean, variance)
    "Usefulness": (5, 4.76, 0.36), "Perspicuity": (5, 4.76, 0.24),
    "Trustworthiness of Content": (5, 4.41, 0.53), "Clarity": (5, 4.38, 0.52), "Trust": (5, 4.24, 0.80),
    "Intuitive use": (4, 4.30, 0.55), "Efficiency": (4, 4.22, 0.56), "Dependability": (4, 4.11, 0.82),
    "Quality of Content": (4, 4.05, 0.61), "Attractiveness": (4, 4.00, 0.94),
    "Visual Aesthetics": (4, 3.70, 0.77), "Value": (4, 3.54, 1.20), "Adaptability": (3, 3.24, 0.74),
    "Stimulation": (3, 3.22, 0.90), "Novelty": (3, 3.00, 0.56),
}
SLIDE_PROFILE = {"Woman": 13, "Man": 24, "years_mean": 12.9,
                 "usability": {"Expert": 18, "Competent": 15, "Limited": 4},
                 "va_design": {"Expert": 14, "Competent": 20, "Limited": 3}}
SLIDE_KENDALL = {"excluded": ["Attractiveness", "Dependability"], "W": 0.4071104}
SLIDE_PILOT_COUNTS = {1: 0, 2: 5, 3: 15, 4: 26, 5: 14}


# --------------------------------------------------------------------------- statistics

def kendall_w(ratings: pd.DataFrame) -> dict:
    """Kendall's W for m raters (rows) ranking n objects (columns), corrected for ties."""
    y = ratings.dropna()
    m, n = y.shape
    ranks = y.rank(axis=1)
    s = ((ranks.sum() - ranks.sum().mean()) ** 2).sum()
    ties = sum(((g := row.value_counts()) ** 3 - g).sum() for _, row in y.iterrows())
    w = 12 * s / (m ** 2 * (n ** 3 - n) - m * ties)
    chi2 = m * (n - 1) * w
    return {"raters": m, "topics": n, "W": w, "chi2": chi2, "df": n - 1, "p": stats.chi2.sf(chi2, n - 1)}


def stepwise_exclusion(ratings: pd.DataFrame, names: dict) -> list[dict]:
    cols = list(ratings.columns)
    steps = [{"step": 0, "excluded_topic": "", **kendall_w(ratings[cols])}]
    while steps[-1]["W"] <= KENDALL_TARGET and len(cols) > 2:
        best = max(cols, key=lambda c: kendall_w(ratings[[x for x in cols if x != c]])["W"])
        cols.remove(best)
        steps.append({"step": len(steps), "excluded_topic": names[best], **kendall_w(ratings[cols])})
    return steps


def topic_table(ratings: pd.DataFrame, topics: pd.DataFrame, comments: pd.DataFrame | None) -> pd.DataFrame:
    rows = []
    for t in ratings.columns:
        v = ratings[t].dropna()
        row = {"topic": t, "name": topics.at[t, "name"], "n": len(v), "median": v.median(), "mean": v.mean(),
               "variance": v.var(ddof=1), "sd": v.std(ddof=1)}
        for level in LEVELS:
            row[f"n_{level}"] = int((v == level).sum())
        if comments is not None:
            row["n_comments"] = int(comments.at[t, "n_comments"])
        rows.append(row)
    out = pd.DataFrame(rows).sort_values(["median", "mean"], ascending=False).reset_index(drop=True)
    out.insert(2, "rank", range(1, len(out) + 1))
    out["relevant"] = out["mean"] >= RELEVANCE_THRESHOLD
    return out


def profile_table(participants: pd.DataFrame) -> pd.DataFrame:
    prof = [("Experts (submitted responses)", len(participants))]
    prof += [(f"Gender: {g}", n) for g, n in participants["gender"].value_counts().items()]
    years = pd.to_numeric(participants["years_experience_va"], errors="coerce")
    prof += [("Years of experience with VA: mean", round(years.mean(), 1)),
             ("Years of experience with VA: median", years.median()),
             ("Years of experience with VA: min", years.min()), ("Years of experience with VA: max", years.max())]
    for col, label in [("expertise_usability_evaluation", "Usability evaluation"),
                       ("expertise_va_system_design", "VA system design")]:
        prof += [(f"{label}: {lvl}", n) for lvl, n in participants[col].value_counts().items()]
    return pd.DataFrame(prof, columns=["measure", "value"])


def response_summary() -> pd.DataFrame | None:
    """Started/submitted/incomplete and completion time, read from the raw export (tmp-data)."""
    files = sorted(TMP_DIR.glob("results-survey654492*.xlsx"), key=lambda p: p.stat().st_mtime)
    if not files:
        return None
    df = pd.read_excel(files[-1])
    df.columns = [str(c).split(". ", 1)[0] for c in df.columns]
    sub = df["submitdate"].notna()
    t1 = [c for c in df.columns if re.fullmatch(r"S\d\d\w+", c) and not c.endswith("Time")]
    minutes = pd.to_numeric(df.loc[sub, "interviewtime"], errors="coerce") / 60
    rows = [("Responses started", len(df)), ("Submitted (full) responses", int(sub.sum())),
            ("Incomplete responses", int((~sub).sum())),
            ("Incomplete responses with all Task 1 ratings", int((~sub & df[t1].notna().all(axis=1)).sum())),
            ("Completion time of submitted responses (min): median", round(minutes.median(), 1)),
            ("Completion time of submitted responses (min): mean", round(minutes.mean(), 1))]
    return pd.DataFrame(rows, columns=["measure", "value"])


def latex_topics(table: pd.DataFrame) -> str:
    lines = [
        r"\begin{table}[tbp]",
        r"\centering",
        r"\caption{Relevance of the 15 UEQ+ topics in the first expert survey ($n = 37$; "
        r"1 = never relevant, 5 = always relevant). Topics with a mean $\geq$ 4 were kept.}",
        r"\label{tab:topic-relevance}",
        r"\small",
        r"\begin{tabular}{lrrrc}",
        r"\toprule",
        r"Topic & Median & Mean & Variance & Kept \\",
        r"\midrule",
    ]
    for _, r in table.iterrows():
        kept = r"\checkmark" if r["relevant"] else ""
        lines.append(f"{r['name']} & {r['median']:g} & {r['mean']:.2f} & {r['variance']:.2f} & {kept} \\\\")
    lines += [r"\bottomrule", r"\end{tabular}", r"\end{table}", ""]
    return "\n".join(lines)


# --------------------------------------------------------------------------- check

def check(table, profile_df, steps, pilot_counts, ratings, topics) -> bool:
    ok = True

    def report(cond, msg):
        nonlocal ok
        if not cond:
            ok = False
            print(f"--check: DIFFERENT {msg}")

    by_name = table.set_index("name")
    for name, (med, mean, var) in SLIDE_TOPICS.items():
        r = by_name.loc[name]
        report(r["median"] == med and round(r["mean"], 2) == mean and round(r["variance"], 2) == var,
               f"{name}: slide {med}/{mean}/{var}, here {r['median']}/{r['mean']:.2f}/{r['variance']:.2f}")
    # Same order as the slide, except within exact ties (Perspicuity and Usefulness: 5 / 4.757).
    order_here = [(r["median"], round(r["mean"], 6)) for _, r in table.iterrows()]
    order_slide = [(by_name.loc[n, "median"], round(by_name.loc[n, "mean"], 6)) for n in SLIDE_TOPICS]
    report(order_here == order_slide, "order of the topics")
    p = dict(zip(profile_df["measure"], profile_df["value"]))
    report(p.get("Gender: Woman") == SLIDE_PROFILE["Woman"] and p.get("Gender: Man") == SLIDE_PROFILE["Man"], "gender")
    report(p.get("Years of experience with VA: mean") == SLIDE_PROFILE["years_mean"], "mean years")
    for k, v in SLIDE_PROFILE["usability"].items():
        report(p.get(f"Usability evaluation: {k}") == v, f"usability expertise {k}")
    for k, v in SLIDE_PROFILE["va_design"].items():
        report(p.get(f"VA system design: {k}") == v, f"VA design expertise {k}")
    excluded = [s["excluded_topic"] for s in steps[1:]]
    report(excluded == SLIDE_KENDALL["excluded"] and abs(steps[-1]["W"] - SLIDE_KENDALL["W"]) < 5e-8,
           f"Kendall exclusion: slide {SLIDE_KENDALL}, here {excluded} W = {steps[-1]['W']:.7f}")
    report(pilot_counts == SLIDE_PILOT_COUNTS, f"pilot counts: slide {SLIDE_PILOT_COUNTS}, here {pilot_counts}")

    if OLD_TASK1.exists():
        import openpyxl
        ws = openpyxl.load_workbook(OLD_TASK1, data_only=True)["Ratings"]
        rows = [r for r in ws.iter_rows(min_row=2, values_only=True) if r[0] is not None]
        labels = {v: k for k, v in LEVELS.items()}
        # Columns: topic rating in G, I, K, ... (every second column from index 6), 15 topics.
        old = pd.DataFrame([[labels.get(r[6 + 2 * i]) for i in range(15)] for r in rows],
                           columns=list(topics.index))
        report(old.shape == ratings.shape and (old.values == ratings.values).all(),
               "ratings differ from the sheet 'Ratings' of Task 1 - CommentsAnalysis250127")
        print(f"--check: compared the 37 x 15 ratings with {OLD_TASK1.name}.")
    else:
        print(f"--check: {OLD_TASK1.name} not found; ratings not compared with the spreadsheet.")
    print("--check: all values agree with the 2025 slides." if ok else "--check: differences found.")
    return ok


# --------------------------------------------------------------------------- main

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="compare with the 2025 slides and spreadsheet")
    args = parser.parse_args()

    topics = pd.read_csv(DATA_DIR / "codebook" / "expert-survey-1_topics.csv").set_index("topic")
    ratings = pd.read_csv(DATA_DIR / "raw" / "expert-survey-1_ratings.csv").set_index("expert")
    pilot = pd.read_csv(DATA_DIR / "raw" / "expert-survey-1-pilot_ratings.csv").set_index("expert")
    participants = pd.read_csv(DATA_DIR / "raw" / "expert-survey-1_participants.csv")
    comments = pd.read_csv(DATA_DIR / "raw" / "expert-survey-1_comment-counts.csv").set_index("topic")
    suggestions = pd.read_csv(DATA_DIR / "raw" / "expert-survey-1_suggestion-counts.csv")
    OUT_DIR.mkdir(exist_ok=True)

    profile_df = profile_table(participants)
    profile_df.to_csv(OUT_DIR / "participants-profile.csv", index=False)

    summary = response_summary()
    if summary is not None:
        summary.to_csv(OUT_DIR / "response-summary.csv", index=False)
    else:
        print("response-summary.csv not written: the raw export is not in tmp-data/.")

    table = topic_table(ratings, topics, comments)
    table.to_csv(OUT_DIR / "topic-relevance.csv", index=False, float_format="%.6g")
    (OUT_DIR / "table-topic-relevance.tex").write_text(latex_topics(table), encoding="utf-8")
    topic_table(pilot, topics, None).to_csv(OUT_DIR / "pilot-topic-relevance.csv", index=False, float_format="%.6g")

    counts = {k: int((ratings.values == k).sum()) for k in LEVELS}
    pilot_counts = {k: int((pilot.values == k).sum()) for k in LEVELS}
    pd.DataFrame([{"level": k, "label": LEVELS[k], "survey_1": counts[k], "pilot": pilot_counts[k]} for k in LEVELS]) \
        .to_csv(OUT_DIR / "rating-counts.csv", index=False)

    names = topics["name"].to_dict()
    steps = stepwise_exclusion(ratings, names)
    kendall = pd.DataFrame(steps)
    kendall.insert(0, "sample", "survey 1")
    pilot_w = {"sample": "pilot", "step": 0, "excluded_topic": "", **kendall_w(pilot)}
    pd.concat([kendall, pd.DataFrame([pilot_w])]).to_csv(OUT_DIR / "agreement-kendall.csv", index=False,
                                                          float_format="%.7g")

    n_filled = int(suggestions["n_suggestions"].sum())
    pd.DataFrame([("Experts who answered Task 2", int((suggestions["n_suggestions"] > 0).sum())),
                  ("Answer fields filled", n_filled),
                  ("Experts with 1, 2, 3, ... answers",
                   "; ".join(f"{k}: {v}" for k, v in sorted(suggestions["n_suggestions"].value_counts().items())))],
                 columns=["measure", "value"]).to_csv(OUT_DIR / "task2-suggestions.csv", index=False)

    print(f"Experts: {len(ratings)} (pilot: {len(pilot)}); topics: {ratings.shape[1]}")
    print("Relevant topics (mean >= 4):", ", ".join(table.loc[table["relevant"], "name"]))
    print(f"Kendall's W, 15 topics: {steps[0]['W']:.3f} (chi2({steps[0]['df']}) = {steps[0]['chi2']:.1f}, "
          f"p = {steps[0]['p']:.2g}); stepwise: " +
          ", ".join(f"without {s['excluded_topic']} W = {s['W']:.4f}" for s in steps[1:]))
    print(f"Pilot: rating counts {pilot_counts}; W = {pilot_w['W']:.3f}")
    print(f"Task 2: {n_filled} answer fields filled by {int((suggestions['n_suggestions'] > 0).sum())} experts")

    if args.check:
        sys.exit(0 if check(table, profile_df, steps, pilot_counts, ratings, topics) else 1)


if __name__ == "__main__":
    main()
