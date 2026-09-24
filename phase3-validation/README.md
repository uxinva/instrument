# Phase 3: Scale validation

This phase validates the UX in visual analytics scale (called **UXVis** here). The scale has 13 items grouped in three factors: **Cognitive value**, **Intuitiveness** and **Visualization**. Participants also answered two established questionnaires used as gold standards: the **System Usability Scale (SUS)** and the **short User Experience Questionnaire (UEQ-S)**.

The responses were collected with [LimeSurvey](https://www.limesurvey.org) in three surveys: students, user forums and Prolific.

## Steps

The steps must be run in this order, because each step reads files produced by the previous ones.

| Step | What it does | Reads | Report |
|---|---|---|---|
| [Data preparation](data/README.md) | Anonymises, cleans and merges the three LimeSurvey exports (Python scripts) | `data/raw/` | — |
| [00 Collapse categories](00_collapse-categories/README.md) | Merges rarely used answer options of the UXVis items into neighbouring ones | `data/prepared/` | [HTML](00_collapse-categories/00_collapse-categories.html) |
| [01 Gold-standard reliability](01_gold-standard-reliability/README.md) | Reliability (α, ω) of SUS and UEQ-S | `data/prepared/` | [HTML](01_gold-standard-reliability/01_gold-standard-reliability.html) |
| [02 Scale correlations](02_scale-correlations/README.md) | Pearson correlations between scale scores (UXVis factors, SUS, UEQ-S) | `data/prepared/` | [HTML](02_scale-correlations/02_scale-correlations.html) |
| [03 Polychoric correlations](03_polychoric-correlations/README.md) | Item-level polychoric correlations and clustering | step 00 | [UXVis items](03_polychoric-correlations/03_polychoric-correlations_uxvis-scales.html) · [All items](03_polychoric-correlations/03_polychoric-correlations_all-scales.html) |
| [04 Number of factors](04_number-of-factors/README.md) | Exploratory factor analysis and parallel analysis | step 03 | [3 factors](04_number-of-factors/04_number-of-factors_3-factors.html) · [4 factors](04_number-of-factors/04_number-of-factors_4-factors.html) |
| [05 Multi-group CFA](05_cfa-multigroup/README.md) | Reliability and confirmatory factor analysis, pooled and per system | step 00 | [HTML](05_cfa-multigroup/05_cfa-multigroup.html) |
| [06 Alternative structures](06_alternative-structures/README.md) | Compares 11 alternative factor structures (EFA and CFA) | step 00 | [HTML](06_alternative-structures/06_alternative-structures.html) |

## How to reproduce

The prepared data in `data/prepared/` is already in the repository. To rebuild it from the anonymised survey exports, run `python phase3-validation/data/prepare_data.py` (see [data preparation](data/README.md)). Then, for the analyses:

1. Install R 4.5.2, the version used for the published results (recorded in `renv.lock`).
2. Open `instrument.Rproj` (at the repository root) in RStudio. [renv](https://rstudio.github.io/renv/) starts automatically.
3. Install the exact package versions recorded in `renv.lock`:

   ```r
   renv::restore()
   ```

4. Run everything with:

   ```r
   source("phase3-validation/render_all.R")
   ```

   Or knit a single notebook in RStudio. Steps 03 and 04 are run twice with different settings, and `render_all.R` does both runs.
5. Step 02 is a Python notebook. Run it in Jupyter, then export the report with:

   ```bash
   jupyter nbconvert --to html phase3-validation/02_scale-correlations/02_scale-correlations.ipynb
   ```

### R packages

`here`, `rmarkdown`, `knitr`, `dplyr`, `tidyr`, `tibble`, `tidyverse`, `ggplot2`, `RColorBrewer`, `png`, `corrplot`, `dendextend`, `psych`, `GPArotation`, `polycor`, `lavaan`, `semTools`, `mice`, `mifa`, `misty`, `openxlsx`

The exact versions are in [`renv.lock`](../renv.lock), recorded from the environment in which the results were produced (R 4.5.2, Windows).

### Python packages

`pandas`, `numpy`, `scipy`, `matplotlib`, `seaborn`, `jupyter` (listed in `requirements.txt`)

## Reproducibility notes

The results were reproduced on a second computer (macOS on Apple Silicon, with the package versions in `renv.lock`), and they match the originals (Windows) with these exceptions:

- **Package versions matter.** An older `psych` version gives a different RMSR in step 04 and different parallel-analysis simulations in step 06. Use `renv::restore()` to get the recorded versions.
- **One core for simulations.** On macOS and Linux, `psych` runs some computations on several cores, which makes the parallel-analysis simulations change from run to run even with `set.seed()`. Steps 04–06 therefore set `options(mc.cores = 1)`.
- **Power BI, last decimals.** One polychoric correlation in the Power BI group differs in the 5th decimal between the two computers (0.88237 vs 0.88235). This carries over to one reliability value and some 2-factor Power BI loadings in step 06, in the 4th decimal. Rounded to 3 decimals, all values are identical.
- **Packages not used by the analyses.** `data.table`, `glmnet`, `pan` and `ucminf` were installed in newer versions than recorded, because the recorded ones could not be installed on macOS. They are indirect dependencies of `mifa`, which none of the analyses use.

## Stimuli

Participants evaluated the visual analytics system they use (the **stimulus**). The multi-group analyses (steps 05 and 06) use the five systems with enough responses: **Power BI**, **Tableau**, **JMP**, **Excel** and **Data Studio**.

## Item codes

The item codebook is in [`data/codebook/items.csv`](data/codebook/items.csv).

| Code | Short name | Factor |
|---|---|---|
| P064 | CogSysThinkDeep | Cognitive value |
| P027 | CogTaskComplete | Cognitive value |
| P060 | CogSysEnjoy | Cognitive value |
| P301 | CogSysUseful | Cognitive value |
| P026 | IntSysEasyStart | Intuitiveness |
| P4026A | IntAnalysisConfigure | Intuitiveness |
| P088 | IntSysSimpleUnderstand | Intuitiveness |
| P089 | VisSimpleUnderstand | Visualization |
| P022A | VisRemember | Visualization |
| P067 | VisTrialError | Visualization |
| P097 | VisSysRetrieveInfo | Visualization |
| P098 | VisAppropriate | Visualization |
| P106 | VisFaithful | Visualization |
