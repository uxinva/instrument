# Runs 05_combinatorial.Rmd for every threshold and arrangement of the combinatorial search,
# with no limit on the number of models (max_models = 0), so every run is exhaustive.
#
# Settings are those of the May 2026 runs: single-group CFA (all tools pooled), MLR, FIML,
# uncollapsed ratings, fit rule (CFI or TLI >= 0.95) and (SRMR <= 0.08 or RMSEA <= 0.06).
#
# A run whose output folder already has passing_reliability_cfa_results.csv is skipped, so the
# script can be stopped and started again. Delete a run folder to run it again.
# Threshold 0.80 is not run: no item subset of some scale reaches it, so no model can be formed
# (build_runs_table.py derives that row). The search stops at 0.72 (decision of 2026-10-21): it is the
# highest threshold at which subsets with the cognitive items P062 or P064 reach approved models.
# The May runs at 0.70 and 0.71 (cut at 1,000 models) are not repeated.
#
# Run from the repository root (about 1.5 hours in total; the 0.72 run alone takes about 50 minutes):
#   source("phase2-2-item-reduction/05_combinatorial/run-all-thresholds.R")
#
# Afterwards:
#   python phase2-2-item-reduction/05_combinatorial/build_runs_table.py

library(here)

step <- here("phase2-2-item-reduction", "05_combinatorial")
rmd  <- file.path(step, "05_combinatorial.Rmd")
log_file <- file.path(step, "output", "run-all-thresholds-log.csv")

runs <- rbind(
  data.frame(arrangement = "6-3-3", threshold = c(0.79, 0.78, 0.77, 0.76, 0.75, 0.74, 0.73, 0.72)),
  data.frame(arrangement = "6-4-3", threshold = c(0.79, 0.78))
)

for (i in seq_len(nrow(runs))) {
  arr <- runs$arrangement[i]
  thr <- runs$threshold[i]
  run_name <- sprintf("rel%03d_%s_singlegroup_uncollapsed", round(thr * 100), arr)
  out_dir  <- file.path(step, "output", run_name)
  if (file.exists(file.path(out_dir, "passing_reliability_cfa_results.csv"))) {
    message("Skipping ", run_name, " (already done)")
    next
  }
  message("Running ", run_name, " ...")
  t0 <- Sys.time()
  ok <- tryCatch({
    rmarkdown::render(
      rmd,
      params = list(
        combination_file = sprintf("phase2-2-item-reduction/05_combinatorial/input/combinations_%s.csv", arr),
        run_name = run_name,
        reliability_threshold = thr,
        max_models = 0
      ),
      output_file = paste0(run_name, ".html"),
      output_dir = out_dir,
      envir = new.env(),
      quiet = TRUE
    )
    TRUE
  }, error = function(e) {
    message("  FAILED: ", conditionMessage(e))
    FALSE
  })
  minutes <- round(as.numeric(difftime(Sys.time(), t0, units = "mins")), 1)
  message("  ", if (ok) "done" else "failed", " in ", minutes, " min")
  write.table(
    data.frame(run_name = run_name, ok = ok, minutes = minutes, finished = format(Sys.time())),
    log_file, sep = ",", row.names = FALSE,
    col.names = !file.exists(log_file), append = file.exists(log_file)
  )
}

message("All runs finished. Now run: python phase2-2-item-reduction/05_combinatorial/build_runs_table.py")
