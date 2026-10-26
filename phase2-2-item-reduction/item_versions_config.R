# =============================================================================
# item_versions_config.R
# SINGLE SOURCE of the item lists for phase 2 item reduction.
# Used by:
#   01_reliability/01_reliability.Rmd
#   02_cfa/02_cfa.Rmd
# Change item lists ONLY here. Both notebooks read this file.
#
# Decisions (2026-10-15, 2026-10-18):
#   - Baseline of Versions A-D: the 49 screened items (screened_3_factors), not the 65 EFA items.
#   - Data: low-frequency COLLAPSED ratings-stimulus.csv in all analyses.
#   - Versions C and D: Model_1 uses P089; Models 2 and 3 use P022A.
#   - Version E: 4-factor model, only Model_1 (no Model_2 / Model_3).
# =============================================================================

# --- Full (non-reduced) structures ------------------------------------------
# full_3_factors: the 65 items of the 3-factor EFA solution (input of step 00 only).
full_3_factors <- list(
  task_cognition = c('P062','P064','P301','P057','P052','P029','P030','P060','P092','P083','P04A','P027',
                     'P208','P302','P062C','P025','P095','P209','P213','P4026B','P072','P102','P037','P041','P201'),
  system         = c('P088','P026','P214','P4026A','P074','P086','P054','P024','P204','P074A','P049','P084',
                     'P022','P207','P06','P096','P203','P031'),
  visualization  = c('P106','P05','P089','P068','P098','P105','P211','P097','P104','P305','P205','P012',
                     'P022A','P206','P067','P09','P212','P103','P097A','P014','P033','P045A')
)

# Items that started the item reduction phase (49): the 65 items above minus 11 items with
# cross-loadings > 0.32 and 5 items excluded for missing data. Made and checked by
# 00-efa-screening/screen-efa-items.py (ordered by loading). This is the baseline ("full")
# of Versions A-D in all steps.
screened_3_factors <- list(
  task_cognition = c('P062','P064','P301','P057','P052','P029','P030','P060','P083','P04A','P027','P208',
                    'P302','P062C','P025','P4026B','P072','P037','P041'),
  system         = c('P088','P026','P214','P4026A','P074','P086','P054','P024','P204','P074A','P084','P022',
                    'P096','P203'),
  visualization  = c('P106','P05','P089','P068','P098','P211','P097','P205','P012','P022A','P206','P067',
                    'P097A','P014','P033','P045A')
)

full_4_factors <- list(
  task_cognition = c('P062','P064','P057','P052','P301','P029','P302','P030','P083','P062C','P025','P04A',
                     'P092','P027','P060','P095','P4026B','P208','P213','P209','P037'),
  system         = c('P026','P088','P214','P4026A','P086','P054','P024','P074','P204','P084','P074A','P022',
                     'P049','P207','P096','P203'),
  visualization  = c('P089','P106','P05','P068','P097','P098','P211','P022A','P305','P105','P09','P067',
                     'P06','P206','P205','P104','P097A'),
  reliability    = c('P031','P033','P102','P072','P014','P103','P045A')
)

