"""Phase 2.1, step 02: analysis of the EFA factor loadings.

Port of `Notebooks/05_Notebooks/05-EFA factor loading analysis.ipynb` (OSF supplemental folder, Phase 2 - Scale
Development). For every number of factors (1-6) it combines the principal-axis loadings of the six groups (five tools
and the whole sample, `Agg`) and, per group and factor:

- keeps the loadings above the threshold (0.32);
- counts cross-loadings (number of factors, besides the main one, on which an item loads above the threshold);
- assigns each item to the factor of its largest loading and ranks the items within each factor;
- gives each item a global order (factor 1 first, then factor 2, ...);
- across the six groups: in how many groups the item belongs to each factor, and its average rank there.

The functions `set_of_observation`, `cols_to_int` and the main loop are copied from the notebook; only the file
reading and writing changed.

Two modes:

- default: reads the loadings written by step 01 (`../01_efa/output/loadings/pa-<k>-factors-<group>.csv`) and keeps
  only item rows. This is the corrected analysis.
- `--legacy`: reads files with the layout of 2026-03-18 (`<group>/PA1 Stimuli <k> factors - <group>.csv`) and, like
  the notebook, keeps the rows of the variance table (SS loadings, Proportion Var, ...) as if they were items. Used
  only to check that the port reproduces the old outputs; see README.

Run from the repository root:
    python phase2-1-scale-development/02_efa-loadings/efa_loadings.py
    python phase2-1-scale-development/02_efa-loadings/efa_loadings.py --check
"""

import argparse
import os
import re
import sys
from pathlib import Path

import pandas as pd

STEP_DIR = Path(__file__).resolve().parent
PHASE_DIR = STEP_DIR.parent

# list of conditions (same order as the notebook)
conditions = ['Tableau', 'Qlik', 'Power BI', 'Gephi', 'JMP', 'Agg']
factors_numbers = ['1', '2', '3', '4', '5', '6']

# Factor loadings threshold
loading_threshold = 0.32

ITEM_CODE = re.compile(r'^P\d+[A-Z]?$')


def group_slug(g):
    return g.lower().replace(' ', '-')


def import_EFA_file(stimuli, factors, input_dir, legacy):
    """Reads one loadings file; columns are renamed '<factor> <stimuli>' and rows sorted by the first factor."""
    if legacy:
        full_path = os.path.join(input_dir, stimuli, f"PA1 Stimuli {factors} factors - {stimuli}.csv")
    else:
        full_path = os.path.join(input_dir, f"pa-{factors}-factors-{group_slug(stimuli)}.csv")
    this_df = pd.read_csv(full_path)
    if 'items' in this_df.columns:
        this_df = this_df.rename(columns={'items': 'item'}).set_index('item')
    elif "terms" in this_df.columns:
        this_df = this_df.rename(columns={'terms': 'item'}).set_index('item')
    if not legacy:
        # keep only the item rows: drop the separator and the variance table written below the loadings
        this_df = this_df[[bool(ITEM_CODE.match(str(i))) for i in this_df.index]]
        this_df = this_df.astype(float)
    # Including stimulus (Tableau, Qlik, etc) in column name
    for col in list(this_df):
        this_df = this_df.rename(columns={col: f'{col} {stimuli}'})
    this_df = this_df.sort_values(by=list(this_df)[0], axis=0)
    return this_df


# ---------------------------------------------------------------------------------------------------------------
# Copied from the notebook (cell "Utils"); comments as in the original.

