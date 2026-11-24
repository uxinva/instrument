"""Build a self-contained HTML page with the history of every candidate item (step 04).

Writes output/item-history.html: one page, no external files or libraries, that can be opened
in any browser or published on the repository site (GitHub Pages). It shows the 99 candidate
items (95 of the merged pool, 2 added in the cognitive interviews, 2 attention checks) with
their presence at the 10 stages, and, for each item, its wording at each stage, the team's
decisions, the expert survey 2 ratings, the EFA loading, the screening decision and whether it
is in the validated scale. Items can be searched by code or words and filtered.

Reads the same files as item_flow.py and item_lookup.py (see item_tracking.py).

Run from the repository root (after data/prepare_item_sources.py):
    python phase1-item-development/04_item-flow/item_history_page.py
"""

from __future__ import annotations

import html
import json
import sys
from datetime import date
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from item_tracking import (FACTOR_NAMES, PHASE_OF_STAGE, RAW, SOURCE_NAMES, STAGE_LABELS,  # noqa: E402
                           available_stages, trajectory)

OUT = Path(__file__).resolve().parent / "output" / "item-history.html"
DERIVED_FROM = {"P40-26-A": "P0-26", "P40-26-B": "P0-26"}


def clean(v):
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return None
    if hasattr(v, "item"):
        v = v.item()
    return v


def build_records() -> tuple[list[dict], list[int]]:
    traj = trajectory()
    hist = pd.read_csv(RAW / "item-history.csv")
    stages = available_stages()
    records = []
    for _, r in traj.iterrows():
        item = r["item"]
        h = hist[hist["item"] == item].set_index("stage_order")
        steps, prev = [], None
        for s in stages:
            present = bool(r.get(f"stage_{s}", False))
            text, decision = "", ""
            if s <= 8 and s in h.index:
                text = "" if pd.isna(h.at[s, "text"]) else str(h.at[s, "text"])
                decision = "" if pd.isna(h.at[s, "decision"]) else str(h.at[s, "decision"])
            elif s == 9:
                if r.get("stage_8") and not present:
                    decision = f"excluded: {clean(r.get('screening_reason')) or ''}"
                elif present:
                    decision = "retained in the screening"
            elif s == 10:
                if present:
                    text = str(r["validation_wording"])
                elif r.get("stage_9"):
                    decision = "not selected in the item reduction"
            changed = bool(present and text and (prev is None or text.strip(" .").lower() != prev.strip(" .").lower()))
            if present and text:
                prev = text
            steps.append({"s": s, "in": present, "text": text if changed else "", "same": present and not changed,
                          "dec": decision})
        records.append({
            "item": item, "key": r["key"], "src": r["source"],
            "srcName": SOURCE_NAMES.get(r["source"], r["source"]),
            "derived": DERIVED_FROM.get(item),
            "topic": clean(r["topic"]) or "", "concept": "" if clean(r["concept"]) in (None, "__") else r["concept"],
            "optional": bool(r["optional_in_pool"]),
            "first": clean(r["first_stage"]), "last": clean(r["last_stage"]), "final": bool(r["in_final_scale"]),
            "wording": prev or "",
            "steps": steps,
            "es2": None if pd.isna(r.get("es2_mode")) else {
                "mode": int(r["es2_mode"]), "tie": bool(r["es2_mode_tie"]), "median": clean(r["es2_median"]),
                "mean": clean(r["es2_mean"]), "comments": int(r["es2_comments"])},
            "efa": None if pd.isna(r.get("efa_factor")) else {
                "factor": FACTOR_NAMES.get(r["efa_factor"], r["efa_factor"]), "loading": clean(r["efa_loading"]),
                "second": clean(r["efa_second_loading"]), "secondFactor": clean(r["efa_second_factor"]),
                "missing": clean(r["missing_pct"]), "decision": clean(r["screening_decision"]),
                "reason": clean(r["screening_reason"]) or ""},
            "val": None if not r["in_final_scale"] else {
                "factor": r["validation_factor"], "short": r["validation_short_name"]},
        })
    return records, stages


PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>History of the candidate items – UX scale for visual analytics</title>
<style>
:root{--bg:#fbfaf7;--fg:#1d1d1b;--muted:#6b6a64;--line:#e3e0d8;--card:#fff;--accent:#2f5d8a;--accent-soft:#e6eef6;
--in:#2f5d8a;--out:#d8d4ca;--final:#2e7d4f;--final-soft:#e3f1e8;--removed:#9a3b2e;--removed-soft:#f6e6e2;--mark:#fff3bf}
@media (prefers-color-scheme:dark){:root{--bg:#17181a;--fg:#e8e6e1;--muted:#a19f98;--line:#2d2f33;--card:#1f2124;
--accent:#8fb4dc;--accent-soft:#233140;--in:#8fb4dc;--out:#3a3d42;--final:#7cc79a;--final-soft:#1f3328;--removed:#e39a8c;
--removed-soft:#3a2522;--mark:#5a4b12}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.5 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
header{padding:28px 24px 8px;max-width:1180px;margin:0 auto}
h1{font-size:24px;margin:0 0 6px;font-weight:650;letter-spacing:-.01em}
.lead{color:var(--muted);margin:0 0 4px;max-width:900px}
main{max-width:1180px;margin:0 auto;padding:8px 24px 48px}
.controls{position:sticky;top:0;z-index:5;background:var(--bg);padding:12px 0 10px;border-bottom:1px solid var(--line);
display:flex;flex-wrap:wrap;gap:10px;align-items:center}
input[type=search]{flex:1 1 280px;min-width:220px;padding:9px 12px;border:1px solid var(--line);border-radius:8px;
background:var(--card);color:var(--fg);font:inherit}
select{max-width:340px;padding:8px 10px;border:1px solid var(--line);border-radius:8px;background:var(--card);color:var(--fg);font:inherit}
.count{color:var(--muted);font-size:13px;margin-left:auto}
.legend{display:flex;flex-wrap:wrap;gap:6px 18px;font-size:12.5px;color:var(--muted);padding:10px 0 4px}
.legend b{color:var(--fg);font-weight:600}
table{width:100%;border-collapse:collapse;margin-top:6px}
th{font-size:12px;text-transform:uppercase;letter-spacing:.04em;color:var(--muted);font-weight:600;text-align:left;
padding:8px 8px;border-bottom:1px solid var(--line);white-space:nowrap}
td{padding:8px;border-bottom:1px solid var(--line);vertical-align:top}
tr.row{cursor:pointer}
tr.row:hover td{background:var(--accent-soft)}
tr.row:focus{outline:2px solid var(--accent);outline-offset:-2px}
.code{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:13.5px;white-space:nowrap}
.src{display:inline-block;font-size:11.5px;font-weight:600;padding:1px 6px;border-radius:5px;background:var(--accent-soft);color:var(--accent)}
.track{display:flex;gap:3px;align-items:center}
.dot{width:14px;height:14px;border-radius:3px;background:var(--out)}
.dot.in{background:var(--in)}
.dot.in.last-final{background:var(--final)}
.res{font-size:12.5px;font-weight:600;padding:2px 7px;border-radius:5px;white-space:nowrap}
.res.final{background:var(--final-soft);color:var(--final)}
.res.out{background:var(--removed-soft);color:var(--removed)}
.wording{color:var(--fg)}
.topic{color:var(--muted);font-size:13px}
tr.detail td{background:var(--card);padding:14px 16px 18px}
.steps{width:100%;border-collapse:collapse;margin:4px 0 12px}
.steps td{border:none;border-top:1px solid var(--line);padding:6px 8px;font-size:13.5px}
.steps td.st{white-space:nowrap;color:var(--muted);width:330px}
.steps td.pr{width:56px;font-weight:600}
.steps tr.no td{color:var(--muted)}
.dec{display:inline-block;font-size:12px;color:var(--muted);border:1px solid var(--line);border-radius:5px;padding:0 6px;margin-left:6px}
.facts{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:10px}
.fact{border:1px solid var(--line);border-radius:8px;padding:8px 12px;font-size:13.5px}
.fact h4{margin:0 0 3px;font-size:12px;text-transform:uppercase;letter-spacing:.04em;color:var(--muted)}
mark{background:var(--mark);color:inherit;border-radius:2px}
footer{max-width:1180px;margin:0 auto;padding:0 24px 32px;color:var(--muted);font-size:12.5px}
.sr{position:absolute;left:-9999px}
@media (max-width:760px){.hide-sm{display:none}.steps td.st{width:auto}}
</style>
</head>
<body>
<header>
<h1>History of the candidate items</h1>
<p class="lead">UX scale for visual analytics systems: the __N__ candidate items from the merged item pool to the
validated 13-item scale. Search by item code (with or without hyphens, e.g. <span class="code">P0-26</span> or
<span class="code">P026</span>) or by words; click a row to see the item at every stage.</p>
</header>
<main>
<div class="controls" role="search">
<label class="sr" for="q">Search items</label>
<input id="q" type="search" placeholder="Code or words, e.g. P0-26, trust, easy to use" autocomplete="off">
<label class="sr" for="src">Source</label>
<select id="src"><option value="">All sources</option>__SRC_OPTIONS__</select>
<label class="sr" for="res">Result</label>
<select id="res"><option value="">All items</option><option value="final">In the validated scale</option>
__RES_OPTIONS__</select>
<span class="count" id="count" aria-live="polite"></span>
</div>
<div class="legend">__LEGEND__</div>
<table>
<thead><tr><th>Item</th><th>Source</th><th>Stages 1–__S__</th><th>Result</th><th class="hide-sm">Last wording / topic</th></tr></thead>
<tbody id="rows"></tbody>
</table>
</main>
<footer>Generated on __DATE__ by <span class="code">phase1-item-development/04_item-flow/item_history_page.py</span>
from the files of the repository. Sources: P0 experts' suggestions (expert survey 1), P1 UEQ+ scales, P2 other
standardized questionnaires, P3 VA literature, P4 added in the cognitive interviews, P9 attention checks.
Expert survey 2: relevance from 1 = never to 5 = always relevant (32 experts); statements with mode ≤ 3 were removed.</footer>
<script>
const DATA = __DATA__;
const STAGES = __STAGES__;
const LEVEL = {1:"never",2:"not often",3:"sometimes",4:"frequently",5:"always"};
const $ = s => document.querySelector(s);
const esc = s => String(s ?? "").replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const key = s => String(s).toUpperCase().replace(/[^A-Z0-9]/g, "");
let open = new Set();

function terms(){ const q = $("#q").value.trim(); return q ? q.toLowerCase().split(/\\s+/) : []; }
function hl(text){
  let t = esc(text); const ws = terms().filter(w => w.length > 1 && !/^p\\d/.test(w));
  for (const w of ws){ t = t.replace(new RegExp("(" + w.replace(/[.*+?^${}()|[\\]\\\\]/g,"\\\\$&") + ")","gi"), "<mark>$1</mark>"); }
  return t;
}
function matches(d){
  const q = $("#q").value.trim(); if (!q) return true;
  if (/^p\\s*\\d[\\d\\s-]*[a-z]?$/i.test(q)) { const k = key(q); return d.key === k || d.key.startsWith(k); }
  const hay = [d.item, d.topic, d.concept, d.wording, ...d.steps.map(s => s.text), ...d.steps.map(s => s.dec)].join(" ").toLowerCase();
  return terms().every(w => hay.includes(w));
}
function resultOf(d){
  if (d.final) return `<span class="res final">Final scale</span>`;
  if (d.src === "P9") return `<span class="res">attention check</span>`;
  if (d.last == null) return `<span class="res out">never used</span>`;
  return `<span class="res out" title="last present at stage ${d.last}">removed at stage ${d.last + 1}</span>`;
}
function track(d){
  return `<div class="track" aria-label="present at stages ${d.steps.filter(s=>s.in).map(s=>s.s).join(', ')}">` +
    d.steps.map(s => `<span class="dot ${s.in ? "in" : ""} ${s.in && d.final ? "last-final" : ""}" title="${s.s}. ${esc(STAGES[s.s])}: ${s.in ? "present" : "absent"}"></span>`).join("") + `</div>`;
}
function detail(d){
  const rows = d.steps.map(s => {
    let note = s.text ? `“${hl(s.text)}”` : (s.same ? `<span class="topic">same wording</span>` : "");
    if (s.dec) note += `<span class="dec">${esc(s.dec)}</span>`;
    return `<tr class="${s.in ? "" : "no"}"><td class="st">${s.s}. ${esc(STAGES[s.s])}</td><td class="pr">${s.in ? "yes" : "–"}</td><td>${note}</td></tr>`;
  }).join("");
  const facts = [];
  facts.push(`<div class="fact"><h4>Origin</h4>${esc(d.src)} – ${esc(d.srcName)}${d.derived ? `, derived from ${esc(d.derived)}` : ""}` +
    (d.topic ? `<br>Topic: ${hl(d.topic)}${d.concept ? ` · concept: ${hl(d.concept)}` : ""}` : "") +
    (d.optional ? `<br>Marked optional in the pool` : "") + `<br>Code in the surveys and phases 2–3: <span class="code">${esc(d.key)}</span></div>`);
  if (d.es2) facts.push(`<div class="fact"><h4>Expert survey 2</h4>Mode ${d.es2.mode} (${LEVEL[d.es2.mode]} relevant)${d.es2.tie ? ", two modes (first in expert order)" : ""}` +
    `<br>Median ${d.es2.median}, mean ${d.es2.mean.toFixed(2)}, ${d.es2.comments} comment${d.es2.comments === 1 ? "" : "s"}` +
    (d.es2.mode <= 3 ? `<br><b>Removed (mode ≤ 3)</b>` : "") + `</div>`);
  if (d.efa) facts.push(`<div class="fact"><h4>EFA and item reduction</h4>${esc(d.efa.factor)}, loading ${d.efa.loading.toFixed(3)}` +
    `<br>Second highest ${d.efa.second.toFixed(3)} (${esc(d.efa.secondFactor)}); missing ${d.efa.missing}%` +
    `<br>Screening: ${esc(d.efa.decision)}${d.efa.reason ? " – " + esc(d.efa.reason) : ""}</div>`);
  if (d.val) facts.push(`<div class="fact"><h4>Validated scale</h4>${esc(d.val.factor)} · <span class="code">${esc(d.val.short)}</span></div>`);
  return `<table class="steps">${rows}</table><div class="facts">${facts.join("")}</div>`;
}
function render(){
  const src = $("#src").value, res = $("#res").value;
  const list = DATA.filter(d => matches(d) && (!src || d.src === src) &&
    (!res || (res === "final" ? d.final : (!d.final && d.src !== "P9" && String(d.last + 1) === res))));
  const autoOpen = list.length === 1;
  $("#rows").innerHTML = list.map(d => {
    const isOpen = autoOpen || open.has(d.item);
    const sub = d.topic ? `<div class="topic">${hl(d.topic)}${d.concept ? " · " + hl(d.concept) : ""}</div>` : "";
    return `<tr class="row" tabindex="0" data-item="${esc(d.item)}" aria-expanded="${isOpen}">` +
      `<td class="code">${hl(d.item)}</td><td><span class="src">${esc(d.src)}</span></td><td>${track(d)}</td>` +
      `<td>${resultOf(d)}</td><td class="hide-sm"><div class="wording">${hl(d.wording)}</div>${sub}</td></tr>` +
      (isOpen ? `<tr class="detail"><td colspan="5">${detail(d)}</td></tr>` : "");
  }).join("");
  $("#count").textContent = `${list.length} of ${DATA.length} items`;
}
document.addEventListener("click", e => { const tr = e.target.closest("tr.row"); if (!tr) return;
  const it = tr.dataset.item; open.has(it) ? open.delete(it) : open.add(it); render(); });
document.addEventListener("keydown", e => { if ((e.key === "Enter" || e.key === " ") && e.target.matches("tr.row")) { e.preventDefault(); e.target.click(); }});
["#q", "#src", "#res"].forEach(s => $(s).addEventListener("input", render));
const params = new URLSearchParams(location.search); if (params.get("q")) $("#q").value = params.get("q");
render();
</script>
</body>
</html>
"""


def main() -> None:
    records, stages = build_records()
    sources = sorted({r["src"] for r in records})
    src_options = "".join(f'<option value="{s}">{s} – {html.escape(SOURCE_NAMES.get(s, s))}</option>' for s in sources)
    res_options = "".join(f'<option value="{s + 1}">Removed at stage {s + 1}: {html.escape(STAGE_LABELS[s + 1])}</option>'
                          for s in stages[:-1]
                          if any((not r["final"]) and r["src"] != "P9" and r["last"] == s for r in records))
    legend = " ".join(f"<span><b>{s}</b> {html.escape(STAGE_LABELS[s])}</span>" for s in stages)
    page = (PAGE.replace("__DATA__", json.dumps(records, ensure_ascii=False))
                .replace("__STAGES__", json.dumps({s: STAGE_LABELS[s] for s in stages}))
                .replace("__SRC_OPTIONS__", src_options).replace("__RES_OPTIONS__", res_options)
                .replace("__LEGEND__", legend).replace("__S__", str(stages[-1]))
                .replace("__N__", str(len(records))).replace("__DATE__", date.today().isoformat()))
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(page, encoding="utf-8")
    print(f"Written {OUT} ({len(records)} items, {len(stages)} stages).")


if __name__ == "__main__":
    main()
