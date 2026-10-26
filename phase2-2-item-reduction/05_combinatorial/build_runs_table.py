"""
Builds the summary of the combinatorial reduction runs and the paper table from the output
folders written by the R pipeline (05_combinatorial.Rmd, or Reproduce8 in May 2026).

For each run folder it reads:
  *tested_reliability_sets.csv           -> subsets tested / passing reliability, per scale
  *all_reliability_cfa_results.csv       -> CFA models fitted
  *passing_reliability_cfa_results.csv   -> models passing model fit, Task_cognition subsets
The threshold comes from run_info.txt (new runs) or from the folder name (May runs, "Reliability0XX").

Rows for thresholds that were not run (e.g. 0.80) can be derived with --derive: the subsets
passing reliability are counted from the reliability scores of a run with the same arrangement;
if any scale has no subset, no CFA model can be formed (0 models). Otherwise the row is not derived.

Outputs (05_combinatorial/output/):
  runs_summary.csv               one row per run (and derived row)
  table_combinatorial_runs.tex   paper table for the thresholds given in --table
  final_reliability_sets.csv / table_final_reliability_sets.tex
                                 subsets passing reliability in the final run (--final), with alpha and omega
  final_item_frequency.csv / table_final_item_frequency.tex
                                 how often each item appears in the models passing model fit in the final run
  selected-model.csv / table-selected-model.tex
                                 the selected instrument (items, wording, reliability) and its fit, compared with
                                 the alternatives listed in input/selected-models.csv

Which runs are used:
  - by default, the runs made in the repository by run-all-thresholds.R
    (output/rel0XX_<arrangement>_singlegroup_uncollapsed/), all exhaustive;
  - with --may, the original May 2026 folders in Gdrive_files (0.70-0.72 cut at 1,000 models);
  - with --runs, the folders given.
When both the repository runs and the May folders are available, checks-vs-may.txt compares them
run by run (expected: identical, except the models fitted/passing of the May runs cut at 1,000).

Run from the repository root:
  python phase2-2-item-reduction/05_combinatorial/build_runs_table.py
  python phase2-2-item-reduction/05_combinatorial/build_runs_table.py --may
"""
from pathlib import Path
import argparse
import glob
import re

import pandas as pd

STEP = Path(__file__).resolve().parent
ROOT = STEP.parents[1]
MAY = ROOT / "Gdrive_files" / "Item Reduction" / "Reliability_CFA_Analysis"
LOCAL_RUNS = STEP / "output"
LOCAL_FINAL = LOCAL_RUNS / "rel078_6-4-3_singlegroup_uncollapsed"
COMPARE = ["tested_Task", "tested_Vis", "tested_Sys", "pass_reliability_Task", "pass_reliability_Vis",
           "pass_reliability_Sys", "candidate_models", "models_fitted", "models_passing_fit", "tc_subsets_in_passing"]
SCALES = ["task_cognition", "visualization", "system"]
SHORT = {"task_cognition": "Task", "visualization": "Vis", "system": "Sys"}


def find(folder, suffix):
    hits = sorted(glob.glob(str(Path(folder) / f"*{suffix}")))
    return hits[0] if hits else None


def threshold_of(folder):
    info = Path(folder) / "run_info.txt"
    if info.exists():
        m = re.search(r"reliability_threshold:\s*([0-9.]+)", info.read_text(encoding="utf-8"))
        if m:
            return float(m.group(1))
    m = re.search(r"Reliability0(\d\d)", str(folder))
    if m:
        return int(m.group(1)) / 100
    raise ValueError(f"No threshold found for {folder}")


def summarise(folder):
    tested = pd.read_csv(find(folder, "tested_reliability_sets.csv"))
    tested["n_items"] = tested["combination"].str.count(",") + 1
    n_items = {s: int(tested.loc[tested.scale == s, "n_items"].iloc[0]) for s in SCALES}
    n_tested = {s: int((tested.scale == s).sum()) for s in SCALES}
    n_pass = {s: int(tested.loc[tested.scale == s, "reliability_pass"].sum()) for s in SCALES}
    candidates = n_pass["task_cognition"] * n_pass["visualization"] * n_pass["system"]

    all_file, pass_file = find(folder, "all_reliability_cfa_results.csv"), find(folder, "passing_reliability_cfa_results.csv")
    fitted = len(pd.read_csv(all_file)) if all_file else 0
    passing = pd.read_csv(pass_file) if pass_file else pd.DataFrame(columns=["task_cognition_items"])
    tc_counts = passing["task_cognition_items"].value_counts()
    tc_sets = "; ".join(f"{k.replace('__', ', ')} ({v})" for k, v in tc_counts.items())

    return dict(
        run=Path(folder).name, source="run", threshold=threshold_of(folder),
        arrangement=" / ".join(str(n_items[s]) for s in SCALES),
        **{f"tested_{SHORT[s]}": n_tested[s] for s in SCALES},
        **{f"pass_reliability_{SHORT[s]}": n_pass[s] for s in SCALES},
        candidate_models=candidates, models_fitted=fitted, truncated=fitted < candidates,
        models_passing_fit=len(passing), n_tc_subsets_passing=len(tc_counts), tc_subsets_in_passing=tc_sets,
        _scores=tested[["scale", "n_items", "reliability_score"]],
    )


