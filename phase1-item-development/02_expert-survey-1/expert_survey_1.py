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
    task2-suggestions.csv         answers to Task 2: experts, fields filled, non-answers
    agreement-icc.csv             ICC of the 15 topics (two-way, average of the 37 experts), consistency and
                                  absolute agreement, with 95% confidence intervals
    comment-coding-by-topic.csv   open coding of the Task 1 comments: coded segments per topic and code
    task2-coding-agreement.csv    agreement of the two coders on "item or topic" for the Task 2 answers
    table-topic-relevance.tex     LaTeX table of the topic relevance (median, mean, variance, % rated 4-5,
                                  Kendall's W without the topic, comments, kept)
    table-comment-coding.tex      LaTeX table of the comment codes per topic
    table-removed-topics.tex      LaTeX table of the five topics that were not kept, with the reasons
    figure-topic-relevance.pdf/.png  distribution of the ratings of the 15 topics (diverging bars)
    ../tmp-data/expert-survey-1_comments-of-removed-topics.csv   the comments on the five removed topics,
                                  to choose quotations (written only if the raw export is present; not
                                  versioned)

Choices reproduced from the 2025 analysis (slides of 30 January and 6 February 2025):
- variance and SD with n - 1;
- a topic is kept as relevant when its mean is >= 4 (10 topics);
- Kendall's W with the correction for ties; agreement was considered acceptable above 0.4;
  the stepwise procedure (script by Emanuele) removes, at each step, the topic whose exclusion
  gives the highest W, until W > 0.4 (Attractiveness, then Dependability: W = 0.407).

--check compares the results with the values on the 2025 slides and with the ratings in a
local copy of the spreadsheet "Task 1 - CommentsAnalysis250127" (restricted-data/team-sheets/).

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
TMP_DIR = PHASE_DIR / "tmp-data"  # scratch files only (not versioned)
RESTRICTED = PHASE_DIR / "restricted-data"  # records that cannot be published (see its MANIFEST.csv)
EXPORTS_DIR = RESTRICTED / "limesurvey"
OUT_DIR = STEP_DIR / "output"
OLD_TASK1 = RESTRICTED / "team-sheets" / "Task 1 - CommentsAnalysis250127.xlsx"

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

# Reasons for not keeping the five topics with a mean below 4 (team decision, meeting of
# 6 February 2025; summary of the qualitative analysis of the comments).
REMOVAL_REASONS = {
    "Visual Aesthetics": "Overlaps with Attractiveness",
    "Value": "Interpreted in inconsistent ways; its items did not seem to describe the topic",
    "Adaptability": "Depends on the system and its context of use",
    "Stimulation": "Not a frequently desired quality in daily use; depends on the usage pattern",
    "Novelty": "Rarely relevant; other qualities (effectiveness, efficiency, learnability) matter more",
}
CODE_LABELS = {
    "reason_irrelevance": "Reason for irrelevance", "reason_importance": "Reason for importance",
    "context_dependence": "Depends on context", "specific_item": "Comment on a specific item",
    "overlap_other_topic": "Overlap with another topic", "tradeoff": "Trade-off",
    "rating_problem": "Difficulty in rating", "new_item_suggested": "New item suggested",
    "interpretation": "Interpretation of the topic",
}


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
               "variance": v.var(ddof=1), "sd": v.std(ddof=1), "pct_rated_4_5": 100 * (v >= 4).mean(),
               "kendall_w_without_topic": kendall_w(ratings.drop(columns=t))["W"]}
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