def set_of_observation(this_df, condition='Agg', efa_method='PA', fa_str='1'):
    col_names = []  # we will store the col names for iterating through the ranking colummns later
    this_df_factors = {}
    for col in this_df.columns:  # we will iterate through each factor
        col_names.append(col)
        this_df.sort_values(by=col, axis=0, inplace=True, ascending=False)  # we sort the df
        this_factor = pd.DataFrame(this_df[this_df[col] > loading_threshold][col].reset_index().reset_index().set_index('item')).rename(columns={'index': f'factor rank in {col}'})  # We make a df for this factor, taking only values above the threshold

        this_df_factors.update({
            f'{col[2]}': this_factor  # the number is the third character of the col name
        })

    this_c_factor = pd.concat([df for df in this_df_factors.values()], axis=1)  # We concat all dfs for this stimulus

    if len(fa_str) == 1:
        fa_nb = int(fa_str)
    else:
        fa_nb = int(fa_str[0])

    # for analysis with more than 1 factor, we count crossloadings where an item loads above the threshold more than once, then we rewrite the ranks
    if fa_nb > 1:
        crossloadings_dict = {}

        for item, row in this_c_factor.iterrows():
            row_slice = row[[col for col in this_c_factor if 'rank' not in col]]
            crossloadings = len(row_slice.dropna()) - 1  # since the last operation we have NaN where an item was lower than threshold. Cross-loadings occurs when items are above threshold more than once
            crossloadings_dict.update({
                item: crossloadings
            })
            max_value = row_slice.max()
            columns_with_value = this_c_factor.columns[this_c_factor.loc[item].isin([max_value])]
            if len(columns_with_value) == 1:
                item_factor = columns_with_value[0]
                this_c_factor.at[item, f'factor rank in {item_factor}'] = 1  # True #we set the ranking to True (we changed to 1) in order to recompile it afterwards
                for col in [col for col in this_c_factor if 'rank' in col and item_factor not in col]:
                    this_c_factor.at[item, col] = pd.NA
            elif len(columns_with_value) > 1:
                print(f"It's a tie between factors {columns_with_value} for item {item}")
            elif len(columns_with_value) == 0:
                print(f'Something is wrong with item {item}')

        this_c_factor.insert(0,
                             f'Cross-loadings in {condition}',
                             this_c_factor.index.map(crossloadings_dict))  # we add crossloadings in the df as a new column

    # we calculate the rank for each factor
    cols_Factors = []
    for n in range(1, fa_nb + 1, 1):
        cols_Factors.append(f'{efa_method}{str(n)} {condition}')  # we generate all the list of all "FactorN condition" column names
    for col_prefix in cols_Factors:
        fa_col = f'{col_prefix}'
        rank_col = f'factor rank in {col_prefix}'

        # Filter rows where the factor rank column is True
        factor_rows = this_c_factor[this_c_factor[rank_col] == True]
        # Rank the values in the Factor column and fill the factor rank column for selected rows
        this_c_factor.loc[factor_rows.index, rank_col] = factor_rows[fa_col].rank(ascending=False, method='min')

    # We create a new column for global ranks
    global_rank_col = f'Order in {condition}'
    this_c_factor[global_rank_col] = pd.NA
    global_rank_counter = 1  # Initialize a counter for global ranks

    # Iterate over the factor rank columns and update the global ranks
    for col_prefix in cols_Factors:  # Add more prefixes as needed
        rank_col = f'factor rank in {col_prefix}'

        # Update the global ranks for each factor rank column
        this_c_factor[global_rank_col] = this_c_factor.apply(lambda row: global_rank_counter + row[rank_col] - 1
                                                             if not pd.isnull(row[rank_col]) else row[global_rank_col],
                                                             axis=1)

        # Increment the counter for the next factor rank column
        global_rank_counter += len(this_c_factor) - this_c_factor[rank_col].isnull().sum()

    return (condition, this_c_factor)


# just to make certain columns look prettier (otherwise int were converted to float because of the presence of NaNs)
def cols_to_int(df, list_of_cols, nan_value='NaN'):
    for col in list_of_cols:
        df[col] = df[col].astype('Int64').astype('object').fillna(nan_value)  # Int64 supports Na, then we convert to object and we can replace them
    return df


# ---------------------------------------------------------------------------------------------------------------
# Copied from the notebook (cell "Individual stimulus EFA").

def all_stimuli(EFA_df_dict):
    fa_loadings_dict = {}
    for fa in factors_numbers:
        this_fa_factor = {}
        fa_nb = int(fa)

        for c in EFA_df_dict[fa].keys():  # for each EFA conducted (= condition = stimulus) with this number of factors
            this_df = EFA_df_dict[fa][c]  # we take the df
            processed_c_df = set_of_observation(this_df, condition=c, fa_str=fa)  # see in utils
            this_fa_factor.update({
                processed_c_df[0]: processed_c_df[1]
            })

        # let's concat the dfs
        this_factor_loadings = pd.concat([df for df in this_fa_factor.values()], axis=1)

        crossloadings_cols = [col for col in this_factor_loadings if 'Cross' in col]
        this_factor_loadings = cols_to_int(this_factor_loadings, crossloadings_cols, nan_value='Never above threshold')
        order_cols = [col for col in this_factor_loadings if 'Order' in col]
        this_factor_loadings = cols_to_int(this_factor_loadings, order_cols, nan_value='Missing')

        # organize df columns by alphabetical order = order of factors
        all_cols = sorted(list(this_factor_loadings))
        this_factor_loadings = this_factor_loadings[all_cols]

        # create a col with averages of ranks when items are in this factor for all conditions
        average_cols = []
        # create a col with count of presence across conditions
        presence_count_cols = []

        rank_cols = [col for col in all_cols if 'rank' in col]

        for PA_nb in range(1, fa_nb + 1, 1):  # we iterate through the PA numbers

            this_PA_rank_cols = [col for col in rank_cols if f'PA{PA_nb}' in col]  # ranks for this PA nb only

            # information will be stored in dict and then trasnformed into columns
            this_PA_rank_averages = {}
            this_PA_presence_count = {}

            for item, row in this_factor_loadings.iterrows():
                relevant_row_slice = row[this_PA_rank_cols]
                if relevant_row_slice.isna().any():  # if there is any condition where this item isn't part of the factor > threshold
                    average_rank = ''  # then no rank
                else:  # calculate item's average rank  and store it
                    average_rank = relevant_row_slice.mean()
                this_PA_rank_averages.update({
                    item: average_rank
                })
                slice_not_na = relevant_row_slice.dropna()
                this_PA_presence_count.update({
                    item: len(slice_not_na)
                })

            # create the new cols from the dict
            av_col_name = f'average rank in PA{PA_nb}'
            count_col_name = f'presence count PA{PA_nb}'
            average_cols.append(av_col_name)
            this_factor_loadings[av_col_name] = this_factor_loadings.index.map(this_PA_rank_averages)
            presence_count_cols.append(count_col_name)
            this_factor_loadings[count_col_name] = this_factor_loadings.index.map(this_PA_presence_count)

        # reorganize the order of columns
        FL_cols = [col for col in all_cols if col not in rank_cols]
        order_cols = [col for col in all_cols if 'order' in col]
        new_cols = presence_count_cols + order_cols + FL_cols + average_cols + rank_cols
        this_factor_loadings = this_factor_loadings[new_cols]

        # add that df to the dict of dfs
        fa_loadings_dict.update({
            fa: this_factor_loadings
        })
    return fa_loadings_dict


