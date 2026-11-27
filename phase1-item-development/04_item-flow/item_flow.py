"""Step 04: sources of the item pool (P0-P3) and number of items at each stage, up to the validated scale.

Reads phase1-item-development/data/raw/ (built by data/prepare_item_sources.py), the screening
output of phase 2.2 (49 items) and the item codebook of phase 3 (13 items), and writes, to output/:
    sources-summary.csv         per source: material reviewed, classification counts, items in the pool
    source-p0-by-topic.csv      P0: expert suggestions coded per topic and their outcome
    source-p2-by-scale.csv      P2: items reviewed per standardized scale and their classification
    source-p3-by-topic.csv      P3: literature terms per final topic
    concept-coverage.csv        topic-concepts of the pool and the sources in which they occur
    item-flow.csv               items per stage and source (P0, P1, P2, P3, P4 = added in the
                                interviews, P9 = attention checks), from the pool (95) to the
                                exploratory survey (65), the item-reduction screening (49) and the
                                validated scale (13)
    item-flow-changes.csv       items removed and added between consecutive stages
    items-by-topic.csv          items per topic in the pool, after expert survey 2, in the
                                exploratory survey and in the validated scale
    item-trajectory.csv         one row per item: source, topic, concept, presence at each stage,
                                expert survey 2 statistics, EFA loading, screening decision,
                                validation factor (also used by ../item_lookup.py)
    final-items.csv             the 13 items of the validated scale with their origin
    table-item-flow.tex         LaTeX table of the item flow (main text)
    table-item-flow-changes.tex LaTeX table (appendix): items removed, added and reworded at each stage, and why
    table-final-items-history.tex LaTeX table (appendix): origin and wording history of the 13 final items
    table-p0-by-topic.tex       LaTeX table (appendix): Task 2 answers coded per topic and the P0 items written

Sources (team codes):
    P0  items written from the experts' suggestions (Task 2 of expert survey 1)
    P1  items of the UEQ+ scales of the 15 topics of Task 1, compared with P0
    P2  items of other standardized questionnaires, compared with P0+P1
    P3  terms and excerpts extracted from the VA literature (systematic review), compared with P0+P1+P2

--check compares the counts with the values recorded in the phase context (Items Historic, read
on 2026-11-17, 49 and 13 for phases 2.2 and 3) and with the outputs of step 03 (the 18 statements
removed after expert survey 2).

Run from the repository root:
    python phase1-item-development/04_item-flow/item_flow.py [--check]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from item_tracking import STAGE_LABELS, available_stages, presence, trajectory  # noqa: E402

STEP_DIR = Path(__file__).resolve().parent
PHASE_DIR = STEP_DIR.parent
RAW = PHASE_DIR / "data" / "raw"
OUT_DIR = STEP_DIR / "output"
STEP03_REMOVED = PHASE_DIR / "03_expert-survey-2" / "output" / "removed-statements.csv"

SOURCES = ["P0", "P1", "P2", "P3", "P4", "P9"]

# Section of the paper that describes each stage (last column of table-item-flow.tex). Labels
# marked "assumed" are not yet in the draft of 2026-11-24: create them in the paper or change them here.
STAGE_SECTIONS = {
    1: "sec:comb_fontes",          # Sources combination for item generation (P0+P1+P2+P3)
    2: "sec:comb_fontes",          # internal review: "Reducing the number of items and standardizing the format"
    3: "sec:content_validity",     # pilot of the second expert survey (label referenced in the draft)
    4: "sec:content_validity",     # second expert survey, relevance analysis
    5: "sec:cognitive_interviews",  # assumed
    6: "sec:cognitive_interviews",  # assumed
    7: "sec:cognitive_interviews",  # assumed (final team revision before the survey)
    8: "sec:scale_development",    # assumed: exploratory survey and EFA (phase 2.1)
    9: "sec:item_reduction",       # assumed: EFA screening (phase 2.2)
    10: "sec:scale_validation",    # validated 13-item scale (phase 3), label in the paper
}

# Counts of scale items (attention checks excluded) recorded on 2026-11-17 from the sheet
# "Items Historic" (phases/scale-development-context.md).
EXPECTED_SCALE_ITEMS = {1: 95, 2: 84, 3: 83, 4: 65, 5: 67, 6: 64, 7: 66, 8: 65, 9: 49, 10: 13}


# --- appendix tables -----------------------------------------------------------------

# Short reason for each transition (summary of the team's decision labels in "Items Historic",
# of step 03 and of the phase 2.2 screening). Key: stage reached.
TRANSITION_REASONS = {
    2: "Internal review: near-identical items, optional items (not applicable to all users) and items "
       "with an unclear meaning removed; wording changed to the past tense",
    3: "P2-10 removed after the pilot: it requires the participant to have seen error messages",
    4: "Mode of the relevance ratings $\\leq$ 3 in the second expert survey (Section~\\ref{sec:content_validity})",
    5: "P0-87 redundant with P0-26; P2-09 restored with a new wording; P40-26-A and P40-26-B derived from P0-26",
    6: "Items that remained problematic in the interviews",
    7: "P0-31 and P2-08 restored (items are removed only if rewording was tried and they stayed problematic)",
    8: "P0-15 was not shown to the participants by an error in the survey",
    9: "Cross-loading $>$ .32 or more than 3\\% missing answers in a system (item reduction)",
    10: "Not selected by the reliability and CFA-based search of the item reduction",
}
MAX_CODES_LISTED = 20


def tex(text) -> str:
    """Escape the LaTeX special characters of a plain text."""
    text = "" if text is None or (isinstance(text, float) and pd.isna(text)) else str(text)
    for a, b in [("\\", r"\textbackslash{}"), ("&", r"\&"), ("%", r"\%"), ("$", r"\$"), ("#", r"\#"),
                 ("_", r"\_"), ("{", r"\{"), ("}", r"\}"), ("~", r"\textasciitilde{}"), ("^", r"\^{}")]:
        text = text.replace(a, b)
    return text


def code_list(codes: str, n: int) -> str:
    if not n:
        return "--"
    if n > MAX_CODES_LISTED:
        return f"{n} items (listed in the supplemental material)"
    return tex(codes).replace(" ", ", ")


def latex_changes(changes: pd.DataFrame, traj: pd.DataFrame) -> str:
    lines = [r"\begin{table*}[tbp]", r"\centering",
             r"\caption{Items removed, added and reworded between consecutive stages, from the merged pool to the "
             r"validated scale. Item codes as in the team spreadsheets; the first two characters give the source "
             r"(P0--P4, see Table~\ref{tab:item-flow}). Attention checks are not counted. "
             r"Reworded: items whose wording the team changed at that stage.}",
             r"\label{tab:item-flow-changes}", r"\footnotesize",
             r"\begin{tabular}{p{3.3cm}p{5.2cm}p{2.0cm}rp{4.6cm}}", r"\toprule",
             r"Stage reached & Removed & Added & Reworded & Reason \\", r"\midrule"]
    for _, r in changes.iterrows():
        k = int(r["to_stage_order"])
        removed = code_list(r["removed"], r["n_removed"])
        if k == 9 and "screening_reason" in traj:
            out = traj[traj["item"].isin(str(r["removed"]).split())]
            cross = out[out["screening_reason"].str.startswith("cross", na=False)]["item"].tolist()
            miss = out[out["screening_reason"].str.startswith("missing", na=False)]["item"].tolist()
            removed = (f"Cross-loading ({len(cross)}): {tex(', '.join(cross))}; "
                       f"missing data ({len(miss)}): {tex(', '.join(miss))}")
        n_removed = f" ({r['n_removed']})" if 0 < r["n_removed"] <= MAX_CODES_LISTED and k != 9 else ""
        lines.append(f"{tex(r['to_stage'])} & {removed}{n_removed} & {code_list(r['added'], r['n_added'])} & "
                     f"{r['n_reworded'] if k <= 8 else '--'} & {TRANSITION_REASONS.get(k, '')} \\\\")
    lines += [r"\bottomrule", r"\end{tabular}", r"\end{table*}", ""]
    return "\n".join(lines)


def latex_p0_by_topic(p0: pd.DataFrame, pool: pd.DataFrame) -> str:
    p0_pool = pool[pool["source"] == "P0"]
    n_topic_level = int((p0_pool["concept"] == "__").sum())
    concepts = p0_pool[p0_pool["concept"] != "__"].groupby("topic")["concept"].nunique()
    invalid = p0["topic"].str.lower().str.contains("invalid")
    n_invalid = int(invalid.sum())
    valid = p0[~invalid].copy()
    # A not-used assignment is "repeated" when its topic-concept already has an item.
    with_item = set(map(tuple, valid.loc[valid["outcome"] != "removed", ["topic", "concept"]].values))
    valid["repeated"] = [(o == "removed") and ((t, c) in with_item)
                         for o, t, c in valid[["outcome", "topic", "concept"]].values]
    tab = valid.pivot_table(index="topic", columns="outcome", values="item", aggfunc="count", fill_value=0)
    for c in ("item", "optional item", "removed"):
        if c not in tab:
            tab[c] = 0
    tab["assignments"] = tab[["item", "optional item", "removed"]].sum(axis=1)
    tab["repeated"] = valid.groupby("topic")["repeated"].sum().reindex(tab.index).fillna(0).astype(int)
    tab["other"] = tab["removed"] - tab["repeated"]
    tab["concepts"] = concepts.reindex(tab.index).fillna(0).astype(int)
    tab = tab.sort_values(["item", "assignments"], ascending=False)
    ueq = PHASE_DIR / "data" / "codebook" / "expert-survey-1_topics.csv"
    ueq_names = {n.lower() for n in pd.read_csv(ueq)["name"]} if ueq.exists() else set()
    n_new = sum(t.lower() not in ueq_names for t in tab.index) if ueq_names else 0
    lines = [r"\begin{table}[tbp]", r"\centering",
             r"\caption{Pool P0: the experts' answers to Task 2 of the first expert survey, coded by topic. "
             r"Coded: topic--concept assignments (an answer can name more than one concept); Concepts: distinct "
             r"concepts with an item" + (f" ({n_topic_level} further items address the topic as a whole)" if n_topic_level else "")
             + r"; Items and Optional: items written; Repeated: assignments of a concept that already had an item; "
             r"Other: assignments not used for other reasons (e.g., concepts judged hard for users to assess or about system functions rather than UX). "
             + (r"$^\dagger$~Topic not among the 15 UEQ+ topics of Task~1. " if ueq_names else "")
             + (f"{n_invalid} assignments coded as invalid are not shown." if n_invalid else "") + "}",
             r"\label{tab:p0-by-topic}", r"\footnotesize",
             r"\resizebox{\columnwidth}{!}{%", r"\begin{tabular}{lrrrrrr}", r"\toprule",
             r"Topic & Coded & Concepts & Items & Optional & Repeated & Other \\", r"\midrule"]
    for t, r in tab.iterrows():
        mark = r"$^\dagger$" if ueq_names and t.lower() not in ueq_names else ""
        lines.append(f"{tex(t)}{mark} & {r['assignments']} & {r['concepts']} & {r['item']} & {r['optional item']} & "
                     f"{r['repeated']} & {r['other']} \\\\")
    tot = tab[["assignments", "concepts", "item", "optional item", "repeated", "other"]].sum()
    n_with_items = int((tab["item"] + tab["optional item"] > 0).sum())
    lines += [r"\midrule",
              f"Total ({len(tab)} topics, {n_new} new; {n_with_items} with items) & {tot['assignments']} & {tot['concepts']} & "
              f"{tot['item']} & {tot['optional item']} & {tot['repeated']} & {tot['other']} \\\\",
              r"\bottomrule", r"\end{tabular}}", r"\end{table}", ""]
    return "\n".join(lines)


def latex_final_items(traj: pd.DataFrame, hist: pd.DataFrame) -> str:
    final = traj[traj["in_final_scale"]].copy()
    first_text = {}
    for item in final["item"]:
        h = hist[(hist["item"] == item) & hist["present"]].sort_values("stage_order")
        first_text[item] = (h["text"].iloc[0] if len(h) else "").rstrip(".")
    order = ["Cognitive value", "Intuitiveness", "Visualization"]
    final["factor_order"] = final["validation_factor"].map({f: i for i, f in enumerate(order)})
    final = final.sort_values(["factor_order", "efa_loading"], ascending=[True, False])
    lines = [r"\begin{table*}[tbp]", r"\centering",
             r"\caption{Origin and wording history of the 13 items of the validated scale. Source: P0 expert "
             r"suggestions, P1 UEQ+, P3 VA literature, P4 added in the cognitive interviews. First wording: wording "
             r"when the item entered the pool. ES2: mean relevance in the second expert survey (1--5). "
             r"$\lambda$: loading in the three-factor EFA.}",
             r"\label{tab:final-items-history}", r"\footnotesize",
             r"\begin{tabular}{llp{2.6cm}p{4.6cm}p{4.6cm}rr}", r"\toprule",
             r"Code & Src & Topic: concept & First wording & Final wording & ES2 & $\lambda$ \\", r"\midrule"]
    current = None
    for _, r in final.iterrows():
        if r["validation_factor"] != current:
            if current is not None:
                lines.append(r"\midrule")
            lines.append(rf"\multicolumn{{7}}{{l}}{{\textit{{{tex(r['validation_factor'])}}}}} \\")
            current = r["validation_factor"]
        concept = "" if r["concept"] in ("__", "") or pd.isna(r["concept"]) else f": {r['concept']}"
        topic = f"{r['topic']}{concept}" if isinstance(r["topic"], str) and r["topic"] else "derived from P0-26"
        first = first_text[r["item"]]
        final_w = str(r["validation_wording"]).rstrip(".")
        first_cell = "(same)" if first.lower() == final_w.lower() else tex(first)
        es2 = f"{r['es2_mean']:.2f}" if pd.notna(r["es2_mean"]) else "--"
        lines.append(f"{tex(r['item'])} & {r['source']} & {tex(topic)} & {first_cell} & {tex(final_w)} & "
                     f"{es2} & {r['efa_loading']:.2f} \\\\")
    lines += [r"\bottomrule", r"\end{tabular}", r"\end{table*}", ""]
    return "\n".join(lines)


P2_LABELS = {  # display names of the questionnaires of P2 (as written in the team sheet → paper)
    "Presence (include Presence and Immersive tendency questionnaires below)": "Presence and Immersive Tendency",
    "PXI Player Experience Inventory (Funcional and Psychosocial Consequences)": "PXI (Player Experience Inventory)",
    "Emotions - SAM non-verbal pictorial X Semantic Differential scale)": "SAM (Self-Assessment Manikin)",
    "IPQ (igroup presence questionnaire)": "IPQ (igroup Presence Questionnaire)",
    "Trust betwee People and Automation Scale": "Trust between People and Automation",
    "Recommender Systems": "Recommender systems (user-centric evaluation)",
}


def p2_label(name: str) -> str:
    if str(name).startswith("With the help of the word pairs"):
        return "UEQ"  # the UEQ instruction text leaked into the scale column of one row
    return P2_LABELS.get(name, name)


def stage_counts(pool: pd.DataFrame, items) -> dict:
    x = pool[pool["item"].isin(set(items))]
    named = x[x["concept"] != "__"]
    return {"items": len(x), "optional": int(x["optional"].sum()),
            "concepts": named.groupby(["topic", "concept"]).ngroups,
            "topic_level": int((x["concept"] == "__").sum()), "topics": x["topic"].nunique()}


def latex_merge_pools(pool: pd.DataFrame, hist: pd.DataFrame, p1: pd.DataFrame, p2: pd.DataFrame,
                      p3: pd.DataFrame) -> tuple[str, pd.DataFrame]:
    p2_n = p2["scale"].map(p2_label).nunique()
    steps = [
        ("P0: experts' suggestions", "104 valid answers of Task 2", ["P0"]),
        ("+ P1: UEQ+ scales", f"{len(p1)} items of {p1['ueqplus_scale'].nunique()} scales", ["P0", "P1"]),
        ("+ P2: standardized questionnaires", f"{len(p2)} items of {p2_n} questionnaires", ["P0", "P1", "P2"]),
        ("+ P3: VA literature", f"{len(p3):,} terms", ["P0", "P1", "P2", "P3"]),
    ]
    rows, prev = [], None
    for label, material, srcs in steps:
        c = stage_counts(pool, pool[pool["source"].isin(srcs)]["item"])
        c.update(step=label, material=material,
                 new_concepts=c["concepts"] - (prev["concepts"] if prev else 0),
                 added=c["items"] - (prev["items"] if prev else 0))
        rows.append(c)
        prev = c
    for order, label, material in ((2, "Internal review", "--"), (3, "Final review (pilot)", "--")):
        items = hist[(hist["stage_order"] == order) & (hist["present"] == 1)]["item"]
        c = stage_counts(pool, items)
        c.update(step=label, material=material, new_concepts=c["concepts"] - prev["concepts"],
                 added=c["items"] - prev["items"])
        rows.append(c)
        prev = c
    df = pd.DataFrame(rows)[["step", "material", "added", "new_concepts", "items", "optional", "concepts",
                             "topic_level", "topics"]]
    sign = lambda v: f"+{v}" if v > 0 else (r"$-$" + str(-v) if v < 0 else "0")
    lines = [r"\begin{table*}[tbp]", r"\centering",
             r"\caption{Combination of the four sources into the item pool and its internal review. Added and New "
             r"concepts: change with respect to the previous row; Items: cumulative (Optional: items that apply only "
             r"to some systems or users); Concepts: distinct topic--concepts with an item; Topic-level: items that "
             r"address a topic as a whole; Topics: topics with at least one item.}",
             r"\label{tab:merge-pools}", r"\small",
             r"\resizebox{\textwidth}{!}{%", r"\begin{tabular}{llrrrrrrr}", r"\toprule",
             r"Step & Material & Added & New concepts & Items & Optional & Concepts & Topic-level & Topics \\",
             r"\midrule"]
    for i, r in df.iterrows():
        if i == 4:
            lines.append(r"\midrule")
        added = str(r["added"]) if i == 0 else sign(r["added"])
        newc = str(r["new_concepts"]) if i == 0 else sign(r["new_concepts"])
        lines.append(f"{tex(r['step'])} & {tex(r['material'])} & {added} & {newc} & {r['items']} & {r['optional']} & "
                     f"{r['concepts']} & {r['topic_level']} & {r['topics']} \\\\")
    lines += [r"\bottomrule", r"\end{tabular}}", r"\end{table*}", ""]
    return "\n".join(lines), df


def latex_p2_questionnaires(p2: pd.DataFrame) -> tuple[str, pd.DataFrame]:
    x = p2.assign(questionnaire=p2["scale"].map(p2_label))
    tab = x.pivot_table(index="questionnaire", columns="classification", values="subscale", aggfunc="size",
                        fill_value=0)
    for c in ("INCLUDE", "MAYBE", "EXCLUDE"):
        if c not in tab:
            tab[c] = 0
    tab["total"] = tab[["INCLUDE", "MAYBE", "EXCLUDE"]].sum(axis=1)
    tab = tab.sort_values(["total", "INCLUDE"], ascending=False)[["total", "INCLUDE", "MAYBE", "EXCLUDE"]]
    lines = [r"\begin{table}[tbp]", r"\centering",
             r"\caption{Pool P2: items of standardized questionnaires compared with the concepts of P0+P1. "
             r"Include: related to a concept of the list; Maybe: possibly related; Exclude: not related to UX in VA.}",
             r"\label{tab:p2-questionnaires}", r"\footnotesize",
             r"\resizebox{\columnwidth}{!}{%", r"\begin{tabular}{lrrrr}", r"\toprule",
             r"Questionnaire & Items & Include & Maybe & Exclude \\", r"\midrule"]
    for q, r in tab.iterrows():
        lines.append(f"{tex(q)} & {r['total']} & {r['INCLUDE']} & {r['MAYBE']} & {r['EXCLUDE']} \\\\")
    tot = tab.sum()
    lines += [r"\midrule", f"Total ({len(tab)} questionnaires) & {tot['total']} & {tot['INCLUDE']} & {tot['MAYBE']} & "
              f"{tot['EXCLUDE']} \\\\", r"\bottomrule", r"\end{tabular}}", r"\end{table}", ""]
    return "\n".join(lines), tab


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="compare with the recorded counts")
    args = parser.parse_args()

    hist = pd.read_csv(RAW / "item-history.csv")
    pool = pd.read_csv(RAW / "item-pool.csv")
    p0 = pd.read_csv(RAW / "source-p0-suggestions.csv")
    p1 = pd.read_csv(RAW / "source-p1-ueqplus.csv")
    p2 = pd.read_csv(RAW / "source-p2-scales.csv")
    p3 = pd.read_csv(RAW / "source-p3-literature.csv")
    conc = pd.read_csv(RAW / "concept-occurrences.csv")
    OUT_DIR.mkdir(exist_ok=True)

    pool_by_source = pool["source"].value_counts()
    optional = pool[pool["optional"]]["source"].value_counts()

    # --- sources summary -------------------------------------------------------------
    rows = []
    n_answers = p0["task2_answer"].nunique()
    rows.append({"source": "P0", "description": "Expert suggestions (expert survey 1, Task 2)",
                 "material": f"{n_answers} Task 2 answers coded into {len(p0)} topic-concept assignments "
                             f"({p0['topic'].nunique()} topics)",
                 "classification": "; ".join(f"{k}: {v}" for k, v in p0["outcome"].value_counts().items()),
                 "items_in_pool": int(pool_by_source.get("P0", 0)), "optional_items": int(optional.get("P0", 0))})
    rows.append({"source": "P1", "description": "UEQ+ items of the 15 topics of Task 1, compared with P0",
                 "material": f"{len(p1)} items of {p1['ueqplus_scale'].nunique()} UEQ+ scales",
                 "classification": "; ".join(f"{k}: {v}" for k, v in p1["recommendation"].value_counts().items()),
                 "items_in_pool": int(pool_by_source.get("P1", 0)), "optional_items": int(optional.get("P1", 0))})
    rows.append({"source": "P2", "description": "Items of other standardized questionnaires, compared with P0+P1",
                 "material": f"{len(p2)} items of {p2['scale'].nunique()} questionnaires",
                 "classification": "; ".join(f"{k}: {v}" for k, v in p2["classification"].value_counts().items()),
                 "items_in_pool": int(pool_by_source.get("P2", 0)), "optional_items": int(optional.get("P2", 0))})
    p3_final = p3["final_topic_concept"].fillna("")
    rows.append({"source": "P3", "description": "Terms extracted from the VA literature, compared with P0+P1+P2",
                 "material": f"{len(p3)} terms classified into {p3_final[p3_final.ne('') & p3_final.ne('-')].nunique()} "
                             f"topic-concepts",
                 "classification": "; ".join(f"{k}: {v}" for k, v in
                                           p3["status"].fillna("no status").str.strip().str.lower().value_counts().items()),
                 "items_in_pool": int(pool_by_source.get("P3", 0)), "optional_items": int(optional.get("P3", 0))})
    rows.append({"source": "Total", "description": "Merged pool P0+P1+P2+P3", "material": "", "classification": "",
                 "items_in_pool": len(pool), "optional_items": int(pool["optional"].sum())})
    pd.DataFrame(rows).to_csv(OUT_DIR / "sources-summary.csv", index=False)

    # --- per-source detail ------------------------------------------------------------
    (p0.pivot_table(index="topic", columns="outcome", values="item", aggfunc="count", fill_value=0)
       .assign(total=lambda d: d.sum(axis=1)).sort_values("total", ascending=False)
       .to_csv(OUT_DIR / "source-p0-by-topic.csv"))
    (p2.pivot_table(index="scale", columns="classification", values="subscale", aggfunc="size", fill_value=0)
       .assign(total=lambda d: d.sum(axis=1)).sort_values("total", ascending=False)
       .to_csv(OUT_DIR / "source-p2-by-scale.csv"))
    topic3 = p3_final.str.split("-", n=1).str[0].replace("", "(none)")
    topic3.value_counts().rename_axis("topic").rename("terms").to_csv(OUT_DIR / "source-p3-by-topic.csv")

    pool_tc = (pool["topic"] + "-" + pool["concept"]).value_counts().rename("items_in_pool")
    cov = conc.set_index("topic_concept").join(pool_tc, how="outer").fillna({"items_in_pool": 0})
    cov["sources_with_occurrence"] = cov[["p0", "p1", "p2", "p3"]].gt(0).sum(axis=1)
    cov.reset_index().rename(columns={"index": "topic_concept"}).to_csv(OUT_DIR / "concept-coverage.csv", index=False)

    # --- item flow -----------------------------------------------------------------
    pres = presence()
    stages = available_stages()
    flow = pres.pivot_table(index="stage_order", columns="source", values="item", aggfunc="count", fill_value=0)
    flow = flow.reindex(index=stages, columns=SOURCES, fill_value=0)
    flow.insert(0, "stage", [STAGE_LABELS[i] for i in flow.index])
    flow["scale_items"] = flow[[s for s in SOURCES if s != "P9"]].sum(axis=1)
    flow["attention_checks"] = flow["P9"]
    opt = hist[hist["present"]].groupby("stage_order")["optional"].sum()
    flow["optional"] = opt.reindex(flow.index).fillna(0).astype(int)
    flow.reset_index().to_csv(OUT_DIR / "item-flow.csv", index=False)

    traj = trajectory()
    traj.to_csv(OUT_DIR / "item-trajectory.csv", index=False)
    reasons = {9: traj.set_index("item")["screening_reason"].dropna().to_dict() if "screening_reason" in traj else {},
               10: {}}

    changes = []
    sets = {k: set(pres.loc[(pres["stage_order"] == k) & pres["source"].ne("P9"), "item"]) |
               set(pres.loc[(pres["stage_order"] == k) & pres["source"].eq("P9"), "item"]) for k in stages}
    for k in stages[1:]:
        prev = sets[k - 1] - ({i for i in sets[k - 1] if i.startswith("P9")} if k >= 9 else set())
        out_items, in_items = sorted(prev - sets[k]), sorted(sets[k] - sets[k - 1])
        if k <= 8:
            dec = hist[(hist["stage_order"] == k) & hist["item"].isin(out_items)].set_index("item")["decision"].to_dict()
            reworded = int(((hist["stage_order"] == k) & hist["present"] &
                            hist["decision"].fillna("").str.lower().str.startswith("chang")).sum())
        else:
            dec = {i: reasons[k].get(i, "") for i in out_items}
            if k == 10:
                dec = {i: "not selected in the item reduction (combinatorial search)" for i in out_items}
            reworded = 0
        changes.append({"to_stage_order": k, "from_stage": STAGE_LABELS[k - 1], "to_stage": STAGE_LABELS[k],
                        "n_removed": len(out_items), "removed": " ".join(out_items),
                        "n_added": len(in_items), "added": " ".join(in_items), "n_reworded": reworded,
                        "removal_labels": "; ".join(f"{i}: {d}" for i, d in dec.items() if isinstance(d, str) and d)})
    changes_df = pd.DataFrame(changes)
    changes_df.to_csv(OUT_DIR / "item-flow-changes.csv", index=False)
    (OUT_DIR / "table-item-flow-changes.tex").write_text(latex_changes(changes_df, traj), encoding="utf-8")
    (OUT_DIR / "table-p0-by-topic.tex").write_text(latex_p0_by_topic(p0, pool), encoding="utf-8")
    merge_tex, merge_df = latex_merge_pools(pool, hist, p1, p2, p3)
    merge_df.to_csv(OUT_DIR / "merge-pools.csv", index=False)
    (OUT_DIR / "table-merge-pools.tex").write_text(merge_tex, encoding="utf-8")
    p2_tex, p2_df = latex_p2_questionnaires(p2)
    p2_df.rename_axis("questionnaire").to_csv(OUT_DIR / "source-p2-by-questionnaire.csv")
    (OUT_DIR / "table-p2-questionnaires.tex").write_text(p2_tex, encoding="utf-8")

    topics = pool.set_index("item")["topic"]

    def topic_counts(stage):
        items = pres[(pres["stage_order"] == stage) & pres["source"].ne("P9")]["item"]
        return items.map(topics).fillna("(added in interviews)").value_counts()

    cols = {"pool": pool["topic"].value_counts(), "after_expert_survey_2": topic_counts(4),
            "exploratory_survey": topic_counts(8)}
    if 9 in stages:
        cols["after_screening"] = topic_counts(9)
    if 10 in stages:
        cols["validated_scale"] = topic_counts(10)
    by_topic = pd.DataFrame(cols).fillna(0).astype(int).sort_values("pool", ascending=False)
    by_topic.rename_axis("topic").to_csv(OUT_DIR / "items-by-topic.csv")

    if 10 in stages:
        final = traj[traj["in_final_scale"]][["item", "key", "source", "topic", "concept", "efa_factor", "efa_loading",
                                              "es2_mode", "es2_mean", "validation_factor", "validation_short_name",
                                              "validation_wording"]]
        final.sort_values(["validation_factor", "item"]).to_csv(OUT_DIR / "final-items.csv", index=False)
        (OUT_DIR / "table-final-items-history.tex").write_text(latex_final_items(traj, hist), encoding="utf-8")

    # --- LaTeX ----------------------------------------------------------------------
    lines = [r"\begin{table}[tbp]", r"\centering",
             r"\caption{Number of candidate items at each stage, from the merged pool to the validated scale, by source "
             r"(P0: expert suggestions; P1: UEQ+; P2: other standardized questionnaires; P3: VA literature; "
             r"P4: added in the cognitive interviews). Attention checks are not counted. "
             r"The last column gives the section that describes each stage.}",
             r"\label{tab:item-flow}", r"\small", r"\resizebox{\columnwidth}{!}{%",
             r"\begin{tabular}{lrrrrrrl}", r"\toprule",
             r"Stage & P0 & P1 & P2 & P3 & P4 & Total & Section \\", r"\midrule"]
    for i, r in flow.iterrows():
        section = rf"\ref{{{STAGE_SECTIONS[i]}}}" if STAGE_SECTIONS.get(i) else ""
        lines.append(f"{r['stage']} & {r['P0']} & {r['P1']} & {r['P2']} & {r['P3']} & {r['P4']} & "
                     f"{r['scale_items']} & {section} \\\\")
    lines += [r"\bottomrule", r"\end{tabular}}", r"\end{table}", ""]
    (OUT_DIR / "table-item-flow.tex").write_text("\n".join(lines), encoding="utf-8")
    print("table-item-flow.tex uses these labels; they must exist in the paper: "
          + ", ".join(dict.fromkeys(v for k, v in STAGE_SECTIONS.items() if k in flow.index and v)))

    # --- screen ---------------------------------------------------------------------
    print(pd.DataFrame(rows)[["source", "material", "items_in_pool"]].to_string(index=False))
    print(flow[["stage"] + SOURCES + ["scale_items"]].to_string(index=False))

    if args.check:
        ok = True
        got = flow["scale_items"].to_dict()
        expected = {k: v for k, v in EXPECTED_SCALE_ITEMS.items() if k in stages}
        if 9 not in stages or 10 not in stages:
            print("--check: phase 2.2 or phase 3 files not found; stages 9-10 not checked.")
        if got != expected:
            ok = False
            print(f"--check: DIFFERENT scale items per stage: expected {expected}, here {got}")
        if STEP03_REMOVED.exists():
            removed03 = set(pd.read_csv(STEP03_REMOVED)["team_code"])
            removed_here = sets[3] - sets[4]
            if removed03 != removed_here:
                ok = False
                print(f"--check: DIFFERENT removals after expert survey 2: step 03 {sorted(removed03 - removed_here)}, "
                      f"item history {sorted(removed_here - removed03)}")
            else:
                print("--check: the 18 items removed after expert survey 2 are those of step 03.")
        else:
            print("--check: run step 03 first to compare the removals after expert survey 2.")
        print("--check: counts agree." if ok else "--check: differences found.")
        sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