def derive(rows, thr):
    """Derived row for a threshold that was not run, per arrangement."""
    out = []
    for arr in sorted({r["arrangement"] for r in rows}):
        if any(r["arrangement"] == arr and abs(r["threshold"] - thr) < 1e-9 for r in rows):
            continue
        ref = next(r for r in rows if r["arrangement"] == arr)
        sc = ref["_scores"]
        n_pass = {s: int((sc.loc[sc.scale == s, "reliability_score"] >= thr).sum()) for s in SCALES}
        if min(n_pass.values()) > 0:
            print(f"Not derived: {arr} at {thr} would need CFA runs ({n_pass})")
            continue
        out.append(dict(
            run=f"derived from {ref['run']}", source="derived", threshold=thr, arrangement=arr,
            **{f"tested_{SHORT[s]}": ref[f"tested_{SHORT[s]}"] for s in SCALES},
            **{f"pass_reliability_{SHORT[s]}": n_pass[s] for s in SCALES},
            candidate_models=0, models_fitted=0, truncated=False, models_passing_fit=0,
            n_tc_subsets_passing=0, tc_subsets_in_passing=""))
    return out


def tex_escape(s):
    return s.replace("_", "\\_").replace("&", "\\&").replace("%", "\\%")


def latex(df, thresholds):
    t = df.copy() if not thresholds else df[df.threshold.round(2).isin([round(x, 2) for x in thresholds])].copy()
    t = t.sort_values(["arrangement", "threshold"], ascending=[True, False])
    lines = [
        "% Generated by phase2-2-item-reduction/05_combinatorial/build_runs_table.py -- do not edit by hand",
        "% Needs \\usepackage{array} and \\usepackage{graphicx} (\\resizebox); table* spans both columns of a two-column layout",
        "\\begin{table*}[htbp]", "\\centering", "\\small",
        "\\caption{Automated combinatorial search: item subsets passing the reliability prefilter and CFA "
        "models passing the global fit criteria, by reliability threshold and number of items per factor. "
        "Single-group CFA (all tools pooled), MLR estimator, FIML, uncollapsed ratings.}",
        "\\label{tab:combinatorial-search}",
        "\\resizebox{\\linewidth}{!}{%",
        "\\begin{tabular}{ccccccc>{\\raggedright\\arraybackslash}p{3.8cm}}", "\\hline",
        "Items & Reliability & \\multicolumn{3}{c}{Subsets passing reliability} & CFA models & Models passing & Task\\_cognition subset \\\\",
        "(Task / Vis / Sys) & threshold ($\\alpha$ or $\\omega$) & Task & Vis & Sys & fitted & model fit & in passing models \\\\",
        "\\hline",
    ]
    # footnote letters in order of use: a, b, ...
    marks = {}
    if t.truncated.any():
        marks["truncated"] = chr(ord("a") + len(marks))
    if (t.source == "derived").any():
        marks["derived"] = chr(ord("a") + len(marks))
    notes, prev = [], None
    for _, r in t.iterrows():
        if prev is not None and r.arrangement != prev:
            lines.append("\\hline")
        prev = r.arrangement
        fitted = f"{r.models_fitted:,}"
        if r.truncated:
            m = marks["truncated"]
            fitted += f"$^{{{m}}}$"
            notes.append(f"$^{{{m}}}$ {r.candidate_models:,} candidate models; the run was limited to the first {r.models_fitted:,}.")
        if r.source == "derived":
            fitted += f"$^{{{marks['derived']}}}$"
        tc = r.tc_subsets_in_passing if r.n_tc_subsets_passing <= 2 else f"{r.n_tc_subsets_passing} subsets"
        lines.append(" & ".join([r.arrangement, f"{r.threshold:.2f}", str(r.pass_reliability_Task),
                                 str(r.pass_reliability_Vis), str(r.pass_reliability_Sys), fitted,
                                 f"{r.models_passing_fit:,}", tex_escape(tc) or "--"]) + " \\\\")
    lines.append("\\hline")
    tested = "; ".join(f"{a}: {g.tested_Task.iloc[0]}, {g.tested_Vis.iloc[0]} and {g.tested_Sys.iloc[0]}"
                       for a, g in t.groupby("arrangement"))
    foot = (f"Subsets tested in the reliability prefilter (Task, Vis, Sys) -- {tested}. "
            "CFA models fitted = product of the subsets passing reliability. Reliability criterion: "
            "Cronbach's $\\alpha$ or McDonald's $\\omega$ $\\geq$ threshold. Model fit criterion: "
            "(CFI or TLI $\\geq$ 0.95) and (SRMR $\\leq$ 0.08 or RMSEA $\\leq$ 0.06).")
    if (t.source == "derived").any():
        notes.append(f"$^{{{marks['derived']}}}$ Threshold not run; derived from the reliability of the subsets (no model can be formed).")
    # notes below the scaled tabular, so that they keep the normal footnote size
    lines += ["\\end{tabular}}", "\\par\\smallskip", "{\\footnotesize\\raggedright " + foot + "\\par"]
    if notes:
        lines.append(" ".join(dict.fromkeys(notes)) + "\\par")
    lines += ["}", "\\end{table*}"]
    return "\n".join(lines) + "\n"


