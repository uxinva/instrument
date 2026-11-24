"""Step 03: analysis of the second expert survey (relevance of 83 statements, LimeSurvey 718131).

Reads the anonymised data in phase1-item-development/data/ and writes, to output/:
    participants-profile.csv       gender, years of experience, expertise levels
    rating-counts.csv              number of ratings at each relevance level (all statements)
    statement-statistics.csv       per statement: n, mode (three tie rules), mean, median,
                                   variance, SD, counts per level, comments, removed flag
    agreement-icc.csv              two-way ICC, consistency and absolute agreement, average of k raters
    removed-statements.csv         the statements removed after the survey (mode <= 3)
    table-removed-statements.tex   LaTeX table of the removed statements

Mode rule. The 2025 analysis (Google Sheet "2nd_survey_results_complete_answers", sheet
"Analysis") computed the mode with MODE.SNGL over the experts in Response ID order. When two
levels are tied, MODE.SNGL returns the one that occurs first in that order. This script
reproduces that rule ("mode_first") and also reports the lower and the higher tied value.
A statement is removed when mode_first <= 3 (18 statements).

--check compares the results with the 2025 spreadsheet, if a copy is present at
tmp-data/old-analysis/2nd_survey_results_complete_answers.xlsx (not versioned).

Run from the repository root:
    python phase1-item-development/03_expert-survey-2/expert_survey_2.py [--check]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

STEP_DIR = Path(__file__).resolve().parent
PHASE_DIR = STEP_DIR.parent
DATA_DIR = PHASE_DIR / "data"
OUT_DIR = STEP_DIR / "output"
OLD_ANALYSIS = PHASE_DIR / "tmp-data" / "old-analysis" / "2nd_survey_results_complete_answers.xlsx"

LEVELS = {1: "Never relevant", 2: "Not often relevant", 3: "Sometimes relevant",
          4: "Frequently relevant", 5: "Always relevant"}
REMOVAL_THRESHOLD = 3  # removed when mode_first <= 3


def load():
    ratings = pd.read_csv(DATA_DIR / "raw" / "expert-survey-2_ratings.csv").set_index("expert")
    participants = pd.read_csv(DATA_DIR / "raw" / "expert-survey-2_participants.csv")
    comments = pd.read_csv(DATA_DIR / "raw" / "expert-survey-2_comment-counts.csv").set_index("statement")
    statements = pd.read_csv(DATA_DIR / "codebook" / "expert-survey-2_statements.csv").set_index("statement")
    if list(ratings.index) != sorted(ratings.index):
        sys.exit("Experts must be in Response ID order (E01, E02, ...): the mode rule depends on it.")
    return ratings, participants, comments, statements


def modes(values: pd.Series) -> tuple[int, int, int, bool]:
    """Mode as MODE.SNGL (first tied value in expert order), lowest and highest tied value."""
    v = values.dropna().astype(int)
    counts = v.value_counts()
    tied = set(counts[counts == counts.max()].index)
    first = next(x for x in v if x in tied)
    return first, min(tied), max(tied), len(tied) > 1


def icc_two_way(matrix: np.ndarray) -> dict:
    """ICC for n subjects (rows) rated by k raters (columns), two-way model, average of k ratings.
    Same definitions as irr::icc(model = "twoway", unit = "average")."""
    n, k = matrix.shape
    grand = matrix.mean()
    ms_rows = k * ((matrix.mean(axis=1) - grand) ** 2).sum() / (n - 1)
    ms_cols = n * ((matrix.mean(axis=0) - grand) ** 2).sum() / (k - 1)
    resid = matrix - matrix.mean(axis=1, keepdims=True) - matrix.mean(axis=0, keepdims=True) + grand
    ms_err = (resid ** 2).sum() / ((n - 1) * (k - 1))
    from scipy import stats
    f = ms_rows / ms_err
    df1, df2 = n - 1, (n - 1) * (k - 1)
    icc_c = (ms_rows - ms_err) / ms_rows
    icc_a = (ms_rows - ms_err) / (ms_rows + (ms_cols - ms_err) / n)
    # Denominator degrees of freedom of the F test for absolute agreement, as printed by
    # irr::icc (McGraw and Wong, 1996): a and b evaluated at the estimated coefficient.
    a = k * icc_a / (n * (1 - icc_a))
    b = 1 + k * icc_a * (n - 1) / (n * (1 - icc_a))
    df2_a = (a * ms_cols + b * ms_err) ** 2 / ((a * ms_cols) ** 2 / (k - 1) + (b * ms_err) ** 2 / df2)
    return {
        "subjects_statements": n, "raters_experts": k,
        "icc_consistency": icc_c, "icc_agreement": icc_a,
        "F": f, "df1": df1, "df2_consistency": df2, "df2_agreement": df2_a,
        "p_consistency": stats.f.sf(f, df1, df2), "p_agreement": stats.f.sf(f, df1, df2_a),
    }


def statement_table(ratings, comments, statements) -> pd.DataFrame:
    rows = []
    for s in ratings.columns:
        v = ratings[s]
        first, low, high, tie = modes(v)
        row = {
            "statement": s, "team_code": statements.at[s, "team_code"], "text": statements.at[s, "text"],
            "n": int(v.notna().sum()), "mode_first": first, "mode_low": low, "mode_high": high,
            "mode_tie": tie, "mean": v.mean(), "median": v.median(), "variance": v.var(ddof=1),
            "sd": v.std(ddof=1),
        }
        for level in LEVELS:
            row[f"n_{level}"] = int((v == level).sum())
        row["n_comments"] = int(comments.at[s, "n_comments"])
        row["removed"] = first <= REMOVAL_THRESHOLD
        rows.append(row)
    return pd.DataFrame(rows)


def latex_removed(removed: pd.DataFrame) -> str:
    lines = [
        r"\begin{table}[tbp]",
        r"\centering",
        r"\caption{Statements removed after the second expert survey (mode of the relevance ratings $\leq$ 3; "
        r"$n = 32$ experts; 1 = never relevant, 5 = always relevant). "
        r"$^{\dagger}$Two modes; the mode reported is the first tied value in Response ID order.}",
        r"\label{tab:removed-statements}",
        r"\small",
        r"\begin{tabular}{llrrr}",
        r"\toprule",
        r"Code & Statement & Mode & Median & Mean \\",
        r"\midrule",
    ]
    for _, r in removed.sort_values(["mean"]).iterrows():
        dagger = r"$^{\dagger}$" if r["mode_tie"] else ""
        text = r["text"].replace("&", r"\&").replace("%", r"\%")
        lines.append(f"{r['team_code']} & {text} & {r['mode_first']}{dagger} & {r['median']:g} & {r['mean']:.2f} \\\\")
    lines += [r"\bottomrule", r"\end{tabular}", r"\end{table}", ""]
    return "\n".join(lines)


# Differences from the 2025 spreadsheet that are explained (see README): one comment written in
# the comment box of P0-26 ("I found it easy to use this system") was counted under P0-25 in
# the spreadsheet. This script follows the survey, where box commentsP026 belongs to P0-26.
KNOWN_DIFFERENCES = {("comments", "P0-25"): (1, 0), ("comments", "P0-26"): (0, 1)}


def check(table: pd.DataFrame, ratings: pd.DataFrame) -> bool:
    if not OLD_ANALYSIS.exists():
        print(f"--check: {OLD_ANALYSIS} not found; nothing to compare.")
        return False
    import openpyxl
    ws = openpyxl.load_workbook(OLD_ANALYSIS, data_only=True)["Analysis"]
    rows = list(ws.iter_rows(values_only=True))
    old = {r[1]: r for r in rows[1:] if r[1] and r[4] is not None}
    by_team = table.set_index("team_code")
    ok = True
    if len(old) != len(table):
        print(f"--check: {len(old)} statements in the old sheet, {len(table)} here"); ok = False
    for code, r in old.items():
        new = by_team.loc[code]
        old_vals = [int(x) for x in r[4:36]]
        if old_vals != [int(x) for x in ratings[new["statement"]]]:
            print(f"--check: ratings differ for {code}"); ok = False
        for name, old_v, new_v in [("mode", r[36], new["mode_first"]), ("mean", r[37], new["mean"]),
                                   ("median", r[38], new["median"]), ("variance", r[39], new["variance"]),
                                   ("sd", r[40], new["sd"]), ("comments", r[41], new["n_comments"])]:
            if abs(float(old_v) - float(new_v)) > 1e-9:
                if KNOWN_DIFFERENCES.get((name, code)) == (old_v, new_v):
                    print(f"--check: known difference, {name} of {code}: spreadsheet {old_v}, here {new_v}")
                else:
                    print(f"--check: {name} differs for {code}: {old_v} vs {new_v}"); ok = False
    print("--check: all 83 statements agree with the 2025 spreadsheet (ratings, mode, mean, median, "
          "variance, SD, number of comments), apart from the known differences above."
          if ok else "--check: differences found.")
    return ok


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="compare with the 2025 spreadsheet")
    args = parser.parse_args()

    ratings, participants, comments, statements = load()
    OUT_DIR.mkdir(exist_ok=True)

    # Participants
    prof = [("Experts (submitted responses)", len(participants)),
            ("of which pilot reviewers", int(participants["pilot"].sum()))]
    prof += [(f"Gender: {g}", n) for g, n in participants["gender"].value_counts().items()]
    years = pd.to_numeric(participants["years_experience_va"], errors="coerce")
    prof += [("Years of experience with VA: mean", round(years.mean(), 1)),
             ("Years of experience with VA: median", years.median()),
             ("Years of experience with VA: min", years.min()), ("Years of experience with VA: max", years.max())]
    for col, label in [("expertise_usability_evaluation", "Usability evaluation"),
                       ("expertise_va_system_design", "VA system design")]:
        prof += [(f"{label}: {lvl}", n) for lvl, n in participants[col].value_counts().items()]
    pd.DataFrame(prof, columns=["measure", "value"]).to_csv(OUT_DIR / "participants-profile.csv", index=False)

    # Rating counts
    all_values = ratings.values.ravel()
    pd.DataFrame([{"level": k, "label": lab, "n": int((all_values == k).sum())} for k, lab in LEVELS.items()]) \
        .to_csv(OUT_DIR / "rating-counts.csv", index=False)

    # Statement statistics and removed statements
    table = statement_table(ratings, comments, statements)
    table.to_csv(OUT_DIR / "statement-statistics.csv", index=False, float_format="%.6g")
    removed = table[table["removed"]]
    removed[["statement", "team_code", "text", "mode_first", "mode_low", "mode_high", "mode_tie",
             "median", "mean", "n_comments"]].to_csv(OUT_DIR / "removed-statements.csv", index=False,
                                                     float_format="%.6g")
    (OUT_DIR / "table-removed-statements.tex").write_text(latex_removed(removed), encoding="utf-8")

    # Agreement
    icc = icc_two_way(ratings.T.values.astype(float))
    pd.DataFrame([icc]).to_csv(OUT_DIR / "agreement-icc.csv", index=False, float_format="%.6g")

    # Summary on screen
    ties = table[table["mode_tie"]]
    print(f"Experts: {len(ratings)}; statements: {ratings.shape[1]}; ratings: {all_values.size}")
    print("Rating counts:", {LEVELS[k]: int((all_values == k).sum()) for k in LEVELS})
    print(f"ICC(C,{icc['raters_experts']}) = {icc['icc_consistency']:.3f}, "
          f"ICC(A,{icc['raters_experts']}) = {icc['icc_agreement']:.3f}, "
          f"F({icc['df1']}, {icc['df2_consistency']}) = {icc['F']:.2f}")
    print(f"Removed (mode_first <= {REMOVAL_THRESHOLD}): {len(removed)}; "
          f"with lower tied value: {(table['mode_low'] <= REMOVAL_THRESHOLD).sum()}; "
          f"with higher tied value: {(table['mode_high'] <= REMOVAL_THRESHOLD).sum()}")
    print("Tied modes:", ", ".join(f"{r.team_code} ({r.mode_low}/{r.mode_high}, first {r.mode_first})"
                                   for r in ties.itertuples()))
    print(f"Mode 5 and no comment: {((table['mode_first'] == 5) & (table['n_comments'] == 0)).sum()} statements")

    if args.check:
        sys.exit(0 if check(table, ratings) else 1)


if __name__ == "__main__":
    main()
