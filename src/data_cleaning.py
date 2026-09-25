"""Reusable data cleaning functions for the Maven Toys project."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

import pandas as pd


def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Standardize a DataFrame's column names to lowercase snake_case."""
    cleaned = df.copy()
    cleaned.columns = (
        cleaned.columns
        .astype(str)
        .str.strip()
        .str.lower()
        .str.replace(r"[^a-z0-9]+", "_", regex=True)
        .str.replace(r"_+", "_", regex=True)
        .str.strip("_")
    )
    return cleaned


def normalize_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize common missing value markers to pandas NA."""
    cleaned = df.copy()
    cleaned = cleaned.replace({"": pd.NA, " ": pd.NA, "NA": pd.NA, "N/A": pd.NA, "nan": pd.NA, "NaN": pd.NA})
    return cleaned


def remove_exact_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """Remove exact duplicate rows while preserving order."""
    original_rows = len(df)
    cleaned = df.drop_duplicates().copy()
    removed = original_rows - len(cleaned)
    return cleaned, removed


def convert_date_columns(df: pd.DataFrame, date_columns: Iterable[str]) -> pd.DataFrame:
    """Convert specified columns into datetime64[ns]."""
    cleaned = df.copy()
    for column in date_columns:
        if column in cleaned.columns:
            cleaned[column] = pd.to_datetime(cleaned[column], errors='coerce')
    return cleaned


def save_processed_data(df: pd.DataFrame, output_path: str | Path) -> None:
    """Save processed data to CSV output."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


def audit_cleaning(df_before: pd.DataFrame, df_after: pd.DataFrame, removed_rows: int) -> dict:
    """Return a summary of rows and missing values before and after cleaning."""
    return {
        "initial_row_count": len(df_before),
        "rows_removed": removed_rows,
        "rows_retained": len(df_after),
        "missing_before": int(df_before.isna().sum().sum()),
        "missing_after": int(df_after.isna().sum().sum()),
        "duplicates_before": int(df_before.duplicated().sum()),
        "duplicates_after": int(df_after.duplicated().sum()),
    }
