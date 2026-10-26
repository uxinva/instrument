"""
Builds the tables of the multi-criteria triangulation ranking (paper section 3.3).

Inputs (all in the repository):
  04_ranking/ranking_criteria.csv   per-item criteria (made by extract_ranking_criteria.py)
  data/codebook/items.csv           item wording
  item_versions_config.R            item lists of the models, used only for the checks
  05_combinatorial/input/candidate_pool.csv   handpicked candidate pool, used only for the checks

Outputs (04_ranking/output/):
  ranking_table_main.tex   paper table: prioritized items of each factor (final priority), three criteria side by side
  ranking_table_full.csv   supplementary material: all 49 items with values, ranks, IRT plot scores,
                           priority and the considerations recorded in the ranking meetings
The IRT scores are shown in the paper by build-irt-ranking-table.py (Table tab:IRT-ranking).
  checks.txt               result of the consistency checks

Run from the repository root:
  python phase2-2-item-reduction/04_ranking/build_ranking_table.py
"""
from pathlib import Path
import csv
import re
import sys

STEP = Path(__file__).resolve().parent
PHASE = STEP.parent
OUT = STEP / "output"

FACTOR_ORDER = ["task_cognition", "system", "visualization"]
FACTOR_LABEL = {"task_cognition": "Task_cognition", "system": "System", "visualization": "Visualization"}
TOP = 5  # size of the reduced models


# ----------------------------------------------------------------------------- inputs
def read_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def dash(x):
    return "--" if x is None else str(x)


def to_int(v):
    return int(v) if v not in ("", None) else None


def r_lists(text):
    """Parse `name = c('A','B')` entries of an R list into {name: [items]}."""
    return {m.group(1): re.findall(r"'(\w+)'", m.group(2))
            for m in re.finditer(r"(\w+)\s*=\s*c\(([^)]*)\)", text)}


def model_lists(cfg, version, model):
    vblock = cfg.split(f"{version} = list(")[1]
    mblock = vblock.split(f"{model} = list(")[1].split("))")[0] + ")"  # keep the last c( ) closed
    return r_lists(mblock)


items = read_csv(STEP / "ranking_criteria.csv")
wording = {r["code"]: r["wording"] for r in read_csv(PHASE / "data" / "codebook" / "items.csv")}
cfg = (PHASE / "item_versions_config.R").read_text(encoding="utf-8")

for r in items:
    r["alpha_if_dropped"] = float(r["alpha_if_dropped"])
    r["loading"] = float(r["loading"])
    for k in ("rank_reliability", "rank_loading", "rank_irt", "priority", "priority_final",
              "irt_monotonicity", "irt_discrimination", "irt_middle_category", "irt_coverage"):
        r[k] = to_int(r[k])
    r["wording"] = wording.get(r["code"], "")
    ranks = [x for x in (r["rank_reliability"], r["rank_loading"], r["rank_irt"]) if x is not None]
    r["mean_rank"] = sum(ranks) / len(ranks)
    r["top_in"] = ", ".join(lbl for lbl, x in (("R", r["rank_reliability"]), ("L", r["rank_loading"]),
                                                 ("I", r["rank_irt"])) if x is not None and x <= TOP)

by_factor = {f: [r for r in items if r["factor"] == f] for f in FACTOR_ORDER}

# ----------------------------------------------------------------------------- checks
checks, failed = [], False


def check(ok, msg):
    global failed
    checks.append(("OK   " if ok else "FAIL ") + msg)
    failed |= not ok


def min_rank(values, reverse=False):
    s = sorted(values, reverse=reverse)
    return [s.index(v) + 1 for v in values]


for f, rows in by_factor.items():
    # 1. reliability rank = rank of alpha if dropped, lowest first
    exp = min_rank([r["alpha_if_dropped"] for r in rows])
    bad = [r["code"] for r, e in zip(rows, exp) if r["rank_reliability"] != e]
    check(not bad, f"{f}: reliability rank follows alpha if dropped (lowest = 1) {bad or ''}")
    # 2. loading rank = rank of loading, highest first
    exp = min_rank([r["loading"] for r in rows], reverse=True)
    bad = [r["code"] for r, e in zip(rows, exp) if r["rank_loading"] != e]
    check(not bad, f"{f}: loading rank follows the factor loading (highest = 1) {bad or ''}")


def top_codes(rows, key):
    return {r["code"] for r in rows if r[key] is not None and r[key] <= TOP}


# 3. reduced models = top 5 of one criterion (Model_3 uses the first priority, April 2026)
for crit, key, version, model in (("loadings", "rank_loading", "Version_B", "Model_1"),
                                  ("IRT", "rank_irt", "Version_A", "Model_2"),
                                  ("triangulated priority", "priority", "Version_A", "Model_3")):
    lists = model_lists(cfg, version, model)
    for f, rows in by_factor.items():
        top, cfg_items = top_codes(rows, key), set(lists[f])
        note = "" if top == cfg_items else f"(top {TOP}: {sorted(top)}; config: {sorted(cfg_items)})"
        checks.append(("OK   " if top == cfg_items else "NOTE ") +
                      f"{version} {model} {f} = top {TOP} by {crit} {note}")

