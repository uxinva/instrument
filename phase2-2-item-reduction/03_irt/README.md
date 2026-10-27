# 03 IRT

**Notebook:** [`03_irt.Rmd`](03_irt.Rmd) · **Report:** [`03_irt.html`](https://uxinva.github.io/instrument/phase2-2-item-reduction/03_irt/03_irt.html)

## What it does

For each factor (`task_cognition`, `system`, `visualization`), the notebook fits a **unidimensional graded response model** with `mirt` (`itemtype = "graded"`), on the data of all five tools together. It then:

1. **Global fit:** computes M2\* (or C2 when M2\* cannot be computed), with RMSEA, SRMSR, TLI and CFI.
2. **Check against classical test theory:** correlates the IRT scores with the scores of a one-factor CFA on the same items.
3. **Item parameters:** exports them, with the discrimination *a* and the thresholds *b1 … bk*.
4. **Figures:**
   - a **trace plot** per item, with the probability of each answer option along the latent trait θ;
   - **one figure per factor** with the trace plots of all its items in 5 columns (the paper figures "IRT Plots – … Factor");
   - **item information curves**.

**Colours.** Each answer option has a fixed colour in every panel: −3 blue, −2 orange, −1 green, 0 red, +1 purple, +2 olive, +3 pink. An item without a given option, because it was collapsed, simply has no line of that colour.

**Item sets.** They come from [`../item_versions_config.R`](../item_versions_config.R) (`irt_item_sets`). The default is the 49 items that started the item reduction phase (`screened_3_factors`: 19 task_cognition, 14 system and 16 visualization items), as in the April 2026 figures.

**Parameters** (YAML header):

| Parameter | Meaning |
|---|---|
| `data_file` | Input data. Default (since 2026-10-21): the **uncollapsed** data, `../data/raw/ratings-stimulus_original.csv`, as in the April 2026 figures on which the IRT rubric scores (`04_ranking`, Table `tab:IRT-ranking`) were given. Steps 01 and 02 use the collapsed data |
| `listwise` | `TRUE` (default): participants with a missing answer in the factor's items are dropped, as in the old notebook |
| `theta_lim` | The θ axis goes from −`theta_lim` to +`theta_lim` (default 3) |

## Difference from the old figures

The April 2026 figures (`Gdrive_files/Item Reduction/IRT/260412-IRT-ThirdRun-Colored/All Stimulus-<factor>-Items_traces_colored.pdf`) were made by `phase2-2-itemreduction/Notebooks/Reproduce7_Notebooks/Reproduce7-IRT-graded.Rmd`. They differ from this step in three ways:

- **Data.** They used the **uncollapsed** data (`phase2-2-itemreduction/Data/Reproduce7_Data/ratings-stimulus_<factor>.csv`). With the collapsed data, the rare options (mostly −3 and −2) are merged, so some items have fewer curves. This is why the default is now the uncollapsed data: the figures match the ones that were scored. For a collapsed run, set `data_file: "phase2-2-item-reduction/data/prepared/ratings-stimulus_collapsed.csv"`.
- **Runs.** The old notebook was run once per factor, by editing the `read.csv()` line and `this_factor_name` by hand. This step runs all three factors at once.
- **Colours.** The old colour map was keyed by the values 1–7, while the answers are coded −3…+3, so probably only some options got their intended colour. Here the colours are keyed by the actual answer value.

## Inputs

| File | Content |
|---|---|
| `../data/raw/ratings-stimulus_original.csv` | Uncollapsed ratings (default; see [data](../data/README.md)) |
| `../data/prepared/ratings-stimulus_collapsed.csv` | Collapsed ratings (optional) |
| `../item_versions_config.R` | `irt_item_sets` (items per factor) and `irt_figure_titles` |

## Outputs (`output/`)

| File | Content |
|---|---|
| `irt_traces_<factor>.pdf`, `.png` | **Paper figure**: trace plots of all items of the factor, 5 per row (PNG at 300 dpi) |
| `irt_information_<factor>.pdf` | Item information curves of the factor |
| `items/ItemIRT-<item>-trace.pdf` | Trace plot of one item |
| `item_parameters_<factor>.csv` | *a* and *b1 … bk* for each item of the factor |
| `item_parameters_all.csv` | The same for all factors in one table |
| `irt_fit_by_factor.csv` | Per factor: number of items, participants used, M2\*/C2, df, p, RMSEA, SRMSR, TLI, CFI, and the CTT–IRT score correlation |
| `run_info.txt`, `sessionInfo.txt` | Data file, MD5, run time, R and package versions |