def final_tables(folder, out):
    """Reliability of the retained subsets and item frequency in the passing models of one run."""
    thr = threshold_of(folder)
    tested = pd.read_csv(find(folder, "tested_reliability_sets.csv"))
    kept = tested[tested.reliability_pass].copy()
    kept["scale"] = pd.Categorical(kept.scale, SCALES, ordered=True)
    kept = kept.sort_values(["scale", "reliability_score"], ascending=[True, False])
    kept[["scale", "combination", "alpha", "omega_total", "reliability_score"]].to_csv(
        out / "final_reliability_sets.csv", index=False)

    passing = pd.read_csv(find(folder, "passing_reliability_cfa_results.csv"))
    n = len(passing)
    freq = []
    for s_ in SCALES:
        counts = passing[f"{s_}_items"].str.split("__").explode().value_counts()
        pool = sorted({i for c in tested.loc[tested.scale == s_, "combination"] for i in c.split(",")})
        for item in pool:
            freq.append(dict(scale=s_, item=item, n_models=int(counts.get(item, 0)),
                             pct_models=round(100 * counts.get(item, 0) / n, 1)))
    freq = pd.DataFrame(freq).sort_values(["scale", "n_models"], ascending=[True, False],
                                          key=lambda c: c.map({k: i for i, k in enumerate(SCALES)}) if c.name == "scale" else c)
    freq.to_csv(out / "final_item_frequency.csv", index=False)

    label = {"task_cognition": "Task\\_cognition", "visualization": "Visualization", "system": "System"}
    # table: retained subsets
    L = ["% Generated by phase2-2-item-reduction/05_combinatorial/build_runs_table.py -- do not edit by hand",
         "\\begin{table}[htbp]", "\\centering", "\\small",
         f"\\caption{{Item subsets passing the reliability prefilter ($\\alpha$ or $\\omega$ $\\geq$ {thr:.2f}) in the final run.}}",
         "\\label{tab:combinatorial-reliability-sets}", "\\begin{tabular}{llcc}", "\\hline",
         "Factor & Items & $\\alpha$ & $\\omega$ \\\\", "\\hline"]
    for s_ in SCALES:
        g = kept[kept.scale == s_]
        for i, (_, r) in enumerate(g.iterrows()):
            L.append(f"{label[s_] if i == 0 else ''} & {r.combination.replace(',', ', ')} & {r.alpha:.3f} & {r.omega_total:.3f} \\\\")
        L[-1] += " \\hline"
    L += ["\\end{tabular}", "\\end{table}"]
    (out / "table_final_reliability_sets.tex").write_text("\n".join(L) + "\n", encoding="utf-8")
    # table: item frequency
    L = ["% Generated by phase2-2-item-reduction/05_combinatorial/build_runs_table.py -- do not edit by hand",
         "\\begin{table}[htbp]", "\\centering", "\\small",
         f"\\caption{{Number of models passing model fit (out of {n}) that include each candidate item, final run.}}",
         "\\label{tab:combinatorial-item-frequency}", "\\begin{tabular}{llrr}", "\\hline",
         "Factor & Item & Models & \\% \\\\", "\\hline"]
    for s_ in SCALES:
        g = freq[freq.scale == s_]
        for i, (_, r) in enumerate(g.iterrows()):
            L.append(f"{label[s_] if i == 0 else ''} & {r['item']} & {r.n_models} & {r.pct_models:.1f} \\\\")
        L[-1] += " \\hline"
    L += ["\\end{tabular}", "\\end{table}"]
    (out / "table_final_item_frequency.tex").write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"Final run: {Path(folder).name} ({len(kept)} retained subsets, {n} passing models)")


