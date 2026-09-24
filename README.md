# Instrument: User Experience in Visual Analytics

This repository holds the data, scripts and analysis reports used to develop and validate an instrument for evaluating the **user experience (UX) of visual analytics systems**.

The rendered reports are published at **<https://uxinva.github.io/instrument/>**.

> **Status:** work in progress. The paper describing the instrument is being written, and further study phases will be added to this repository.

## Study phases

| Phase | Folder | Status |
|---|---|---|
| Phase 3: Scale validation | [`phase3-validation/`](phase3-validation/README.md) | Being documented |
| Other phases | *to be added* | Not yet documented |

### Analysis reports: phase 3 (scale validation)

| Step | Report |
|---|---|
| 00 Collapse categories | [report](https://uxinva.github.io/instrument/phase3-validation/00_collapse-categories/00_collapse-categories.html) |
| 01 Gold-standard reliability | [report](https://uxinva.github.io/instrument/phase3-validation/01_gold-standard-reliability/01_gold-standard-reliability.html) |
| 02 Scale correlations | [report](https://uxinva.github.io/instrument/phase3-validation/02_scale-correlations/02_scale-correlations.html) |
| 03 Polychoric correlations | [UXVis items](https://uxinva.github.io/instrument/phase3-validation/03_polychoric-correlations/03_polychoric-correlations_uxvis-scales.html) · [all items](https://uxinva.github.io/instrument/phase3-validation/03_polychoric-correlations/03_polychoric-correlations_all-scales.html) |
| 04 Number of factors | [3 factors](https://uxinva.github.io/instrument/phase3-validation/04_number-of-factors/04_number-of-factors_3-factors.html) · [4 factors](https://uxinva.github.io/instrument/phase3-validation/04_number-of-factors/04_number-of-factors_4-factors.html) |
| 05 Multi-group CFA | [report](https://uxinva.github.io/instrument/phase3-validation/05_cfa-multigroup/05_cfa-multigroup.html) |
| 06 Alternative structures | [report](https://uxinva.github.io/instrument/phase3-validation/06_alternative-structures/06_alternative-structures.html) |

What each step does is described in the [phase README](phase3-validation/README.md).

Each phase is self-contained. It has its own `data/` folder and a series of numbered analysis steps, each with a README, a notebook, its rendered HTML report and an `output/` folder.

## Repository structure

```
instrument/
├── README.md                  this file
├── instrument.Rproj           R project: open this in RStudio
├── _config.yml                GitHub Pages site settings
├── .github/workflows/         builds and publishes the site
└── phase3-validation/
    ├── README.md              overview of the phase and how to reproduce it
    ├── render_all.R           runs every step in order
    ├── data/                  raw data, data preparation, prepared data, item codebook
    └── NN_step-name/          one folder per analysis step (00–06)
        ├── README.md          what the step does, its inputs and outputs
        ├── NN_step-name.Rmd   notebook (step 02 is a Python notebook, .ipynb)
        ├── NN_step-name.html  rendered report
        └── output/            tables and figures produced by the step
```

## Requirements

- [R](https://cran.r-project.org) 4.5.2 and [RStudio Desktop](https://posit.co/download/rstudio-desktop/). The exact R package versions are recorded in `renv.lock` and installed with `renv::restore()`.
- [Python](https://www.python.org) (≥ 3.11) for the data preparation scripts and step 02 of the validation phase. The package versions are in `requirements.txt` (`pip install -r requirements.txt`).

More details are in the README of each phase.

## How to reproduce

1. Clone this repository.
2. Open `instrument.Rproj` in RStudio. All paths in the notebooks start from the repository root, so they work no matter where the repository is on your computer.
3. Follow the instructions in the README of the phase you want to reproduce, e.g. [`phase3-validation/README.md`](phase3-validation/README.md).

## Website

The site at <https://uxinva.github.io/instrument/> is rebuilt automatically on every push to `main` (see `.github/workflows/pages.yml`). It shows the README files as pages and links to the HTML reports that are committed next to each notebook, so no files have to be copied into a separate folder.

**After knitting a notebook, commit the updated `.html` together with the `.Rmd`**, so that the published report matches the code.

## License and citation

*To be defined* (suggested: CC BY 4.0 for the data and reports, MIT for the code). A `CITATION.cff` file and a DOI will be added when the paper is submitted.