# 4. final priority = handpicked candidate pool of the combinatorial search
pool = {r["factor"]: set(r["items_set"].split(",")) for r in read_csv(PHASE / "05_combinatorial" / "input" / "candidate_pool.csv")}
for f, rows in by_factor.items():
    pri = {r["code"]: r["priority_final"] for r in rows if r["priority_final"] is not None}
    missing = sorted(pool[f] - set(pri))
    n = max((pri[c] for c in pool[f] if c in pri), default=0)
    top = {c for c, p in pri.items() if p <= n}
    check(not missing and top == pool[f],
          f"{f}: candidate pool of 05_combinatorial = items with final priority 1-{n} "
          f"{'' if not missing and top == pool[f] else (sorted(top - pool[f]), missing)}")
    changed = [f"{r['code']} {dash(r['priority'])}->{dash(r['priority_final'])}" for r in rows
               if r["priority"] != r["priority_final"]]
    checks.append(f"INFO {f}: priority changed after the handpicked revision: {', '.join(changed) or 'none'}")

(OUT).mkdir(exist_ok=True)
(OUT / "checks.txt").write_text("\n".join(checks) + "\n", encoding="utf-8")
print("\n".join(checks))
if failed:
    sys.exit("A rank does not match its values; tables not written.")


# ----------------------------------------------------------------------------- ordering
def ordered(rows):
    """Prioritized items by priority; then the others by mean of their available ranks."""
    pri = sorted([r for r in rows if r["priority_final"] is not None], key=lambda r: (r["priority_final"], r["mean_rank"]))
    rest = sorted([r for r in rows if r["priority_final"] is None], key=lambda r: (r["mean_rank"], r["rank_loading"]))
    return pri + rest


def esc(s):
    return (s.replace("\\", "\\textbackslash{}").replace("&", "\\&").replace("%", "\\%")
             .replace("_", "\\_").replace("#", "\\#"))


# ----------------------------------------------------------------------------- main table (paper)
main = [
    "% Generated by phase2-2-item-reduction/04_ranking/build_ranking_table.py -- do not edit by hand",
    "\\begin{table}[htbp]",
    "\\centering",
    "\\small",
    "\\caption{Multi-criteria triangulation ranking: prioritized items of each factor, from the strongest "
    "to the weakest mixed psychometric properties. Each criterion ranks the items of the factor "
    "(1 = best): reliability by Cronbach's $\\alpha$ if the item is dropped (lowest first), factor "
    "loading by $\\lambda$ (highest first) and IRT by the inspection of the item trace plots "
    "(scores in Table~\\ref{tab:IRT-ranking}). $\\alpha$ if dropped was computed within the factors of the "
    "65-item EFA solution. "
    "\\emph{Top~5 in} lists the criteria in which the item is among the five best "
    "(R = reliability, L = loading, I = IRT); -- = not ranked in the IRT inspection.}",
    "\\label{tab:triangulation-ranking}",
    "\\begin{tabular}{clp{6.2cm}cccc}",
    "\\hline",
    "Priority & Code & Item & Reliability & Loading & IRT & Top~5 in \\\\",
    " & & & rank ($\\alpha$ if dropped) & rank ($\\lambda$) & rank & \\\\",
    "\\hline",
]
for f in FACTOR_ORDER:
    rows = [r for r in ordered(by_factor[f]) if r["priority_final"] is not None]
    main.append(f"\\multicolumn{{7}}{{l}}{{\\textit{{{esc(FACTOR_LABEL[f])} Factor}}}} \\\\")
    for r in rows:
        main.append(f"{r['priority_final']} & {r['code']} & {esc(r['wording'])} & "
                    f"{r['rank_reliability']} ({r['alpha_if_dropped']:.4f}) & "
                    f"{r['rank_loading']} ({r['loading']:.2f}) & {dash(r['rank_irt'])} & "
                    f"{r['top_in'] or '--'} \\\\")
    main[-1] += " \\hline"
main += ["\\end{tabular}", "\\end{table}"]
(OUT / "ranking_table_main.tex").write_text("\n".join(main) + "\n", encoding="utf-8")

# ----------------------------------------------------------------------------- full CSV (supplementary material)
csv_rows = []
for f in FACTOR_ORDER:
    for r in ordered(by_factor[f]):
        csv_rows.append({
            "factor": f, "code": r["code"], "wording": r["wording"],
            "alpha_if_dropped": round(r["alpha_if_dropped"], 6), "rank_reliability": r["rank_reliability"],
            "loading": round(r["loading"], 6), "rank_loading": r["rank_loading"],
            "irt_monotonicity": r["irt_monotonicity"], "irt_discrimination": r["irt_discrimination"],
            "irt_middle_category": r["irt_middle_category"], "irt_coverage": r["irt_coverage"],
            "rank_irt": r["rank_irt"], "mean_rank": round(r["mean_rank"], 3), "top5_in": r["top_in"],
            "priority": r["priority"], "priority_final": r["priority_final"], "considerations": r["considerations"]})

with open(OUT / "ranking_table_full.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(csv_rows[0]))
    w.writeheader()
    w.writerows(csv_rows)

print(f"\nWrote ranking_table_main.tex and ranking_table_full.csv to {OUT}")