SCALE_NAME = {"visualization": "Visualization", "task_cognition": "Cognitive Value", "system": "Intuitiveness"}


def selected_model_table(folder, out):
    """Selected instrument and the alternatives in input/selected-models.csv, looked up in one run."""
    spec = pd.read_csv(STEP / "input" / "selected-models.csv")
    wording = pd.read_csv(STEP.parent / "data" / "codebook" / "items.csv").set_index("code")["wording"]
    passing = pd.read_csv(find(folder, "passing_reliability_cfa_results.csv"))
    passing["rank"] = range(1, len(passing) + 1)   # file is ordered by CFI, TLI, RMSEA, SRMR
    key = lambda items: "__".join(sorted(items.split(",")))
    passing["key"] = passing[[f"{s_}_items" for s_ in SCALES]].apply(
        lambda r: "|".join("__".join(sorted(x.split("__"))) for x in r), axis=1)

    rows = []
    for _, m in spec.iterrows():
        k = "|".join(key(m[s_]) for s_ in SCALES)
        hit = passing[passing.key == k]
        if hit.empty:
            raise SystemExit(f"{m.label}: not among the models passing model fit in {folder}")
        h = hit.iloc[0]
        rows.append(dict(role=m.role, label=m.label, rank=int(h["rank"]), n_passing=len(passing),
                         **{f"{s_}_items": m[s_] for s_ in SCALES},
                         CFI=h.CFI, TLI=h.TLI, RMSEA=h.RMSEA, SRMR=h.SRMR,
                         **{f"alpha_{s_}": h[f"alpha_{s_}"] for s_ in SCALES},
                         **{f"omega_{s_}": h[f"omega_{s_}"] for s_ in SCALES}))
    res = pd.DataFrame(rows)
    res.to_csv(out / "selected-model.csv", index=False)

    sel = res[res.role == "selected"].iloc[0]
    order = ["system", "task_cognition", "visualization"]
    n_items = sum(len(sel[f"{s_}_items"].split(",")) for s_ in SCALES)
    L = ["% Generated by phase2-2-item-reduction/05_combinatorial/build_runs_table.py -- do not edit by hand",
         "\\begin{table}[htbp]", "\\centering", "\\small",
         f"\\caption{{Selected {n_items}-item instrument (item-reduction sample). Panel A: items and scale reliability. "
         f"Panel B: global fit of the selected model and of the alternatives considered, with their rank among the "
         f"{len(passing)} models passing model fit (ordered by CFI). Single-group CFA, MLR, uncollapsed data.}}",
         "\\label{tab:selected-model}",
         "\\begin{tabular}{llp{8.5cm}}", "\\hline",
         "\\multicolumn{3}{l}{\\textit{Panel A. Items}} \\\\", "\\hline",
         "Scale & Code & Item \\\\", "\\hline"]
    for s_ in order:
        items = sel[f"{s_}_items"].split(",")
        L.append(f"\\multicolumn{{3}}{{l}}{{{SCALE_NAME[s_]} ({len(items)} items; "
                 f"$\\alpha$ = {sel[f'alpha_{s_}']:.3f}, $\\omega$ = {sel[f'omega_{s_}']:.3f})}} \\\\")
        for it in items:
            L.append(f" & {it} & {tex_escape(wording.get(it, ''))} \\\\")
    L += ["\\hline", "\\end{tabular}", "", "\\vspace{0.6em}",
          "\\begin{tabular}{lp{3.2cm}rcccc}", "\\hline",
          "\\multicolumn{7}{l}{\\textit{Panel B. Global fit}} \\\\", "\\hline",
          "Model & Intuitiveness items & Rank & CFI & TLI & RMSEA & SRMR \\\\", "\\hline"]
    for _, r in res.iterrows():
        L.append(f"{tex_escape(r.label)} & {r.system_items.replace(',', ', ')} & {r['rank']} & "
                 f"{r.CFI:.3f} & {r.TLI:.3f} & {r.RMSEA:.3f} & {r.SRMR:.3f} \\\\")
    L += ["\\hline",
          "\\multicolumn{7}{p{0.9\\linewidth}}{\\footnotesize Benchmarks: CFI and TLI $\\geq$ 0.95; RMSEA $\\leq$ 0.06; "
          "SRMR $\\leq$ 0.08. The models differ only in the Intuitiveness (System) items.} \\\\",
          "\\end{tabular}", "\\end{table}"]
    (out / "table-selected-model.tex").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("Selected model: rank", int(sel["rank"]), "of", len(passing))