def icc_two_way(matrix: np.ndarray, alpha: float = 0.05) -> list[dict]:
    """ICC for n subjects (rows) rated by k raters (columns): two-way model, average of the k
    ratings, consistency and absolute agreement, with confidence intervals as in irr::icc
    (McGraw and Wong, 1996)."""
    n, k = matrix.shape
    g = matrix.mean()
    msr = k * ((matrix.mean(axis=1) - g) ** 2).sum() / (n - 1)
    msc = n * ((matrix.mean(axis=0) - g) ** 2).sum() / (k - 1)
    resid = matrix - matrix.mean(axis=1, keepdims=True) - matrix.mean(axis=0, keepdims=True) + g
    mse = (resid ** 2).sum() / ((n - 1) * (k - 1))
    f = msr / mse
    df1, df2 = n - 1, (n - 1) * (k - 1)
    out = []
    icc_c = (msr - mse) / msr
    fl, fu = f / stats.f.ppf(1 - alpha / 2, df1, df2), f * stats.f.ppf(1 - alpha / 2, df2, df1)
    out.append({"type": "consistency, ICC(C,k)", "icc": icc_c, "ci_low": 1 - 1 / fl, "ci_high": 1 - 1 / fu,
                "F": f, "df1": df1, "df2": df2, "p": stats.f.sf(f, df1, df2)})
    icc_a = (msr - mse) / (msr + (msc - mse) / n)
    a = k * icc_a / (n * (1 - icc_a))
    b = 1 + k * icc_a * (n - 1) / (n * (1 - icc_a))
    v = (a * msc + b * mse) ** 2 / ((a * msc) ** 2 / (k - 1) + (b * mse) ** 2 / df2)
    f_l, f_u = stats.f.ppf(1 - alpha / 2, n - 1, v), stats.f.ppf(1 - alpha / 2, v, n - 1)
    lo = n * (msr - f_l * mse) / (f_l * (k * msc + (k * n - k - n) * mse) + n * msr)
    hi = n * (f_u * msr - mse) / (k * msc + (k * n - k - n) * mse + n * f_u * msr)
    lo, hi = lo * k / (1 + lo * (k - 1)), hi * k / (1 + hi * (k - 1))
    out.append({"type": "absolute agreement, ICC(A,k)", "icc": icc_a, "ci_low": lo, "ci_high": hi,
                "F": f, "df1": df1, "df2": v, "p": stats.f.sf(f, df1, v)})
    for o in out:
        o.update({"subjects_topics": n, "raters_experts": k})
    return out


def comment_coding_table(coding: pd.DataFrame, topics: pd.DataFrame) -> pd.DataFrame:
    codes = [c for c in CODE_LABELS if c in coding.columns]
    tab = coding.groupby("topic")[codes].sum()
    tab.insert(0, "segments", coding.groupby("topic").size())
    tab.insert(0, "comments", coding.groupby("topic")["comment_id"].nunique())
    tab = tab.reindex(topics.index).fillna(0).astype(int)
    tab.insert(0, "name", topics["name"])
    total = tab.drop(columns="name").sum()
    tab.loc["total"] = ["Total", *total.tolist()]
    return tab


def latex_comment_coding(tab: pd.DataFrame, table: pd.DataFrame) -> str:
    codes = [c for c in CODE_LABELS if c in tab.columns and tab.loc["total", c] > 0]
    order = list(table["topic"]) + ["total"]
    head = " & ".join([r"Topic", "Comm.", "Seg."] + [rf"\rotatebox{{90}}{{{CODE_LABELS[c]}}}" for c in codes])
    lines = [r"\begin{table}[tbp]", r"\centering",
             r"\caption{Open coding of the comments on the 15 topics (first expert survey): number of comments, "
             r"coded segments and segments per code. Topics in the order of Table~\ref{tab:topic-relevance}.}",
             r"\label{tab:comment-coding}", r"\footnotesize", r"\setlength{\tabcolsep}{3pt}",
             r"\resizebox{\columnwidth}{!}{%",
             r"\begin{tabular}{l" + "r" * (2 + len(codes)) + "}", r"\toprule", head + r" \\", r"\midrule"]
    for t in order:
        r = tab.loc[t]
        if t == "total":
            lines.append(r"\midrule")
        lines.append(" & ".join([str(r["name"]), str(r["comments"]), str(r["segments"])] +
                                [str(r[c]) if r[c] else "" for c in codes]) + r" \\")
    lines += [r"\bottomrule", r"\end{tabular}}", r"\end{table}", ""]
    return "\n".join(lines)


def latex_removed_topics(table: pd.DataFrame, tab: pd.DataFrame) -> str:
    removed = table[~table["relevant"]].sort_values("mean", ascending=False)
    lines = [r"\begin{table*}[tbp]", r"\centering",
             r"\caption{Topics not kept after the first expert survey: mean relevance, share of ratings 4--5, "
             r"number of comments, the most frequent codes of the comments and the reason for the decision.}",
             r"\label{tab:removed-topics}", r"\footnotesize",
             r"\begin{tabular}{lrrrp{4.2cm}p{6.4cm}}", r"\toprule",
             r"Topic & Mean & \% 4--5 & Comm. & Main codes & Reason \\", r"\midrule"]
    codes = [c for c in CODE_LABELS if c in tab.columns and c not in ("specific_item", "reason_importance")]
    for _, r in removed.iterrows():
        row = tab.loc[r["topic"]]
        main = sorted(((row[c], CODE_LABELS[c]) for c in codes if row[c] > 0), reverse=True)[:2]
        main_txt = "; ".join(f"{lab.lower()} ({n})" for n, lab in main) or "--"
        lines.append(f"{r['name']} & {r['mean']:.2f} & {r['pct_rated_4_5']:.0f} & {row['comments']} & "
                     f"{main_txt} & {REMOVAL_REASONS.get(r['name'], '')} \\\\")
    lines += [r"\bottomrule", r"\end{tabular}", r"\end{table*}", ""]
    return "\n".join(lines)


