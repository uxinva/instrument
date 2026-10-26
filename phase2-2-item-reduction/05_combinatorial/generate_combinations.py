"""
Stage 1 of the automated combinatorial reduction: all combinations of N items per factor.

Same logic as Reproduce8-reliability-filter-for-cfa_exploration.ipynb (May 2026), as a script.

Input : 05_combinatorial/input/candidate_pool.csv  (factor, len_set_items, items_set)
Output: 05_combinatorial/input/combinations_<vis>-<task>-<sys>.csv  (scale, combination, combination_id)

Run from the repository root:
  python phase2-2-item-reduction/05_combinatorial/generate_combinations.py            # 6/4/3 (final run)
  python phase2-2-item-reduction/05_combinatorial/generate_combinations.py 6 3 3      # first runs
"""
from itertools import combinations
from pathlib import Path
import csv
import sys

STEP = Path(__file__).resolve().parent
POOL = STEP / "input" / "candidate_pool.csv"


def main():
    n_vis, n_task, n_sys = (int(x) for x in sys.argv[1:4]) if len(sys.argv) >= 4 else (6, 4, 3)
    per_scale = {"visualization": n_vis, "task_cognition": n_task, "system": n_sys}

    with POOL.open(newline="", encoding="utf-8") as f:
        pool = {r["factor"]: sorted(i.strip().strip("'\"") for i in r["items_set"].split(","))
                for r in csv.DictReader(f)}

    rows = []
    for scale, n in per_scale.items():
        for k, combo in enumerate(combinations(pool[scale], n), start=1):
            rows.append({"scale": scale, "combination": ",".join(sorted(combo)),
                         "combination_id": f"{scale}_comb_{k}"})

    out = STEP / "input" / f"combinations_{n_vis}-{n_task}-{n_sys}.csv"
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["scale", "combination", "combination_id"])
        w.writeheader()
        w.writerows(rows)
    counts = {s: sum(r["scale"] == s for r in rows) for s in per_scale}
    print(f"Wrote {len(rows)} combinations {counts} to {out}")


if __name__ == "__main__":
    main()