# --- Versions ----------------------------------------------------------------
# Model_1 = items with highest factor loadings
# Model_2 = items selected in IRT analysis
# Model_3 = items selected in model-definition analysis (mixed parameters)
versions <- list(

  Version_A = list(full = screened_3_factors, models = list(
    Model_1 = list(
      visualization  = c('P097','P012','P033','P106','P068','P022A','P045A','P098','P097A','P089','P067','P05','P211','P206','P205','P014'),
      task_cognition = c('P060','P301','P041','P4026B','P302','P062','P052','P072','P029','P027','P030','P208','P037','P025','P062C','P057','P04A','P083','P064'),
      system         = c('P214','P026','P086','P088','P4026A','P024','P074','P084','P096','P022','P074A','P054','P203','P204')),
    Model_2 = list(
      visualization  = c('P097','P022A','P045A','P068','P067'),
      task_cognition = c('P041','P060','P064','P062','P027'),
      system         = c('P214','P088','P024','P4026A','P026')),
    Model_3 = list(
      visualization  = c('P098','P089','P097','P106','P068'),
      task_cognition = c('P062','P064','P060','P027','P301'),
      system         = c('P214','P088','P024','P4026A','P026'))
  )),

  Version_B = list(full = screened_3_factors, models = list(
    Model_1 = list(
      visualization  = c('P106','P05','P089','P068','P098'),
      task_cognition = c('P062','P064','P301','P057','P052'),
      system         = c('P088','P026','P214','P4026A','P074')),
    Model_2 = list(
      visualization  = c('P097','P022A','P045A','P068','P067'),
      task_cognition = c('P041','P060','P064','P062','P072'),
      system         = c('P214','P088','P024','P4026A','P026')),
    Model_3 = list(
      visualization  = c('P098','P022A','P097','P106','P068'),
      task_cognition = c('P062','P064','P060','P027','P301'),
      system         = c('P214','P088','P024','P4026A','P026'))
  )),

  Version_B2 = list(full = screened_3_factors, models = list(
    Model_1 = list(
      visualization  = c('P106','P05','P089','P068','P098'),
      task_cognition = c('P062','P064','P301','P057','P052'),
      system         = c('P088','P026','P214','P4026A','P074')),
    Model_2 = list(
      visualization  = c('P097','P022A','P045A','P068','P067'),
      task_cognition = c('P041','P060','P064','P062','P072'),
      system         = c('P214','P088','P024','P4026A','P026')),
    Model_3 = list(
      visualization  = c('P098','P022A','P097','P106','P068'),
      task_cognition = c('P062','P064','P060','P072','P301'),
      system         = c('P214','P088','P024','P4026A','P026'))
  )),

  # Decision (2026-10-15): Model_1 of Versions C and D uses P089 (top factor loadings).
  # The 2026-04 run used P022A by mistake; P022A belongs only to Models 2 and 3.
  Version_C = list(full = screened_3_factors, models = list(
    Model_1 = list(
      visualization  = c('P106','P05','P089','P068'),
      task_cognition = c('P062','P064','P301','P057'),
      system         = c('P088','P026','P214','P4026A')),
    Model_2 = list(
      visualization  = c('P097','P022A','P045A','P068'),
      task_cognition = c('P041','P060','P064','P062'),
      system         = c('P214','P088','P024','P4026A')),
    Model_3 = list(
      visualization  = c('P098','P022A','P097','P106'),
      task_cognition = c('P062','P064','P060','P072'),
      system         = c('P214','P088','P024','P4026A'))
  )),

  Version_D = list(full = screened_3_factors, models = list(
    Model_1 = list(
      visualization  = c('P106','P05','P089'),
      task_cognition = c('P062','P064','P301'),
      system         = c('P088','P026','P214')),
    Model_2 = list(
      visualization  = c('P097','P022A','P045A'),
      task_cognition = c('P041','P060','P064'),
      system         = c('P214','P088','P024')),
    Model_3 = list(
      visualization  = c('P098','P022A','P097'),
      task_cognition = c('P062','P064','P060'),
      system         = c('P214','P088','P024'))
  )),

  # Version E: different 4-factor model (full = full_4_factors). It has no Model_2 / Model_3 by design.
  Version_E = list(full = full_4_factors, models = list(
    Model_1 = list(
      visualization  = c('P089','P106','P05','P068','P097'),
      task_cognition = c('P062','P064','P057','P052','P301'),
      system         = c('P026','P088','P214','P4026A','P086'),
      reliability    = c('P031','P033','P102','P072','P014'))
  ))
)

# -----------------------------------------------------------------------------
# Paper table "Item-level reliability statistics (alpha if item dropped)"
# Built by 01_reliability/01_reliability.Rmd (outputs item_drop_table.csv / .tex).
#   item_table_structure : which full structure the table uses
#   All items of each factor are listed, sorted by alpha if item dropped, lowest first
#   (the items whose removal would lower the factor's reliability the most come first).
#   item_table$<factor>$bold : items to print in bold (none for now, decision 2026-10-16)
# -----------------------------------------------------------------------------
item_table_structure <- "screened_3_factors"

item_table <- list(
  task_cognition = list(bold = character(0)),
  system         = list(bold = character(0)),
  visualization  = list(bold = character(0))
)

item_table_factor_labels <- c(task_cognition = "Task_cognition",
                              system         = "System",
                              visualization  = "Visualization")

# -----------------------------------------------------------------------------
# IRT (step 03_irt): items analysed per factor.
# Default: the 49 items that started the item reduction phase (19 task_cognition,
# 14 system, 16 visualization), as in the April 2026 IRT runs (Reproduce7-IRT-graded.Rmd).
# -----------------------------------------------------------------------------
irt_item_sets <- screened_3_factors

irt_figure_titles <- c(task_cognition = "IRT Plots - Task_cognition Factor",
                       system         = "IRT Plots - System Factor",
                       visualization  = "IRT Plots - Visualization Factor")
