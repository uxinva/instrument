# Renders every R notebook of phase 2.2 (item reduction), in order.
#
# Run from RStudio with instrument.Rproj open:
#   source("phase2-2-item-reduction/render_all.R")
#
# Each report is written next to its notebook; tables go to the step's output/ folder.

library(here)
library(rmarkdown)

phase <- here("phase2-2-item-reduction")

render_step <- function(step, params = list()) {
  input <- file.path(phase, step, paste0(step, ".Rmd"))
  message("\n==> ", step)
  render(input, params = params, envir = new.env())   # clean environment for each step
}

render_step("01_reliability")
render_step("02_cfa")
render_step("03_irt")

message("\nDone. Commit the updated .html files and output/ folders together with the notebooks.")
