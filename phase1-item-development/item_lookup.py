"""Look up candidate items by code or by words, and show their path through all the stages.

Examples (run from the repository root):
    python phase1-item-development/item_lookup.py P0-26
    python phase1-item-development/item_lookup.py P026          (codes with or without hyphens)
    python phase1-item-development/item_lookup.py "easy to use"  (words: searched in the item texts,
                                                                  topics and concepts, any stage)
    python phase1-item-development/item_lookup.py trust --brief  (one line per item)
    python phase1-item-development/item_lookup.py --final        (the 13 items of the validated scale)
    python phase1-item-development/item_lookup.py --all --brief  (all candidate items)

For each item it shows: source pool (P0-P4), topic and concept; the stage at which it entered;
for each stage whether it was present, its wording when the wording changed, and the team's
decision label; the expert survey 2 ratings; the EFA loading and the screening decision of the
item reduction; and whether it is in the validated 13-item scale.

Reads only files that are in the repository (see 04_item-flow/item_tracking.py). Run
data/prepare_item_sources.py and data/prepare_expert_data.py first if data/raw/ is empty.
"""

from __future__ import annotations

import argparse
import re
import sys
import textwrap
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent / "04_item-flow"))
from item_tracking import (FACTOR_NAMES, PHASE_OF_STAGE, RAW, SOURCE_NAMES, STAGE_LABELS,  # noqa: E402
                           available_stages, key, presence, trajectory)

LEVEL = {1: "never", 2: "not often", 3: "sometimes", 4: "frequently", 5: "always"}
DERIVED_FROM = {"P40-26-A": "P0-26", "P40-26-B": "P0-26"}


def load():
    if not (RAW / "item-history.csv").exists():
        sys.exit("data/raw/item-history.csv not found. Run first:\n"
                 "    python phase1-item-development/data/prepare_item_sources.py\n"
                 "    python phase1-item-development/data/prepare_expert_data.py")
    traj = trajectory()
    hist = pd.read_csv(RAW / "item-history.csv")
    return traj, hist, presence()


def find(query: str, traj: pd.DataFrame, pres: pd.DataFrame) -> list[str]:
    q = query.strip()
    if re.fullmatch(r"[Pp]\s*\d[\d\s\-]*[A-Za-z]?", q):          # looks like a code
        k = key(q)
        exact = traj.loc[traj["key"] == k, "item"].tolist()
        if exact:
            return exact
        return traj.loc[traj["key"].str.startswith(k), "item"].tolist()
    words = [w.lower() for w in q.split()]
    texts = pres.groupby("item")["text"].apply(lambda s: " ".join(map(str, s)))
    meta = traj.set_index("item")[["topic", "concept", "es2_wording", "validation_wording"]].fillna("").astype(str)
    hay = (texts.reindex(meta.index).fillna("") + " " + meta.agg(" ".join, axis=1)).str.lower()
    return [i for i, h in hay.items() if all(w in h for w in words)]


def stage_mark(row, s) -> str:
    return "yes" if row.get(f"stage_{s}", False) else "-"


