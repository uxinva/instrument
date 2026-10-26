"""
Missing-data review of the item screening (step 00): joins, for the 65 items of the 3-factor EFA,
the missing-answer rates per system, the team's analysis of missingness concentrated in a system,
the missing-data flags of the EFA workbook, and the screening decision.

History: the missing answers per system were discussed in the meeting of 2026-03-19, before the number of
factors was chosen. The team decided not to exclude items on missingness alone (Anne-Flore: "the bad ones will
get dropped later anyway because they have weak or moderate loadings"). After the three-factor solution was
chosen, missingness was considered together with the items' loadings; the five exclusions were made between
2026-03-31 and 2026-04-08.

Rule compiled on 2026-10-22 from the records and the team's account (the content criterion was discussed in
several team meetings). Items not already excluded for cross-loading and with more than 3% missing answers in
at least one system were reviewed together with the three-factor solution (collapsed data). An item was
excluded when it also had at least one of:
  1. a weak primary loading (lambda < 0.40);
  2. redundancy with another item;
  3. content tied to a feature that only some tools offer, or to a particular kind of data, so that the
     missing answers probably reflect non-applicability (input/missing-data-review-notes.csv).
The script applies the rule and checks that it reproduces every decision (column rule_matches).

Inputs:
  ../data/raw/ratings-stimulus_original.csv   missing rates recomputed per system (uncollapsed data)
  input/summary-missing-data-ux.csv           team sheet "summary_missing_data_UX" (Google Sheets
                                              1gYWB2ORfyswcoRk0LHK93KOrwwC7Djommcr1tGN6TUw, gid 1590052030),
                                              exported on 2026-10-21: missing % per system and, for the
                                              six items with most missing answers, their factor in the
                                              4-, 5- and 6-factor EFA solutions
  input/efa-missing-data-flags.csv            column "Missing Data" (TRUE / MAYBE) of the EFA workbook,
                                              tab "PA1 Stimuli 3 factors - Agg"
  input/manual-exclusions.csv                 note recorded for each item excluded in the missing-data review
  input/missing-data-review-notes.csv         content scope (feature-specific / general) and rationale of the
                                              items reviewed (more than 3% missing in a system)
  output/efa-screening-items.csv              primary loading, decision and reason (made by screen-efa-items.py)

Outputs (output/):
  missing-data-review.csv    one row per item
  missing-data-review.xlsx   sheets "Items" (65 items), "Decision cases" (items with >= 2% missing
                             or a flag), "Notes"

Run from the repository root (after screen-efa-items.py):
  python phase2-2-item-reduction/00-efa-screening/review-missing-data.py
"""
from pathlib import Path

import pandas as pd

STEP = Path(__file__).resolve().parent
PHASE = STEP.parent
SYSTEMS = {"Tableau": "tableau", "Qlik": "qlik", "Power BI": "power_bi", "Gephi": "gephi", "JMP": "jmp"}
CASE_MIN = 2.0  # % missing from which an item is listed in "Decision cases"
SYSTEM_MAX = 3.0  # review: more than this % missing in at least one system
WEAK = 0.40       # criterion 1: weak primary loading
REDUNDANT = {"P049": "P041"}  # criterion 2


