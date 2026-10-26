"""
Builds the IRT part of the multi-criteria triangulation ranking: for each of the 49 items, the four
scores (0-3) given to the item trace plots and the IRT rank agreed in the IRT meetings.

The IRT rank was agreed by the team after looking at the plots and the scores; it is not a formula.
The script reports the total of the four scores next to the rank and, in irt-checks.txt, how far
the rank follows that total (Spearman correlation and the items whose order disagrees most).

Inputs (all in the repository):
  04_ranking/ranking_criteria.csv   per-item criteria (made by extract_ranking_criteria.py)
  data/codebook/items.csv           item wording

Outputs (04_ranking/output/):
  irt-ranking-table.tex   LaTeX table (longtable), label tab:IRT-ranking
  irt-ranking-table.csv   the same as CSV
  irt-checks.txt          rank versus total of the scores

Run from the repository root:
  python phase2-2-item-reduction/04_ranking/build-irt-ranking-table.py
"""
from pathlib import Path
import csv

STEP = Path(__file__).resolve().parent
PHASE = STEP.parent
OUT = STEP / "output"

FACTOR_ORDER = ["task_cognition", "system", "visualization"]
FACTOR_LABEL = {"task_cognition": "Task\\_cognition", "system": "System", "visualization": "Visualization"}
SCORES = [("irt_monotonicity", "Mon."), ("irt_discrimination", "Disc."),
          ("irt_middle_category", "Mid."), ("irt_coverage", "Cov.")]
TOP = 5


def read_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def to_int(v):
    return int(v) if v not in ("", None) else None


def esc(s):
    return (s.replace("\\", "\\textbackslash{}").replace("&", "\\&").replace("%", "\\%")
             .replace("_", "\\_").replace("#", "\\#"))


def dash(x):
    return "--" if x is None else str(x)


def avg_ranks(values, reverse=False):
    """Ranks with ties averaged (1 = first)."""
    order = sorted(range(len(values)), key=lambda i: values[i], reverse=reverse)
    ranks = [0.0] * len(values)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and values[order[j + 1]] == values[order[i]]:
            j += 1
        for k in range(i, j + 1):
            ranks[order[k]] = (i + j) / 2 + 1
        i = j + 1
    return ranks


def spearman(x, y):
    rx, ry = avg_ranks(x), avg_ranks(y)
    n = len(x)
    mx, my = sum(rx) / n, sum(ry) / n
    cov = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    sx = sum((a - mx) ** 2 for a in rx) ** 0.5
    sy = sum((b - my) ** 2 for b in ry) ** 0.5
    return cov / (sx * sy)


items = read_csv(STEP / "ranking_criteria.csv")
wording = {r["code"]: r["wording"] for r in read_csv(PHASE / "data" / "codebook" / "items.csv")}
for r in items:
    for k, _ in SCORES:
        r[k] = to_int(r[k])
    r["rank_irt"] = to_int(r["rank_irt"])
    r["total"] = sum(r[k] for k, _ in SCORES) if all(r[k] is not None for k, _ in SCORES) else None
    r["wording"] = wording.get(r["code"], "")


def ordered(rows):
    """Ranked items by IRT rank, then the unranked ones by total (highest first)."""
    ranked = sorted([r for r in rows if r["rank_irt"] is not None], key=lambda r: r["rank_irt"])
    rest = sorted([r for r in rows if r["rank_irt"] is None], key=lambda r: (-(r["total"] or 0), r["code"]))
    return ranked + rest


# ----------------------------------------------------------------------------- checks
checks = ["IRT rank versus total of the four scores (the rank was agreed by the team, not computed)", ""]
for f in FACTOR_ORDER:
    rows = [r for r in items if r["factor"] == f]
    ranked = [r for r in rows if r["rank_irt"] is not None and r["total"] is not None]
    rho = spearman([r["rank_irt"] for r in ranked], [-r["total"] for r in ranked])
    exp = avg_ranks([r["total"] for r in ranked], reverse=True)
    gaps = sorted(((r["rank_irt"] - e, r) for r, e in zip(ranked, exp)), key=lambda t: -abs(t[0]))
    top_total = {r["code"] for r, e in zip(ranked, exp) if e <= TOP}
    top_rank = {r["code"] for r in ranked if r["rank_irt"] <= TOP}
    checks.append(f"{f}: {len(rows)} items, {len(ranked)} with an IRT rank; "
                  f"Spearman(rank, total) = {rho:.2f}")
    checks.append(f"  top {TOP} by IRT rank: {sorted(top_rank)}")
    checks.append(f"  top {TOP} by total:    {sorted(top_total)} (ties averaged)")
    checks.append("  largest differences (IRT rank - rank by total): " +
                  ", ".join(f"{r['code']} {r['rank_irt']} vs {e:g}" for d, r in gaps[:4]
                            for e in [r['rank_irt'] - d] if abs(d) >= 3))
    unr = [r["code"] for r in rows if r["rank_irt"] is None]
    if unr:
        checks.append(f"  without IRT rank: {', '.join(unr)}")
    checks.append("")

OUT.mkdir(exist_ok=True)
(OUT / "irt-checks.txt").write_text("\n".join(checks), encoding="utf-8")
print("\n".join(checks))

# ----------------------------------------------------------------------------- table
head = ("Code & Item & " + " & ".join(lbl for _, lbl in SCORES) + " & Total & IRT rank \\\\")
T = [
    "% Generated by phase2-2-item-reduction/04_ranking/build-irt-ranking-table.py -- do not edit by hand",
    "% Needs \\usepackage{longtable}",
    "\\small",
    "\\begin{longtable}{lp{7.2cm}cccccc}",
    "\\caption{IRT ranking: each item's trace plot was scored from 0 (poor) to 3 (good) for wave succession -- "
    "monotonicity (Mon.), height of intermediate peaks -- discrimination (Disc.), neutral point centering (Mid.), "
    "and latent trace coverage -- full scale utilization (Cov.). Total is the sum of the four scores (0--12). "
    "The IRT rank (1 = best) was "
    "agreed by the team after inspecting the plots together with these scores, so it does not always follow the "
    "total. Within each factor, items are ordered by IRT rank; -- = not ranked.}",
    "\\label{tab:IRT-ranking}\\\\",
    "\\hline", head, "\\hline", "\\endfirsthead",
    "\\hline", head, "\\hline", "\\endhead",
]
csv_rows = []
for f in FACTOR_ORDER:
    T.append(f"\\multicolumn{{8}}{{l}}{{\\textit{{{FACTOR_LABEL[f]} Factor}}}} \\\\")
    for r in ordered([r for r in items if r["factor"] == f]):
        T.append(" & ".join([r["code"], esc(r["wording"])] + [dash(r[k]) for k, _ in SCORES] +
                            [dash(r["total"]), dash(r["rank_irt"])]) + " \\\\")
        csv_rows.append({"factor": f, "code": r["code"], "wording": r["wording"],
                         **{k: r[k] for k, _ in SCORES}, "total": r["total"], "rank_irt": r["rank_irt"]})
    T[-1] += " \\hline"
T.append("\\end{longtable}")
(OUT / "irt-ranking-table.tex").write_text("\n".join(T) + "\n", encoding="utf-8")

with open(OUT / "irt-ranking-table.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(csv_rows[0]))
    w.writeheader()
    w.writerows(csv_rows)
print(f"Wrote irt-ranking-table.tex / .csv to {OUT}")
