"""Prepare the ratings of the exploratory survey (phase 2.1, used also by phase 2.2): check the tool labels and collapse rare answer options.

Run from the repository root:
    python phase2-1-scale-development/data/prepare_data.py

Input
    raw/ratings-stimulus_original.csv     506 participants x 65 items, uncollapsed (-3..+3)
    raw/survey_seed_system/*.xlsx         survey exports (Response ID, Seed, SYSTEM) of all responses,
                                          including incomplete ones
Output
    prepared/ratings-stimulus_collapsed.csv   all 506 participants, collapsed over the whole sample: the analysis
                                              file of the aggregate EFA (phase 2.1) and of phase 2.2 steps 01 and 02
    prepared/by-tool/ratings-<tool>_collapsed.csv
                                              the participants of one tool, collapsed within that tool: input of the
                                              per-tool EFA (phase 2.1, step 01), as in the EFA run of 2026-03-18
    prepared/collapse_changes.csv             every merge that was made (item, from, to, n answers)
    prepared/label_check.csv                  tool label in the data vs. in the survey export

Collapsing rule for the whole sample (same as Notebooks/04_Notebooks/04_Colapsing_Low-Frequency_Categories-toMoreFrequent.R):
for each item, an answer option chosen by <= 2.5% of the non-missing answers is merged into the
neighbouring option (left or right) that has more answers; on a tie, into the left one. Repeated
until no option is below the threshold. On this data all 111 merges go to the right, so the result
is identical to the "toRight" variant (04_Colapsing_Low-Frequency Categories-toRight.R).
"""
from pathlib import Path
import sys
import hashlib
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


def collapse_to_right(df, items):
    """Rule of 04_Colapsing_Low-Frequency Categories-toRight.R: the lowest option chosen by <= 2.5% of the
    non-missing answers is merged into the option on its right (+3 into +2), repeated until none is left.
    Used for the per-tool files: within a tool, the "to more frequent" rule can merge an option into an empty
    neighbour and back again without end, and the 2026-03-18 per-tool files were made with this rule."""
    df = df.copy()
    changes = []
    for item in items:
        while True:
            props = df[item].value_counts(normalize=True, dropna=True).sort_index()
            low = [v for v in props[props <= THRESHOLD].index if v in LIKERT]
            if not low or len(props) <= 1:
                break
            target = low[0]
            dest = target + 1 if target < LIKERT[-1] else target - 1
            n = int((df[item] == target).sum())
            df.loc[df[item] == target, item] = dest
            changes.append({"item": item, "from": int(target), "to": int(dest), "n_answers": n})
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
    # lineterminator="\n": the same bytes (and MD5) on Windows, macOS and Linux
    collapsed.to_csv(PREPARED / "ratings-stimulus_collapsed.csv", index=False, lineterminator="\n")
    changes.to_csv(PREPARED / "collapse_changes.csv", index=False, lineterminator="\n")
    check.to_csv(PREPARED / "label_check.csv", index=False, lineterminator="\n")
    md5 = hashlib.md5((PREPARED / "ratings-stimulus_collapsed.csv").read_bytes()).hexdigest()
    print(f"MD5 of ratings-stimulus_collapsed.csv: {md5} (expected eb83954b17ac6ef2149f63f4f7c0c572)")
    print(f"Collapsed {len(changes)} answer options in {changes['item'].nunique()} items.")

    # 3. per-tool files for the per-tool EFA, collapsed within each tool with the "toRight" rule,
    #    as the files read by the EFA of 2026-03-18 (Data/ratings-1.csv ... ratings-5.csv)
    by_tool = PREPARED / "by-tool"
    by_tool.mkdir(exist_ok=True)
    for tool, part in data.groupby("stimulus"):
        part_collapsed, part_changes = collapse_to_right(part.drop(columns="stimulus"), items)
        name = "ratings-" + tool.lower().replace(" ", "-") + "_collapsed.csv"
        part_collapsed.to_csv(by_tool / name, index=False, lineterminator="\n")
        print(f"  {tool}: {len(part)} participants, {len(part_changes)} answer options collapsed -> by-tool/{name}")
    print(f"Written to {PREPARED}")


if __name__ == "__main__":
    main()