def describe(item: str, traj: pd.DataFrame, hist: pd.DataFrame, pres: pd.DataFrame, stages: list[int]) -> str:
    r = traj.set_index("item").loc[item]
    out = []
    origin = SOURCE_NAMES.get(r["source"], r["source"])
    header = f"{item}  (code in the surveys and in phases 2-3: {r['key']})"
    out.append(header)
    out.append("=" * len(header))
    line = f"Source: {r['source']} – {origin}"
    if item in DERIVED_FROM:
        line += f"; derived from {DERIVED_FROM[item]}"
    out.append(line)
    if isinstance(r["topic"], str) and r["topic"]:
        out.append(f"Topic: {r['topic']}   Concept: {r['concept']}" + ("   (optional item in the pool)" if r["optional_in_pool"] else ""))

    if pd.isna(r["first_stage"]):
        out.append("Never present in any stage.")
        return "\n".join(out)
    first, last = int(r["first_stage"]), int(r["last_stage"])
    out.append(f"Entered: stage {first}, {STAGE_LABELS[first]}")
    if r["in_final_scale"]:
        out.append(f"Result: IN THE VALIDATED SCALE ({r['validation_factor']}, {r['validation_short_name']})")
    else:
        out.append(f"Result: not in the validated scale; last present at stage {last}, {STAGE_LABELS[last]}")
    out.append("")

    out.append(f"{'Stage':<46}{'Present':<9}Wording / decision")
    prev_text = None
    h = hist[hist["item"] == item].set_index("stage_order")
    for s in stages:
        present = bool(r.get(f"stage_{s}", False))
        label = f"{s:>2} {STAGE_LABELS[s]}"
        note = ""
        if s <= 8 and s in h.index:
            text, decision = h.at[s, "text"], h.at[s, "decision"]
            text = "" if pd.isna(text) else str(text)
            decision = "" if pd.isna(decision) else str(decision)
            if present and text and text != prev_text:
                note = f'"{text}"'
                prev_text = text
            elif present:
                note = "(same wording)"
            if decision:
                note = (note + "  " if note else "") + f"[{decision}]"
        elif s == 9:
            if r["stage_8"] and not present:
                note = f"[excluded: {r.get('screening_reason', '')}]"
            elif present:
                note = "(retained in the screening)"
        elif s == 10:
            if present:
                w = str(r["validation_wording"])
                same = prev_text is not None and w.strip(" .").lower() == prev_text.strip(" .").lower()
                note = "(same wording)" if same else f'"{w}"'
            elif r.get("stage_9", False):
                note = "[not selected in the item reduction]"
        out.append(f"{label:<46}{'yes' if present else '-':<9}" +
                   textwrap.shorten(note, 110, placeholder=" …") if note else f"{label:<46}{'yes' if present else '-':<9}")

    out.append("")
    if pd.notna(r.get("es2_mode")):
        tie = " (two modes; first in expert order)" if r.get("es2_mode_tie") else ""
        out.append(f"Expert survey 2 (32 experts): mode {int(r['es2_mode'])} = {LEVEL[int(r['es2_mode'])]} relevant{tie}, "
                   f"median {r['es2_median']:g}, mean {r['es2_mean']:.2f}, comments {int(r['es2_comments'])}"
                   + ("  -> removed (mode <= 3)" if r["es2_mode"] <= 3 else ""))
    if pd.notna(r.get("efa_factor")):
        out.append(f"EFA, 3 factors (phase 2.1): {FACTOR_NAMES.get(r['efa_factor'], r['efa_factor'])}, "
                   f"loading {r['efa_loading']:.3f}; second highest {r['efa_second_loading']:.3f} ({r['efa_second_factor']}); "
                   f"missing {r['missing_pct']}%")
        out.append(f"Item-reduction screening (phase 2.2): {r['screening_decision']}"
                   + (f" – {r['screening_reason']}" if isinstance(r["screening_reason"], str) and r["screening_reason"] else ""))
    return "\n".join(out)


def brief(item: str, traj: pd.DataFrame, pres: pd.DataFrame, stages: list[int]) -> str:
    r = traj.set_index("item").loc[item]
    marks = "".join("#" if r.get(f"stage_{s}", False) else "." for s in stages)
    text = pres[pres["item"] == item].sort_values("stage_order")["text"]
    text = next((t for t in reversed(text.tolist()) if isinstance(t, str) and t), "")
    final = "FINAL" if r["in_final_scale"] else f"last {int(r['last_stage']) if pd.notna(r['last_stage']) else '-'}"
    return f"{item:<10} {r['source']}  {marks}  {final:<7} {textwrap.shorten(text, 80, placeholder=' …')}"


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):  # Windows consoles: never stop on a character they cannot show
        sys.stdout.reconfigure(errors="replace")
    parser = argparse.ArgumentParser(description="Look up candidate items by code or words.",
                                     formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    parser.add_argument("query", nargs="*", help="item code (P0-26, P026) or words to search")
    parser.add_argument("--brief", action="store_true", help="one line per item")
    parser.add_argument("--final", action="store_true", help="list the items of the validated scale")
    parser.add_argument("--all", action="store_true", help="list all candidate items")
    args = parser.parse_args()

    traj, hist, pres = load()
    stages = available_stages()
    if args.final:
        items = traj.loc[traj["in_final_scale"], "item"].tolist()
    elif args.all:
        items = traj["item"].tolist()
    elif args.query:
        items = find(" ".join(args.query), traj, pres)
    else:
        parser.print_help()
        return

    if not items:
        print(f"No item found for: {' '.join(args.query)}")
        return
    if args.brief or len(items) > 5:
        if not args.brief:
            print(f"{len(items)} items found; showing one line each (give a code for the details).\n")
        print(f"{'Item':<10} Src  Stages {''.join(str(s % 10) for s in stages)}  Result  Last wording")
        for i in items:
            print(brief(i, traj, pres, stages))
        print("\nStages: " + "; ".join(f"{s % 10} = {STAGE_LABELS[s]}" for s in stages))
        return
    print("\n\n".join(describe(i, traj, hist, pres, stages) for i in items))
    print("\nPhases: " + "; ".join(f"stages {', '.join(str(s) for s in stages if PHASE_OF_STAGE[s] == p)} = {p}"
                                   for p in dict.fromkeys(PHASE_OF_STAGE[s] for s in stages)))


if __name__ == "__main__":
    main()