def figure_topic_relevance(table: pd.DataFrame, path_stem: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    order = table.sort_values(["mean"], ascending=True)
    colors = {1: "#b2182b", 2: "#ef8a62", 3: "#bdbdbd", 4: "#67a9cf", 5: "#2166ac"}
    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    y = range(len(order))
    n = order["n"].values
    pct = {lvl: 100 * order[f"n_{lvl}"].values / n for lvl in LEVELS}
    left = -(pct[1] + pct[2] + pct[3] / 2)
    for lvl in LEVELS:
        ax.barh(list(y), pct[lvl], left=left, color=colors[lvl], edgecolor="white", linewidth=0.5,
                label=LEVELS[lvl], height=0.72)
        left = left + pct[lvl]
    ax.axvline(0, color="#333333", linewidth=0.8)
    labels = [f"{nm}{'' if rel else '  ×'}" for nm, rel in zip(order["name"], order["relevant"])]
    ax.set_yticks(list(y), labels, fontsize=8.5)
    for tick, rel in zip(ax.get_yticklabels(), order["relevant"]):
        tick.set_color("#222222" if rel else "#888888")
    ax.set_xlim(-60, 122)
    ax.set_xticks([-50, -25, 0, 25, 50, 75, 100], ["50", "25", "0", "25", "50", "75", "100"], fontsize=8)
    ax.set_xlabel("% of experts (n = 37)", fontsize=8.5)
    for i, m in zip(y, order["mean"]):
        ax.text(121, i, f"{m:.2f}", va="center", ha="right", fontsize=7.5, color="#444444")
    ax.text(121, len(order) - 0.3, "Mean", ha="right", va="bottom", fontsize=7.5, color="#444444")
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.tick_params(axis="y", length=0)
    ax.legend(ncol=5, fontsize=7, frameon=False, loc="upper center", bbox_to_anchor=(0.42, -0.13),
              handlelength=1.2, columnspacing=1.0)
    fig.tight_layout()
    fig.savefig(path_stem.with_suffix(".pdf"), bbox_inches="tight")
    fig.savefig(path_stem.with_suffix(".png"), dpi=200, bbox_inches="tight")
    plt.close(fig)


def task2_agreement(coding: pd.DataFrame) -> pd.DataFrame:
    both = coding[coding["item_or_topic_a"].isin(["item", "topic"]) & coding["item_or_topic_b"].isin(["item", "topic"])]
    n = len(both)
    po = (both["item_or_topic_a"] == both["item_or_topic_b"]).mean()
    pe = sum((both["item_or_topic_a"] == c).mean() * (both["item_or_topic_b"] == c).mean() for c in ("item", "topic"))
    status = coding["status"].fillna("").str.strip().replace({"c": "consolidated", "nv": "not valid",
                                                              "d": "to discuss", "t1": "comment on Task 1"})
    rows = [("Coded segments (both coders)", len(coding)),
            ("Task 2 answers coded", coding["task2_answer"].nunique()),
            ("Segments classified as item or topic by both coders", n),
            ("Agreement on item vs topic (%)", round(100 * po, 1)),
            ("Cohen's kappa, item vs topic", round((po - pe) / (1 - pe), 3))]
    rows += [(f"Consolidation status: {k}", v) for k, v in status.value_counts().items()]
    return pd.DataFrame(rows, columns=["measure", "value"])


def comments_of_removed_topics(table: pd.DataFrame) -> pd.DataFrame | None:
    files = sorted(EXPORTS_DIR.glob("results-survey654492*.xlsx"), key=lambda p: p.stat().st_mtime)
    if not files:
        return None
    df = pd.read_excel(files[-1])
    df.columns = [str(c).split(". ", 1)[0] for c in df.columns]
    df = df[df["submitdate"].notna()].sort_values("id").reset_index(drop=True)
    df["expert"] = [f"A{i:02d}" for i in range(1, len(df) + 1)]
    topics = pd.read_csv(DATA_DIR / "codebook" / "expert-survey-1_topics.csv").set_index("topic")
    rows = []
    for _, r in table[~table["relevant"]].iterrows():
        code = topics.at[r["topic"], "limesurvey_code"]
        for _, x in df[["expert", code, f"{code}[comment]"]].dropna().iterrows():
            rows.append({"topic": r["name"], "expert": x["expert"], "rating": x[code], "comment": x[f"{code}[comment]"]})
    return pd.DataFrame(rows)


def response_summary() -> pd.DataFrame | None:
    """Started/submitted/incomplete and completion time, read from the raw export (restricted-data)."""
    files = sorted(EXPORTS_DIR.glob("results-survey654492*.xlsx"), key=lambda p: p.stat().st_mtime)
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
        r"1 = never relevant, 5 = always relevant): median, mean, variance, share of experts who rated the "
        r"topic 4 or 5, Kendall's $W$ of the other 14 topics when the topic is removed ($W = 0.358$ with all "
        r"15), and number of comments. Topics with a mean $\geq$ 4 were kept.}",
        r"\label{tab:topic-relevance}",
        r"\resizebox{\columnwidth}{!}{%",
        r"\begin{tabular}{lrrrrrrc}",
        r"\toprule",
        r"Topic & Median & Mean & Var. & \% 4--5 & $W_{-t}$ & Comm. & Kept \\",
        r"\midrule",
    ]
    for _, r in table.iterrows():
        kept = "yes" if r["relevant"] else "no"
        lines.append(f"{r['name']} & {r['median']:g} & {r['mean']:.2f} & {r['variance']:.2f} & "
                     f"{r['pct_rated_4_5']:.0f} & {r['kendall_w_without_topic']:.3f} & {int(r.get('n_comments', 0))} & "
                     f"{kept} \\\\")
    lines += [r"\bottomrule", r"\end{tabular}}", r"\end{table}", ""]
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
        print("response-summary.csv not written: the raw export is not in restricted-data/limesurvey/.")

    table = topic_table(ratings, topics, comments)
    table.to_csv(OUT_DIR / "topic-relevance.csv", index=False, float_format="%.6g")
    (OUT_DIR / "table-topic-relevance.tex").write_text(latex_topics(table), encoding="utf-8")
    topic_table(pilot, topics, None).to_csv(OUT_DIR / "pilot-topic-relevance.csv", index=False, float_format="%.6g")

    counts = {k: int((ratings.values == k).sum()) for k in LEVELS}
    pilot_counts = {k: int((pilot.values == k).sum()) for k in LEVELS}
    pd.DataFrame([{"level": k, "label": LEVELS[k], "survey_1": counts[k], "pilot": pilot_counts[k]} for k in LEVELS]) \
        .to_csv(OUT_DIR / "rating-counts.csv", index=False)

    icc = icc_two_way(ratings.T.values.astype(float))
    pd.DataFrame(icc).to_csv(OUT_DIR / "agreement-icc.csv", index=False, float_format="%.6g")
    figure_topic_relevance(table, OUT_DIR / "figure-topic-relevance")

    coding_path = DATA_DIR / "raw" / "expert-survey-1_comment-coding.csv"
    if coding_path.exists():
        tab = comment_coding_table(pd.read_csv(coding_path), topics)
        tab.to_csv(OUT_DIR / "comment-coding-by-topic.csv")
        (OUT_DIR / "table-comment-coding.tex").write_text(latex_comment_coding(tab, table), encoding="utf-8")
        (OUT_DIR / "table-removed-topics.tex").write_text(latex_removed_topics(table, tab), encoding="utf-8")
    else:
        print("Comment coding not found: run data/prepare_item_sources.py.")
    t2_path = DATA_DIR / "raw" / "expert-survey-1_task2-coding.csv"
    if t2_path.exists():
        agree = task2_agreement(pd.read_csv(t2_path))
        agree.to_csv(OUT_DIR / "task2-coding-agreement.csv", index=False)
    quotes = comments_of_removed_topics(table)
    if quotes is not None:
        TMP_DIR.mkdir(exist_ok=True)
        quotes.to_csv(TMP_DIR / "expert-survey-1_comments-of-removed-topics.csv", index=False)

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
    for i in icc:
        print(f"ICC {i['type']}: {i['icc']:.3f} [{i['ci_low']:.3f}, {i['ci_high']:.3f}], "
              f"F({i['df1']}, {i['df2']:.0f}) = {i['F']:.2f}")
    print(f"Task 2: {n_filled} answer fields filled by {int((suggestions['n_suggestions'] > 0).sum())} experts")

    if args.check:
        sys.exit(0 if check(table, profile_df, steps, pilot_counts, ratings, topics) else 1)


if __name__ == "__main__":
    main()
