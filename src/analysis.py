"""Core analysis helpers for retail and inventory metrics."""

from __future__ import annotations

import pandas as pd


def calculate_revenue(df: pd.DataFrame, qty_col: str, price_col: str, revenue_col: str = 'revenue') -> pd.DataFrame:
    """Create a revenue column from quantity and price."""
    cleaned = df.copy()
    cleaned[revenue_col] = pd.to_numeric(cleaned[qty_col], errors='coerce') * pd.to_numeric(cleaned[price_col], errors='coerce')
    return cleaned


def calculate_profit(df: pd.DataFrame, revenue_col: str, cost_col: str, profit_col: str = 'profit') -> pd.DataFrame:
    """Calculate profit as revenue minus cost."""
    cleaned = df.copy()
    cleaned[profit_col] = pd.to_numeric(cleaned[revenue_col], errors='coerce') - pd.to_numeric(cleaned[cost_col], errors='coerce')
    return cleaned


def calculate_profit_margin(df: pd.DataFrame, profit_col: str, revenue_col: str, margin_col: str = 'profit_margin') -> pd.DataFrame:
    """Calculate profit margin percentage."""
    cleaned = df.copy()
    revenue = pd.to_numeric(cleaned[revenue_col], errors='coerce')
    profit = pd.to_numeric(cleaned[profit_col], errors='coerce')
    with pd.option_context('mode.use_inf_as_na', True):
        cleaned[margin_col] = (profit / revenue) * 100
    return cleaned


def build_time_features(df: pd.DataFrame, date_col: str) -> pd.DataFrame:
    """Create common time-based features from a date column."""
    cleaned = df.copy()
    if date_col in cleaned.columns:
        cleaned['year'] = cleaned[date_col].dt.year
        cleaned['month'] = cleaned[date_col].dt.month
        cleaned['month_name'] = cleaned[date_col].dt.strftime('%b')
        cleaned['year_month'] = cleaned[date_col].dt.to_period('M').astype(str)
        cleaned['quarter'] = cleaned[date_col].dt.quarter
        cleaned['day_of_week'] = cleaned[date_col].dt.day_name()
    return cleaned


def safe_divide(numerator: float, denominator: float) -> float:
    """Safely divide and return 0 when the denominator is zero or missing."""
    if pd.isna(denominator) or denominator == 0:
        return 0.0
    return numerator / denominator
