"""Deserialize parquet files in example_output/ by exploding the 'values' column.

This script reads the first parquet file found in `example_output/`, which is expected
to contain a column named `values` where each row is a list of dict-like objects
or serialized JSON. It normalizes those into one row per nested value and writes a
new parquet file `example_output/flattened.parquet` and prints the first 20 rows.

Usage: run inside the project's .venv (activation shown in README or run via the
venv's python executable).
"""
from __future__ import annotations

import json
import numpy as np
from pathlib import Path
import sys
from datetime import datetime

import pandas as pd


def find_parquet_file(output_dir: Path) -> Path | None:
    files = sorted(output_dir.glob("*.parquet"))
    return files[0] if files else None


def expand_values_column(df: pd.DataFrame, values_col: str = "values") -> pd.DataFrame:
    """Explode the `values` column so that each element of the list becomes its own row.

    The function handles cases where the `values` column contains:
    - actual Python lists of dicts
    - JSON strings representing lists
    - null/NaN
    It preserves other columns by repeating them for each exploded item.
    """
    if values_col not in df.columns:
        raise KeyError(f"Column '{values_col}' not found in DataFrame")

    # Parse JSON strings if necessary
    def parse_cell(cell):
        # None or NaN
        if cell is None:
            return []
        if isinstance(cell, float) and np.isnan(cell):
            return []

        # pandas Series or numpy arrays -> convert to list
        if isinstance(cell, (pd.Series, np.ndarray)):
            try:
                return list(cell)
            except Exception:
                return []

        # lists/tuples
        if isinstance(cell, (list, tuple)):
            return list(cell)

        # dicts
        if isinstance(cell, dict):
            return [cell]

        # strings: attempt JSON
        if isinstance(cell, str):
            try:
                parsed = json.loads(cell)
                return parsed if isinstance(parsed, list) else [parsed]
            except Exception:
                # Try light eval fallback for Python literal lists/dicts
                try:
                    parsed = eval(cell)
                    return parsed if isinstance(parsed, list) else [parsed]
                except Exception:
                    return []

        # fallback, unknown type
        return []

    parsed = df[values_col].apply(parse_cell)
    df = df.copy()
    df[values_col] = parsed
    # explode
    exploded = df.explode(values_col).reset_index(drop=True)

    # If exploded values are dict-like, expand into columns
    def expand_dict(cell):
        if pd.isna(cell):
            return {}
        if isinstance(cell, dict):
            return cell
        return {}

    expanded_cols = pd.json_normalize(exploded[values_col].apply(expand_dict))
    # prefix to avoid collisions
    expanded_cols = expanded_cols.add_prefix("")

    result = pd.concat([exploded.drop(columns=[values_col]).reset_index(drop=True), expanded_cols.reset_index(drop=True)], axis=1)
    return result


def main():
    root = Path(__file__).resolve().parent.parent
    output_dir = root / "example_output"
    pq = find_parquet_file(output_dir)
    if pq is None:
        print(f"No parquet files found in {output_dir}")
        sys.exit(1)

    print(f"Reading parquet: {pq}")
    df = pd.read_parquet(pq)
    print(f"Original rows: {len(df)}, columns: {list(df.columns)}")

    try:
        flat = expand_values_column(df, values_col="values")
    except KeyError:
        # try lowercase
        flat = expand_values_column(df, values_col="Values")

    out_path = output_dir / "flattened.parquet"
    flat.to_parquet(out_path, index=False)
    print(f"Wrote flattened parquet to {out_path}")

    # Also write CSV as requested by the user. Convert timezone-aware datetimes to ISO strings
    csv_out = output_dir / "flattened.csv"
    def tidy_for_csv(df: pd.DataFrame) -> pd.DataFrame:
        df2 = df.copy()
        for col in df2.columns:
            if pd.api.types.is_datetime64_any_dtype(df2[col].dtype):
                df2[col] = df2[col].apply(lambda v: v.isoformat() if pd.notna(v) else "")
        return df2

    flat_csv = tidy_for_csv(flat)
    flat_csv.to_csv(csv_out, index=False)
    print(f"Wrote flattened CSV to {csv_out}")
    # show first rows
    print("\nFirst 20 rows of flattened data:")
    with pd.option_context('display.max_rows', 20, 'display.max_columns', None):
        print(flat.head(20))


if __name__ == "__main__":
    main()