# ---------------------------------------------------------------------------------------------------------------

def run(input_dir, output_dir, legacy):
    EFA_df_dict = {n: {c: import_EFA_file(c, n, input_dir, legacy) for c in conditions} for n in factors_numbers}
    fa_loadings_dict = all_stimuli(EFA_df_dict)
    output_dir.mkdir(parents=True, exist_ok=True)
    for fa_nb, df in fa_loadings_dict.items():
        df.to_csv(output_dir / f'all-groups-loadings-{fa_nb}-factors.csv', index_label='item')
    # whole sample alone (notebook cell "Analysis for aggregated data EFA results")
    agg_dir = output_dir / 'agg'
    agg_dir.mkdir(exist_ok=True)
    for n in factors_numbers:
        df2 = set_of_observation(import_EFA_file('Agg', n, input_dir, legacy), condition='Agg', fa_str=n)[1]
        df2.to_csv(agg_dir / f'agg-loadings-{n}-factors.csv', index_label='item')
    return fa_loadings_dict


def compare_frames(new, old, tol=1e-9):
    """Same rows in the same order, same columns, numbers within tol, other cells identical."""
    problems = []
    if list(new.index) != list(old.index):
        problems.append('rows differ or are in another order')
    if list(new.columns) != list(old.columns):
        problems.append(f'columns differ: {set(new.columns) ^ set(old.columns)}')
    if problems:
        return problems, None
    max_diff = 0.0
    for col in old.columns:
        a = pd.to_numeric(new[col], errors='coerce')
        b = pd.to_numeric(old[col], errors='coerce')
        num = a.notna() & b.notna()
        if num.any():
            max_diff = max(max_diff, float((a[num] - b[num]).abs().max()))
        other = ~num
        sa = [('' if pd.isna(v) else str(v)) for v in new[col][other]]
        sb = [('' if pd.isna(v) else str(v)) for v in old[col][other]]
        if sa != sb:
            problems.append(f'non-numeric cells differ in column {col}')
    if max_diff > tol:
        problems.append(f'largest numeric difference {max_diff:.2e}')
    return problems, max_diff


def check():
    """Runs the legacy mode on the 2026-03-18 loadings and compares with the old outputs of the notebook."""
    ref_in = PHASE_DIR / '01_efa' / 'input' / 'reference-2026-03-18'  # the same loadings step 01 is checked against
    ref_out = STEP_DIR / 'input' / 'reference-2026-03-23'
    tmp_out = STEP_DIR / 'output' / 'check-legacy'
    run(ref_in, tmp_out, legacy=True)
    ok = True
    lines = []
    for n in factors_numbers:
        new = pd.read_csv(tmp_out / f'all-groups-loadings-{n}-factors.csv', index_col='item', keep_default_na=False, na_values=[''])
        old = pd.read_csv(ref_out / f'All_stimuli_EFA_loadings-{n}_factors.csv', index_col='item', keep_default_na=False, na_values=[''])
        problems, max_diff = compare_frames(new, old)
        ok &= not problems
        status = 'identical' if not problems else '; '.join(problems)
        lines.append(f'{n} factors: {len(old)} rows x {old.shape[1]} columns, largest numeric difference '
                     f'{(max_diff or 0):.1e} -> {status}')
    print('\n'.join(lines))
    print('REPRODUCED: the port gives the outputs of the notebook of 2026-03-23.' if ok else 'DIFFERENT')
    return ok


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--check', action='store_true', help='reproduce the old outputs (legacy mode) and compare')
    args = parser.parse_args()
    if args.check:
        sys.exit(0 if check() else 1)
    run(PHASE_DIR / '01_efa' / 'output' / 'loadings', STEP_DIR / 'output', legacy=False)
    print(f'Written to {STEP_DIR / "output"}')


if __name__ == '__main__':
    main()
