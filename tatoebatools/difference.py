import csv
import logging

import pandas as pd

from .utils import count_csv_columns

logger = logging.getLogger(__name__)


def compare_csv(
    csv_left, csv_right, delimiter, quoting=csv.QUOTE_NONE, index_col_keys=None
):
    """Get the differences between two CSV files"""
    left = _get_csv_dataframe(csv_left, delimiter=delimiter, quoting=quoting)
    right = _get_csv_dataframe(csv_right, delimiter=delimiter, quoting=quoting)

    if left is None or right is None:
        return {}
    else:
        return _compare_dataframes(left, right, index_col_keys)


def _get_csv_dataframe(csv_path, delimiter, quoting, header=False):
    """Load CSV file into a dataframe"""
    if not csv_path.is_file():
        return
    if header:
        return pd.read_csv(csv_path, header=0, sep=delimiter, quoting=quoting)
    else:
        nb_cols = count_csv_columns(csv_path, delimiter)
        col_names = [f"col_{i}" for i in range(nb_cols)]
        return pd.read_csv(
            csv_path, names=col_names, sep=delimiter, quoting=quoting
        )


def _compare_dataframes(left, right, index_col_keys):
    """Get the differences between two dataframes"""
    assert len(left.columns) == len(right.columns)

    merger = pd.merge(left, right, how="outer", indicator=True)
    right_only = merger.loc[merger["_merge"] == "right_only"]
    left_only = merger.loc[merger["_merge"] == "left_only"]

    diffs = {}
    if index_col_keys is None:
        diffs["added"] = right_only.drop(labels="_merge", axis=1)
        diffs["removed"] = left_only.drop(labels="_merge", axis=1)
    else:
        col_keys = merger.columns[index_col_keys]
        keys_right_only = right_only[col_keys].to_list()
        keys_left_only = left_only[col_keys].to_list()
        keys_modified = set(keys_right_only) & set(keys_left_only)

        added = right_only.loc[~right_only[col_keys].isin(keys_modified)]
        removed = left_only.loc[~left_only[col_keys].isin(keys_modified)]
        modified = right_only.loc[right_only[col_keys].isin(keys_modified)]

        diffs["added"] = added.drop(labels="_merge", axis=1)
        diffs["removed"] = removed.drop(labels="_merge", axis=1)
        diffs["modified"] = modified.drop(labels="_merge", axis=1)

    return diffs
