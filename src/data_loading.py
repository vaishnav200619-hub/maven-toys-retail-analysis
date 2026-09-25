"""Utilities for loading raw data files from the project workspace."""

from __future__ import annotations

from pathlib import Path
import pandas as pd


def list_data_files(data_dir: str | Path) -> list[Path]:
    """Return all supported data files under the given directory."""
    data_path = Path(data_dir)
    if not data_path.exists():
        raise FileNotFoundError(f"Data directory not found: {data_path}")

    supported_extensions = {".csv", ".xlsx", ".xls", ".parquet", ".db", ".sqlite"}
    files = []
    for file_path in sorted(data_path.rglob('*')):
        if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
            files.append(file_path)
    return files


def load_csv_file(file_path: str | Path) -> pd.DataFrame:
    """Load a CSV file and return a DataFrame."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"CSV file not found: {path}")
    return pd.read_csv(path)


def load_excel_file(file_path: str | Path, sheet_name: int | str = 0) -> pd.DataFrame:
    """Load an Excel file and return a DataFrame."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Excel file not found: {path}")
    return pd.read_excel(path, sheet_name=sheet_name)


def detect_file_type(file_path: str | Path) -> str:
    """Return the supported file type for the given file."""
    suffix = Path(file_path).suffix.lower()
    if suffix == '.csv':
        return 'csv'
    if suffix in {'.xlsx', '.xls'}:
        return 'excel'
    if suffix == '.parquet':
        return 'parquet'
    if suffix in {'.db', '.sqlite'}:
        return 'database'
    raise ValueError(f"Unsupported file type for: {file_path}")
