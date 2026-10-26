"""
Step 00 of the item reduction: from the 65 items of the 3-factor EFA solution to the 49 items
used in the following steps (Version A, Model_1).

Rules (reconstructed on 2026-10-18 from the EFA spreadsheet and the item history):
  1. Cross-loading: an item is excluded when its second-highest loading is above 0.32
     (column "0.32 threshold" of the EFA spreadsheet, tab "PA1 Stimuli 3 factors - Agg").
  2. Missing data: items excluded by the team because of missing answers, listed in
     input/manual-exclusions.csv (status "confirmed" or "inferred").
A low primary loading (< 0.32) is only flagged, not excluded.

Inputs:
  input/efa-pa-3-factors-agg.csv  EFA, principal axis, 3 factors, polychoric correlations, all tools
                                  together, ratings collapsed at 2.5%. Copied from
                                  UXVis/Replication - UXVis development figures/Data_Analysis_by_date_focus/
                                  260318Data_Analysis-PolyCorr-2_5_Collapsed/generatedData-EFA/Agg/
                                  "PA1 Stimuli 3 factors - Agg.csv"
  input/manual-exclusions.csv     exclusions decided by the team (missing data)
  ../item_versions_config.R       full_3_factors (65 items); screened_3_factors and Version_A Model_1
                                  (49 items), for the check
  ../data/raw/ratings-stimulus_original.csv   to report the percentage of missing answers per item

Outputs:
  output/efa-screening-items.csv    one row per item: factor, loadings, cross-loading, missing %, decision, reason
  output/items-after-screening.csv  the retained items per factor
  output/check.txt                  comparison with Version_A Model_1 in item_versions_config.R
  output/table-items-after-screening.tex   LaTeX table (longtable) of the retained items, with wording
                                           (../data/codebook/items.csv) and primary loading

Run from the repository root:
  python phase2-2-item-reduction/00-efa-screening/screen-efa-items.py
"""
from pathlib import Path
import re
import sys

import pandas as pd

STEP = Path(__file__).resolve().parent
PHASE = STEP.parent
CROSS_LOADING_CUT = 0.32
FACTOR_OF_PA = {"PA1": "task_cognition", "PA2": "system", "PA3": "visualization"}
ORDER = ["task_cognition", "system", "visualization"]


def r_lists(text):
    return {m.group(1): re.findall(r"'(\w+)'", m.group(2))
            for m in re.finditer(r"(\w+)\s*=\s*c\(([^)]*)\)", text)}