def may_folders():
    return sorted(glob.glob(str(MAY / "2605*"))) + sorted(glob.glob(str(MAY / "4_factors_task_cognition" / "2605*")))


def local_folders():
    return sorted(str(Path(f).parent) for f in
                  glob.glob(str(LOCAL_RUNS / "rel0*_singlegroup_uncollapsed" / "passing_reliability_cfa_results.csv")))


def compare_with_may(local_rows, out):
    """Repository runs versus May runs with the same threshold and arrangement."""
    if not may_folders():
        return
    may = {(r["arrangement"], r["threshold"]): r for r in (summarise(f) for f in may_folders())}
    lines = ["Repository runs versus May 2026 runs (same threshold and arrangement)", ""]
    for r in sorted(local_rows, key=lambda r: (r["arrangement"], -r["threshold"])):
        m = may.get((r["arrangement"], r["threshold"]))
        tag = f"{r['arrangement']} {r['threshold']:.2f}"
        if m is None:
            lines.append(f"--   {tag}: no May run")
            continue
        diff = [k for k in COMPARE if r[k] != m[k]]
        if not diff:
            lines.append(f"OK   {tag}: identical")
        elif m["truncated"] and set(diff) <= {"models_fitted", "models_passing_fit", "tc_subsets_in_passing"}:
            lines.append(f"CUT  {tag}: May fitted {m['models_fitted']} of {m['candidate_models']} "
                         f"({m['models_passing_fit']} passing); now {r['models_fitted']} ({r['models_passing_fit']} passing)")
        else:
            lines.append(f"DIFF {tag}: " + "; ".join(f"{k} May {m[k]} / now {r[k]}" for k in diff))
    (out / "checks-vs-may.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", nargs="*", help="run folders (default: the repository runs, else the May folders)")
    ap.add_argument("--may", action="store_true", help="use the original May 2026 folders")
    ap.add_argument("--derive", nargs="*", type=float, default=[0.80])
    ap.add_argument("--table", nargs="*", type=float, default=[],
                    help="thresholds shown in the paper table (default: all runs and derived rows)")
    ap.add_argument("--final", help="run folder of the final run (default: threshold 0.78, 6/4/3)")
    a = ap.parse_args()
    local = local_folders()
    use_local = not a.runs and not a.may and bool(local)
    folders = a.runs or (local if use_local else may_folders())
    print(f"Using {'repository' if use_local else 'May 2026' if not a.runs else 'given'} runs: {len(folders)} folders")

    rows = [summarise(f) for f in folders]
    out = STEP / "output"
    out.mkdir(exist_ok=True)
    if use_local:
        compare_with_may(rows, out)
    for thr in a.derive:
        rows += derive(rows, thr)
    df = pd.DataFrame([{k: v for k, v in r.items() if k != "_scores"} for r in rows])
    df = df.sort_values(["arrangement", "threshold"], ascending=[True, False])

    df.to_csv(out / "runs_summary.csv", index=False)
    (out / "table_combinatorial_runs.tex").write_text(latex(df, a.table), encoding="utf-8")
    final = a.final or (str(LOCAL_FINAL) if use_local and LOCAL_FINAL.exists() else
                        str(MAY / "4_factors_task_cognition" / "260506Data_AnalysisReliability078-4taskCFAExploration-100best"))
    print("Final run:", final)
    final_tables(final, out)
    if (STEP / "input" / "selected-models.csv").exists():
        selected_model_table(final, out)
    print(df.drop(columns=["run", "tc_subsets_in_passing"]).to_string(index=False))
    print(f"\nWrote runs_summary.csv, table_combinatorial_runs.tex, final_reliability_sets.csv, "
          f"table_final_reliability_sets.tex, final_item_frequency.csv, table_final_item_frequency.tex, selected-model.csv and table-selected-model.tex to {out}")


if __name__ == "__main__":
    main()
