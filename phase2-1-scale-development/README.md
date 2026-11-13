# Phase 2.1: Scale development

> **Status:** started on 2026-11-12. The steps are being documented.

This phase produces the **65-item, three-factor exploratory factor analysis (EFA)** solution that the [item reduction phase](../phase2-2-item-reduction/README.md) starts from.

- **Data:** 65 items rated by 506 participants (Gephi, Power BI, Qlik, Tableau, JMP), in [`data/`](data/README.md): raw ratings, the script that checks the tool labels and collapses rare answer options, and the item codebook. Phase 2.2 and steps 07–08 of phase 3 read the same files.

## Steps

| Step | Content | Status |
|---|---|---|
| [`01_efa/`](01_efa/README.md) | EFA (polychoric, principal axis, 1–6 factors) on the whole sample and on each tool; factorability, parallel analysis, fit indices | Reproduces the run of 2026-03-18 (\|difference\| < 1e-6) |

The steps follow the layout of the other phases: a `data/` folder and numbered steps `NN_step-name/`, each with a README, a notebook or scripts, the rendered report and an `output/` folder.