def main():
    cfg = (PHASE / "item_versions_config.R").read_text(encoding="utf-8")
    full = r_lists(cfg.split("full_3_factors <- list(")[1].split("screened_3_factors <- list(")[0])
    screened = r_lists(cfg.split("screened_3_factors <- list(")[1].split("full_4_factors")[0])
    m1_block = cfg.split("Version_A = list(")[1].split("Model_1 = list(")[1].split("))")[0] + ")"
    model1 = r_lists(m1_block)
    factor_of = {i: f for f, items in full.items() for i in items}

    efa = pd.read_csv(STEP / "input" / "efa-pa-3-factors-agg.csv")
    efa = efa[efa["terms"].str.match(r"^P\w+\.")].copy()
    efa["code"] = efa["terms"].str.split(".").str[0]
    efa = efa.set_index("code")[["PA1", "PA2", "PA3"]]
    if set(efa.index) != set(factor_of):
        sys.exit("The EFA items differ from full_3_factors in item_versions_config.R")

    manual = pd.read_csv(STEP / "input" / "manual-exclusions.csv").set_index("code")
    data = pd.read_csv(PHASE / "data" / "raw" / "ratings-stimulus_original.csv")
    missing = data.drop(columns=["seed", "stimulus"]).isna().mean() * 100

    rows = []
    for code, load in efa.iterrows():
        s = load.sort_values(ascending=False)
        primary_pa, primary, second_pa, second = s.index[0], s.iloc[0], s.index[1], s.iloc[1]
        factor = factor_of[code]
        if second > CROSS_LOADING_CUT:
            decision, reason, status = "excluded", f"cross-loading ({second_pa} = {second:.3f} > {CROSS_LOADING_CUT})", "rule"
        elif code in manual.index:
            decision, reason, status = "excluded", manual.loc[code, "reason"], manual.loc[code, "status"]
        else:
            decision, reason, status = "retained", "", ""
        rows.append(dict(
            code=code, factor=factor, PA1=round(load.PA1, 3), PA2=round(load.PA2, 3), PA3=round(load.PA3, 3),
            primary_factor=FACTOR_OF_PA[primary_pa], primary_loading=round(primary, 3),
            second_loading=round(second, 3), second_factor=FACTOR_OF_PA[second_pa],
            low_primary_flag=primary < CROSS_LOADING_CUT, missing_pct=round(missing[code], 1),
            decision=decision, reason=reason, reason_status=status,
            source=manual.loc[code, "source"] if code in manual.index and status != "rule" else ""))
    res = pd.DataFrame(rows)
    res["factor"] = pd.Categorical(res["factor"], ORDER, ordered=True)
    res = res.sort_values(["factor", "decision", "primary_loading"], ascending=[True, False, False])

    out = STEP / "output"
    out.mkdir(exist_ok=True)
    res.to_csv(out / "efa-screening-items.csv", index=False)
    kept = res[res.decision == "retained"]
    kept[["factor", "code", "primary_loading"]].to_csv(out / "items-after-screening.csv", index=False)

    wording = pd.read_csv(PHASE / "data" / "codebook" / "items.csv").set_index("code")["wording"]
    label = {"task_cognition": "Task\\_cognition", "system": "System", "visualization": "Visualization"}
    esc = lambda t: str(t).replace("&", "\\&").replace("%", "\\%").replace("_", "\\_")
    excl = res[res.decision == "excluded"]
    T = ["% Generated by phase2-2-item-reduction/00-efa-screening/screen-efa-items.py -- do not edit by hand",
         "% Needs \\usepackage{longtable}", "\\small",
         "\\begin{longtable}{llp{9.5cm}r}",
         f"\\caption{{Items that started the item reduction phase ({len(kept)} items), by factor, with their loading "
         f"($\\lambda$) in the three-factor EFA solution.}}",
         "\\label{tab:items-after-screening} \\\\", "\\hline",
         "Factor & Code & Item & $\\lambda$ \\\\", "\\hline", "\\endfirsthead", "\\hline",
         "Factor & Code & Item & $\\lambda$ \\\\", "\\hline", "\\endhead"]
    for f in ORDER:
        g = kept[kept.factor == f]
        for i, (_, r) in enumerate(g.iterrows()):
            T.append(f"{label[f] + f' ({len(g)})' if i == 0 else ''} & {r.code} & {esc(wording.get(r.code, ''))} & {r.primary_loading:.2f} \\\\")
        T[-1] += " \\hline"
    T.append("\\end{longtable}")
    (out / "table-items-after-screening.tex").write_text("\n".join(T) + "\n", encoding="utf-8")

    lines = [f"Items in the EFA: {len(res)}; retained: {len(kept)}; excluded: {len(res) - len(kept)}"]
    for reason, g in res[res.decision == "excluded"].groupby(res["reason"].str.split(" ").str[0]):
        lines.append(f"  excluded for {reason}: {len(g)} ({', '.join(g.code)})")
    mism = res[res.primary_factor != res.factor.astype(str)]
    lines.append(f"Items whose highest loading is not on their factor: {list(mism.code) or 'none'}")
    lines.append(f"Retained with primary loading < {CROSS_LOADING_CUT} (flag only): {list(kept[kept.low_primary_flag].code) or 'none'}")
    ok = True
    for f in ORDER:
        mine, cfg_items = set(kept.loc[kept.factor == f, "code"]), set(model1[f])
        same = mine == cfg_items
        ok &= same
        lines.append(f"{'OK  ' if same else 'DIFF'} {f}: {len(mine)} retained vs {len(cfg_items)} in Version_A Model_1"
                     + ("" if same else f" (only here: {sorted(mine - cfg_items)}; only in config: {sorted(cfg_items - mine)})"))
    lines.append("Result matches Version_A Model_1." if ok else "Result does NOT match Version_A Model_1.")
    same_screened = all(set(kept.loc[kept.factor == f, "code"]) == set(screened[f]) for f in ORDER)
    lines.append("Result matches screened_3_factors (baseline of Versions A-D)." if same_screened
                 else "Result does NOT match screened_3_factors in item_versions_config.R")
    ok &= same_screened
    (out / "check.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
