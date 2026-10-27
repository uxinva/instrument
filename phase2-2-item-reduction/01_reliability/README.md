# 01 Reliability

**Notebook:** [`01_reliability.Rmd`](01_reliability.Rmd) · **Report:** [`01_reliability.html`](https://uxinva.github.io/instrument/phase2-2-item-reduction/01_reliability/01_reliability.html)

## What it does

For every version (A, B, B2, C, D, E), every model (`full_data`, `Model_1`, `Model_2`, `Model_3`) and every factor, the notebook computes:

- **Cronbach's α** (`raw_alpha`, `std.alpha`, from `psych::alpha`). This is the value reported in the paper table.
- **McDonald's ω total** (`omega_tot`), from a 1-factor `psych::omega` on the polychoric correlation matrix of that factor's items.
- **α if an item is dropped**, for every item.
- **The same α and ω for each stimulus separately** (Tableau, Qlik, Power BI, Gephi, JMP).

Item lists come from [`../item_versions_config.R`](../item_versions_config.R). The same file defines which items appear in the paper table (`item_table`); the item wording comes from [`../data/codebook/items.csv`](../data/codebook/items.csv).

**Parameters** (in the YAML header):
- `per_stimulus`: per-tool reliability, default `TRUE`;
- `compute_omega`: compute ω, default `TRUE`; set it to `FALSE` for a faster run.

**Differences from the old notebook** (`phase2-2-itemreduction/02-reliability/Reproduce2-reliability.Rmd`):
- **One run covers all versions.** There is no commenting or uncommenting of item lists.
- **Per-stimulus ω is now computed on that stimulus' data.** The old notebook reused the polychoric matrix of the whole sample, so its per-stimulus ω values were not really per stimulus.
- **Missing items stop the run.** The notebook checks that every configured item exists in the data.

## Inputs

| File | Content |
|---|---|
| `../data/prepared/ratings-stimulus_collapsed.csv` | Collapsed ratings (see [data](../data/README.md)) |
| `../item_versions_config.R` | Item lists for all versions and models |

## Outputs (`output/`)

| File | Content |
|---|---|
| `reliability_summary_wide.csv` | **α for the paper table**: rows = factor × model, columns = version (same layout as *Results Summary*) |
| `omega_summary_wide.csv` | The same layout for ω total |
| `reliability_all_versions_long.csv` | Everything in one long table: version, model, factor, stimulus (`All` or tool), items, α, standardised α, G6, average r, ω, N, number of items |
| `<Version>/<factor>-<model>-reliability.csv` | `psych::alpha` totals + `omega_tot`, `n_obs`, `n_items` |
| `<Version>/<factor>-<model>-items-drop-detailed.csv` | α if each item is dropped |
| `<Version>/<factor>-<model>-<stimulus>-reliability.csv` | The same totals for one stimulus |
| `item_drop_table.csv` | **Paper table** "α if item dropped": every item of the 49 that started the phase (`screened_3_factors`), per factor sorted by α if dropped (lowest first, `rank`), with its wording, the factor's baseline α, its position in the full list and its role (`bold` if listed in `item_table`, otherwise `listed`; no item is in bold for now) |
| `item_drop_table.tex` | The same table as a LaTeX `table` environment, ready for the paper: all items, sorted per factor from the lowest α if dropped (the items whose removal lowers reliability the most) to the highest; items listed in `item_table` would be in bold (none for now). |
| `reliability-summary-table.tex` | **Paper table** (LaTeX, label `tab:reliability-summary`): α by factor × model and version, in the layout of *Results Summary* (Table 9) |
| `versions_config.rds` | The item lists used in this run |
| `run_info.txt` | Data file path, its MD5 and the run time |
| `sessionInfo.txt` | R and package versions |

## Check

[`checks/expected_alpha_collapsed.csv`](checks/expected_alpha_collapsed.csv) has the α values computed independently in Python on the same data and item lists. It also has the value in the old *Results Summary* and the difference. Since 2026-10-18 the `full_data` rows use the 49 screened items; their old value is the old Version A Model_1 value (the same 49 items), because the old `full_data` rows used the 65 EFA items. `raw_alpha` in `reliability_summary_wide.csv` must match the `raw_alpha` column of that file.