def main():
    data = pd.read_csv(PHASE / "data" / "raw" / "ratings-stimulus_original.csv")
    team = pd.read_csv(STEP / "input" / "summary-missing-data-ux.csv", dtype=str).set_index("item_id")
    flags = pd.read_csv(STEP / "input" / "efa-missing-data-flags.csv").set_index("code")["missing_data_flag"]
    screen = pd.read_csv(STEP / "output" / "efa-screening-items.csv").set_index("code")
    manual = pd.read_csv(STEP / "input" / "manual-exclusions.csv").set_index("code")
    review = pd.read_csv(STEP / "input" / "missing-data-review-notes.csv").set_index("code")

    items = list(screen.index)
    miss = data.groupby("stimulus")[items].apply(lambda g: g.isna().mean() * 100).T
    rows, notes = [], []
    for code in items:
        per = {s: miss.loc[code, s] for s in SYSTEMS}
        top = max(per, key=per.get)
        overall = data[code].isna().mean() * 100
        t = team.loc[code] if code in team.index else None
        # recomputed values versus the team sheet
        if t is not None:
            for s, col in SYSTEMS.items():
                v = str(t[f"missing_pct_{col}"]).strip()
                try:
                    if abs(float(v) - per[s]) > 0.01:
                        notes.append(f"{code} {s}: team sheet {v}, recomputed {per[s]:.2f}")
                except ValueError:
                    notes.append(f"{code} {s}: team sheet has '{v}' (typo); recomputed {per[s]:.2f}")
        s = screen.loc[code]
        rows.append({
            "code": code, "factor_3_solution": s["factor"],
            "statement": t["item_statement"] if t is not None else "",
            "topic": t["topic"] if t is not None else "", "concept": t["concept"] if t is not None else "",
            "survey_order": t["survey_order"] if t is not None else "",
            "n_missing": int(data[code].isna().sum()), "missing_pct_all": round(overall, 2),
            **{f"missing_pct_{c}": round(per[sys], 2) for sys, c in SYSTEMS.items()},
            "max_system": top, "max_system_pct": round(per[top], 2),
            "max_over_overall": round(per[top] / overall, 2) if overall else None,
            "factor_4_solution": (t["factor_4_solution"] if t is not None and pd.notna(t["factor_4_solution"]) else ""),
            "factor_5_solution": (t["factor_5_solution"] if t is not None and pd.notna(t["factor_5_solution"]) else ""),
            "factor_6_solution": (t["factor_6_solution"] if t is not None and pd.notna(t["factor_6_solution"]) else ""),
            "efa_missing_flag": flags.get(code, ""),
            "primary_loading_3_solution": s["primary_loading"],
            "second_loading": s["second_loading"], "decision": s["decision"],
            "reason": s["reason"] if pd.notna(s["reason"]) else "",
            "note": manual.loc[code, "note"] if code in manual.index and "note" in manual and pd.notna(manual.loc[code, "note"]) else "",
            "content_scope": review.loc[code, "content_scope"] if code in review.index else "",
            "review_rationale": review.loc[code, "rationale"] if code in review.index else "",
        })
    df = pd.DataFrame(rows).sort_values("missing_pct_all", ascending=False)

    # the compiled rule
    cross = df.reason.str.startswith("cross-loading")
    df["reviewed"] = (df.max_system_pct > SYSTEM_MAX) & ~cross
    crit = []
    for _, r in df.iterrows():
        c = []
        if r.reviewed:
            if r.primary_loading_3_solution < WEAK:
                c.append("1 weak loading")
            if r.code in REDUNDANT:
                c.append(f"2 redundant with {REDUNDANT[r.code]}")
            if r.content_scope == "feature-specific":
                c.append("3 feature/data-specific")
        crit.append("; ".join(c))
    df["rule_criteria"] = crit
    df["rule_decision"] = ["excluded" if (rv and c) else "" for rv, c in zip(df.reviewed, crit)]
    missing_excl = df.reason.str.startswith("missing")
    scope = df.reviewed | missing_excl
    match = (df.rule_decision == "excluded") == missing_excl
    df["rule_matches"] = ["yes" if m else "NO" for m in match]
    df.loc[~scope, "rule_matches"] = ""
    unscored = df[df.reviewed & (df.content_scope == "")].code.tolist()
    out = STEP / "output"
    df.to_csv(out / "missing-data-review.csv", index=False)

    cases = df[(df.missing_pct_all >= CASE_MIN) | (df.efa_missing_flag != "") | df.reviewed].copy()
    ok = not (df.rule_matches == "NO").any() and not unscored
    note_rows = [
        "Missing-data review of the item screening (step 00). Made by review-missing-data.py.",
        f"Missing % recomputed from data/raw/ratings-stimulus_original.csv (N = {len(data)}).",
        "factor_4/5/6_solution: from the team sheet summary_missing_data_UX (only the six items with most missing answers).",
        "efa_missing_flag: column 'Missing Data' of the EFA workbook (TRUE / MAYBE); no criterion is recorded for it.",
        "max_over_overall: highest rate in one system divided by the overall rate (concentration in one system).",
        "primary_loading_3_solution: loading on the item's factor in the three-factor EFA (collapsed data).",
        "History: missing answers per system were discussed on 2026-03-19, before the number of factors was chosen "
        "(Little's test rejected MCAR in every system; EFA workbook, tab All Measures of Sampling). The team decided "
        "not to exclude items on missingness alone, but together with their loadings in the retained solution. The "
        "five exclusions were made between 2026-03-31 (IRT run still on 65 items) and 2026-04-08 (rankings on 49 items).",
        f"Rule: items with > {SYSTEM_MAX:g}% missing in at least one system (and not excluded for cross-loading) were "
        f"excluded if they also had (1) a primary loading < {WEAK:.2f}, (2) redundancy with another item, or (3) content "
        "tied to a feature of only some tools or to a particular kind of data (content_scope, review_rationale).",
        "P096 was retained: the team read 'link information across different visualizations' as a general "
        "characteristic of the system, not as a predefined link between views.",
        ("Check: the rule reproduces every decision of the missing-data review." if ok else
         f"Check: the rule does NOT reproduce every decision (see rule_matches); items without content_scope: {unscored}"),
        "Checks of the team sheet against the data:",
    ] + (notes or ["all values agree (within 0.01)"])
    with pd.ExcelWriter(out / "missing-data-review.xlsx") as xw:
        df.to_excel(xw, sheet_name="Items", index=False)
        cases.to_excel(xw, sheet_name="Decision cases", index=False)
        pd.DataFrame({"note": note_rows}).to_excel(xw, sheet_name="Notes", index=False)
    print(cases[["code", "max_system_pct", "primary_loading_3_solution", "content_scope", "rule_criteria",
                 "decision", "rule_matches"]].to_string(index=False))
    print("Rule reproduces every decision." if ok else "Rule does NOT reproduce every decision.")
    print("\n".join(note_rows[-len(notes or [1]):]))


if __name__ == "__main__":
    main()
