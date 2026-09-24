# Renders every R notebook of the validation phase, in order.
#
# Run from RStudio with instrument.Rproj open:
#   source("phase3-validation/render_all.R")
#
# Each report is written next to its notebook. Steps 03 and 04 are rendered
# twice, with different parameters. Step 02 is a Python notebook and is run
# separately (see 02_scale-correlations/README.md).

library(here)
library(rmarkdown)

phase <- here("phase3-validation")

render_step <- function(step, params = list(), suffix = "") {
  input <- file.path(phase, step, paste0(step, ".Rmd"))
  output_file <- paste0(step, suffix, ".html")
  message("\n==> ", step, suffix)
  render(input,
         params = params,
         output_file = output_file,
         envir = new.env())   # each run starts from a clean environment
}

render_step("00_collapse-categories")
render_step("01_gold-standard-reliability")

message("\n==> 02_scale-correlations is a Python notebook: run it in Jupyter.")

render_step("03_polychoric-correlations", list(scales = "uxvis"), "_uxvis-scales")
render_step("03_polychoric-correlations", list(scales = "all"),   "_all-scales")

render_step("04_number-of-factors", list(k_factors = 3), "_3-factors")
render_step("04_number-of-factors", list(k_factors = 4), "_4-factors")

render_step("05_cfa-multigroup")
render_step("06_alternative-structures")

message("\nDone. Commit the updated .html files together with the notebooks.")
