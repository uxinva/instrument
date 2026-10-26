"""Prepare the phase 2.2 ratings: check the tool labels and collapse rare answer options.

Run from the repository root:
    python phase2-2-item-reduction/data/prepare_data.py

Input
    raw/ratings-stimulus_original.csv     506 participants x 65 items, uncollapsed (-3..+3)
    raw/survey_seed_system/*.xlsx         survey exports (Response ID, Seed, SYSTEM) of all responses,
                                          including incomplete ones
Output
    prepared/ratings-stimulus_collapsed.csv   the analysis file used by steps 01 and 02
    prepared/collapse_changes.csv             every merge that was made (item, from, to, n answers)
    prepared/label_check.csv                  tool label in the data vs. in the survey export

Collapsing rule (same as Notebooks/Reproduce4_Notebooks/04_Colapsing_Low-Frequency_Categories-toMoreFrequent.R):
for each item, an answer option chosen by <= 2.5% of the non-missing answers is merged into the
neighbouring option (left or right) that has more answers; on a tie, into the left one. Repeated
until no option is below the threshold. On this data all 111 merges go to the right, so the result
is identical to the "toRight" variant (04_Colapsing_Low-Frequency Categories-toRight.R).
"""
from pathlib import Path
import sys
import pandas as pd

HERE = Path(__file__).resolve().parent
RAW = HERE / "raw"
PREPARED = HERE / "prepared"
LIKERT = [-3, -2, -1, 0, 1, 2, 3]
THRESHOLD = 0.025


def collapse_to_more_frequent(df, items):
    df = df.copy()
    changes = []
    for item in items:
        while True:
            counts = df[item].value_counts(dropna=True).sort_index()
            if len(counts) <= 1:
                break
            props = counts / counts.sum()
            low = [v for v in props[props <= THRESHOLD].index if v in LIKERT]
            if not low:
                break
            target = low[0]
            i = LIKERT.index(target)
            left = LIKERT[i - 1] if i > 0 else None
            right = LIKERT[i + 1] if i < len(LIKERT) - 1 else None
            n_left = int((df[item] == left).sum()) if left is not None else -1
            n_right = int((df[item] == right).sum()) if right is not None else -1
            if left is not None and n_left >= n_right:
                dest = left
            elif right is not None:
                dest = right
            else:
                break
            n = int((df[item] == target).sum())
            df.loc[df[item] == target, item] = dest
            changes.append({"item": item, "from": int(target), "to": int(dest), "n_answers": n,
                            "n_left_neighbour": n_left, "n_right_neighbour": n_right})
    return df, pd.DataFrame(changes)


def main():
    data = pd.read_csv(RAW / "ratings-stimulus_original.csv", encoding="utf-8-sig")
    items = [c for c in data.columns if c not in ("seed", "stimulus")]
    assert len(data) == 506 and len(items) == 65, (data.shape, len(items))

    # 1. tool labels vs. survey exports
    # each export has a seed column ("Seed" or "seed. Seed") and the tool in the last column
    frames = []
    for f in sorted((RAW / "survey_seed_system").glob("*.xlsx")):
        x = pd.read_excel(f)
        seed_col = next(c for c in x.columns if "seed" in str(c).lower())
        frames.append(pd.DataFrame({"seed": x[seed_col], "system_export": x[x.columns[-1]],
                                    "export_file": f.name}))
    exports = pd.concat(frames).dropna(subset=["seed"])
    exports["seed"] = exports["seed"].astype("int64")
    conflicts = exports.dropna(subset=["system_export"]).groupby("seed")["system_export"].nunique()
    if (conflicts > 1).any():
        sys.exit(f"Seeds with more than one tool in the export: {list(conflicts[conflicts > 1].index)}")
    exports = exports.dropna(subset=["system_export"]).drop_duplicates("seed")
    check = data[["seed", "stimulus"]].merge(exports, on="seed", how="left")
    check["agrees"] = check["stimulus"] == check["system_export"]
    found = check["system_export"].notna()
    wrong = check[found & ~check["agrees"]]
    print(f"Tool labels: {found.sum()} of {len(check)} participants found in the survey export, "
          f"{len(wrong)} disagree.")
    if found.sum() < len(check):
        print("Not found in the export:", list(check.loc[~found, "seed"]))
    if len(wrong) > 0:
        print(wrong)
        sys.exit("Tool labels disagree with the survey export. Fix the raw data first.")

    # 2. collapse
    collapsed, changes = collapse_to_more_frequent(data, items)

    PREPARED.mkdir(exist_ok=True)
    collapsed.to_csv(PREPARED / "ratings-stimulus_collapsed.csv", index=False)
    changes.to_csv(PREPARED / "collapse_changes.csv", index=False)
    check.to_csv(PREPARED / "label_check.csv", index=False)
    print(f"Collapsed {len(changes)} answer options in {changes['item'].nunique()} items.")
    print(f"Written to {PREPARED}")


if __name__ == "__main__":
    main()
