# Phase 2.1: scale development (context)

State as of **2026-11-12**. Git folder `phase2-1-scale-development/` (repository `GitInstrument`), created empty.

## Goal

Document and make reproducible the phase that produced the **65-item, three-factor EFA solution** that item reduction (phase 2.2) starts from. To be confirmed with Eliane: which earlier steps (item development, expert review, pilot) enter this folder, or only the EFA.

## What is already known (from phase 2.2)

- **Data:** 65 items rated by **506 participants** on a −3 … +3 scale. Tools (stimulus): Gephi 104, Power BI 102, Qlik 101, Tableau 100, JMP 99. In the repository: `phase2-2-item-reduction/data/raw/ratings-stimulus_original.csv` (uncollapsed, MD5 `2e967d9c37a6f2f1d2d7e79505a3dbb3`) and `data/prepared/ratings-stimulus_collapsed.csv` (options chosen by ≤ 2.5% merged; MD5 `eb83954b17ac6ef2149f63f4f7c0c572`, built by `data/prepare_data.py`).
- **Tool labels:** an old collapsed file had Tableau ↔ Power BI and Gephi ↔ JMP swapped; the corrected file agrees with the survey export for all 506 participants.
- **EFA used by phase 2.2:** 3 factors, run of 2026-03-18, polychoric correlations, principal axis, collapsed data (2.5%). A 4-factor solution was also run (basis of Version E in phase 2.2).
- **Where the EFA lives now (outside this folder):** `UXVis/Replication…` and `Gdrive_files/Exploratory Factor Analysis - temp/`. Phase 2.2 step 00 copies the loadings it needs: `phase2-2-item-reduction/00-efa-screening/input/efa-pa-3-factors-agg.csv` (MD5 `2f937169c9d566d693c9ba1c2a43ef53`).
- **Open point carried over:** P049, whether it was removed for redundancy with P041 (meeting of 2025-11-25) before the EFA.

## Plan (to be agreed)

1. Inventory the existing EFA scripts and spreadsheets (`Gdrive_files/Exploratory Factor Analysis - temp/`, `UXVis/Replication…`).
2. Decide the steps of the folder, e.g. `00_data`, `01_factorability` (KMO, Bartlett), `02_number-of-factors` (parallel analysis…), `03_efa` (3 and 4 factors), following the layout of the other phases.
3. Reproduce the 2026-03-18 loadings and check them against `efa-pa-3-factors-agg.csv`.
4. Then point phase 2.2 step 00 to the outputs of this phase.

## Decisions

*None yet.*

## Pending

- Everything in the plan.
