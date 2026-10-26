# 04 Multi-criteria triangulation ranking

**Scripts:** [`extract_ranking_criteria.py`](extract_ranking_criteria.py) (run once) · [`build_ranking_table.py`](build_ranking_table.py) · [`build-irt-ranking-table.py`](build-irt-ranking-table.py)

## What it does

For the 49 items kept after the factor-loading screen (Version A, Model_1), three criteria rank the items of each factor (1 = best):

| Criterion | Value | Rank |
|---|---|---|
| **Reliability** | Cronbach's α of the full factor if the item is dropped | lowest α first: the items whose removal lowers reliability the most |
| **Factor loading** | λ in the 3-factor EFA (collapsed data, tab *Loadings*, column "Collapse 2.5") | highest λ first |
| **IRT** | Scores 0–3 given to each trace plot for monotonicity, discrimination, middle-category intersection / non-redundancy and latent-trait coverage | rank agreed in the IRT meetings |

The **priority** is the list agreed by the team after looking at the three ranks together (triangulation). It is a judgement, not a formula. There are two versions:

| Column | When | Source | Used for |
|---|---|---|---|
| `priority` (*First*) | April 2026 | `Ranking revisited considering reliabitiy- loadings- and IRT.xlsx` | Model_3 of Versions A–D |
| `priority_final` (*Final*) | May 2026, when Petra Isenberg and Anne-Flore Cabouat chose the candidate pool of the combinatorial search | `Ranking revisited 2 - AfterHandpickedItemsbyAFandP- … .xlsx`; pool in `handpicked_items_list_by_factor.csv`; history in `Historic of handpicked_items_list_by_factor.pdf` | candidate pool of `05_combinatorial` |

The revision changed:
- **System:** P074 entered at 3 and P024 left;
- **Visualization:** P05 (6) and P067 (7) entered;
- **Task_cognition:** nothing changed. The pool takes priorities 1–5 (P062, P064, P060, P027, P301).

The other columns of the two spreadsheets are identical; `extract_ranking_criteria.py` checks this. P045A was set aside by Anne-Flore: "P045A load poorly on this factor (.31) so we don't want to keep it as an option".

The reasons recorded for the items are in the `considerations` column of `ranking_table_full.csv`, completed on 2026-10-20 with the reasons given by Petra and Anne-Flore (`Gdrive_files/Item Reduction/ranking_table_full.xlsx`). For example, P041 is first in IRT but was not prioritized because it seems to belong to the system factor.

**Open point.** In `ranking_table_full.xlsx`, P074 has priority 5, tied with P026. In `Ranking revisited 2` it has priority 3, which matches the order of the handpicked list (P214, P088, P074, P4026A, P026). The extraction uses 3 and prints a NOTE.

The reduced models are the top 5 of one criterion each:

| Model | Top 5 by | Check |
|---|---|---|
| Model_1 (Versions B–D) | factor loading | matches `item_versions_config.R` |
| Model_2 (Version A) | IRT rank | matches |
| Model_3 (Version A) | first priority | matches. In visualization, P022A and P089 are tied at priority 2: Version A uses P089, Versions B–D use P022A |

A further check confirms that the candidate pool of `05_combinatorial` is the top of the final priority in each factor (1–5, 1–5 and 1–7).

`checks.txt` records these checks. It also checks that every reliability and loading rank follows its value. The build stops if a rank does not.

## Inputs

| File | Content |
|---|---|
| `ranking_criteria.csv` | Per item: factor, α if dropped and rank, λ and rank, the four IRT scores, IRT rank, first and final priority, considerations. Made by `extract_ranking_criteria.py` from three files in `Gdrive_files/Item Reduction/`: `Ranking revisited considering reliabitiy- loadings- and IRT.xlsx` and `Ranking revisited 2 - AfterHandpickedItemsbyAFandP- … .xlsx` (tab *3 fators merged*), and `ranking_table_full.xlsx` (considerations) |
| `../05_combinatorial/input/candidate_pool.csv` | Handpicked candidate pool, used only for the checks |
| `../data/codebook/items.csv` | Item wording |
| `../item_versions_config.R` | Model item lists, used only for the checks |

## Outputs (`output/`)

| File | Content |
|---|---|
| `ranking_table_main.tex` | **Paper table** (`tab:triangulation-ranking`, main text): prioritized items of each factor with the three ranks side by side, and the criteria in which each item is in the top 5. Made by `build_ranking_table.py` |
| `ranking_table_full.csv` | **Supplementary material**: all 49 items with values, ranks, IRT scores, priority, mean rank and the considerations recorded in the meetings. Since 2026-10-19 it is no longer typeset as a LaTeX table |
| `checks.txt` | Consistency checks |
| `irt-ranking-table.tex` | **Appendix table** (`tab:IRT-ranking`, `longtable`): the four trace-plot scores, their total (0–12) and the IRT rank of the 49 items. Made by [`build-irt-ranking-table.py`](build-irt-ranking-table.py) |
| `irt-ranking-table.csv` | The same as CSV |
| `irt-checks.txt` | How far the IRT rank follows the total of the scores, per factor |

**The IRT rank is not the sum of the scores.** It was agreed in the meetings after looking at the plots. Spearman between the rank and the total: task_cognition 0.43, system 0.81, visualization 0.72. The largest differences are P097 (rank 1, total 6 of 12), P05 (rank 13, total 7) and P041 (rank 1, total 9). In task_cognition, 11 items have no IRT rank, among them P301, which has priority 5. In system, the ranks go up to 18 for 14 items, so they were probably assigned within a larger item set.

## How to run

From the repository root (Python ≥ 3.11; `openpyxl` only for the extraction):

```bash
python phase2-2-item-reduction/04_ranking/extract_ranking_criteria.py   # only if the spreadsheet changes
python phase2-2-item-reduction/04_ranking/build_ranking_table.py
python phase2-2-item-reduction/04_ranking/build-irt-ranking-table.py
```

## Data used in the ranking

**Baseline of the reliability rank.** In April 2026, α if dropped was computed within the factors of the 65-item EFA solution (25/18/22 items), not within the 49 items that started the phase. Recomputed within the 49 items (collapsed data), the top 5 by reliability is the same in every factor, so the reduced models do not change; 4 to 12 lower ranks per factor change. With the uncollapsed data, the System top 5 changes (P024 in, P074 out). The table keeps the April ranks, which the decisions were based on.


The ranks are the ones the decisions were based on (April 2026):

- **α if dropped** was computed on the **uncollapsed** data (`data/raw/ratings-stimulus_original.csv`). It is reproduced exactly, with a maximum difference of 5·10⁻¹¹.
- **Loadings** come from the EFA on the collapsed data.
- **No criterion depends on the tool labels**, so the label correction does not affect this step.

With the collapsed data, which is used in steps 01–03, α if dropped changes by up to 0.002, and some reliability ranks change by 1–3 positions. **No item enters or leaves the top 5 by reliability**: in task_cognition, P027 and P072 swap ranks 2 and 3; in visualization, P045A and P206 swap ranks 3 and 4. The other changes are below rank 5.
