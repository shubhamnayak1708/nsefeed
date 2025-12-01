"""
Utility functions for nsefeed library.

This module provides helper functions for:
- Date parsing and validation
- Symbol validation
- DataFrame operations
- Period to date range conversion
"""

from __future__ import annotations

import re
from datetime import datetime, date, timedelta
from typing import Tuple

import pandas as pd
from dateutil.parser import parse as dateutil_parse
from dateutil.relativedelta import relativedelta

from .constants import PERIOD_DAYS, DATE_FORMATS, PRIMARY_SERIES
from .exceptions import NSEInvalidDateError, NSEInvalidSymbolError


def parse_date(
    date_input: str | datetime | date | None,
    default: date | None = None,
) -> date | None:
    """
    Parse a date from various input formats.

    Supports:
    - ISO format: "2024-01-15"
    - Indian format: "15-01-2024", "15/01/2024"
    - NSE format: "15JAN2024", "15-Jan-2024"
    - datetime objects
    - date objects

    Args:
        date_input: Date in various formats
        default: Default value if input is None

    Returns:
        Parsed date object

    Raises:
        NSEInvalidDateError: If date cannot be parsed
    """
    if date_input is None:
        return default

    if isinstance(date_input, datetime):
        return date_input.date()

    if isinstance(date_input, date):
        return date_input

    if isinstance(date_input, str):
        date_str = date_input.strip()

        # Try common formats
        formats_to_try = [
            "%Y-%m-%d",      # ISO format
            "%d-%m-%Y",      # Indian format
            "%d/%m/%Y",      # Slash format
            "%d%b%Y",        # NSE bhav copy format
            "%d-%b-%Y",      # NSE format with dash
            "%Y%m%d",        # Compact ISO
        ]

        for fmt in formats_to_try:
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue

        # Fall back to dateutil parser
        try:
            return dateutil_parse(date_str, dayfirst=True).date()
        except (ValueError, TypeError):
            pass

    raise NSEInvalidDateError(
        f"Cannot parse date: '{date_input}'",
        details="Use formats like '2024-01-15', '15-01-2024', or '15JAN2024'",
    )


def format_date(d: date | datetime, format_name: str = "display") -> str:
    """
    Format a date according to NSE conventions.

    Args:
        d: Date to format
        format_name: Format type from DATE_FORMATS

    Returns:
        Formatted date string
    """
    if isinstance(d, datetime):
        d = d.date()

    fmt = DATE_FORMATS.get(format_name, DATE_FORMATS["display"])
    return d.strftime(fmt).upper()


def period_to_dates(period: str) -> tuple[date, date]:
    """
    Convert a period string to start and end dates.

    Args:
        period: Period string like "1mo", "3mo", "1y", "ytd", "max"

    Returns:
        Tuple of (start_date, end_date)

    Raises:
        NSEInvalidDateError: If period is invalid
    """
    period = period.lower()
    end_date = date.today()

    if period not in PERIOD_DAYS:
        raise NSEInvalidDateError(
            f"Invalid period: '{period}'",
            details=f"Valid periods: {', '.join(PERIOD_DAYS.keys())}",
        )

    days = PERIOD_DAYS[period]

    if days == -1:  # ytd
        start_date = date(end_date.year, 1, 1)
    elif days == -2:  # max
        start_date = date(2000, 1, 1)  # NSE data generally available from 2000
    else:
        start_date = end_date - timedelta(days=days)

    return start_date, end_date


def validate_date_range(
    start_date: date,
    end_date: date,
    allow_future: bool = False,
) -> tuple[date, date]:
    """
    Validate a date range.

    Args:
        start_date: Start date
        end_date: End date
        allow_future: Whether to allow future dates

    Returns:
        Validated (start_date, end_date) tuple

    Raises:
        NSEInvalidDateError: If date range is invalid
    """
    today = date.today()

    # Ensure start is before end
    if start_date > end_date:
        start_date, end_date = end_date, start_date

    # Check for future dates
    if not allow_future:
        if start_date > today:
            raise NSEInvalidDateError(
                "Start date cannot be in the future",
                details=f"Today is {today}, start_date is {start_date}",
            )
        if end_date > today:
            end_date = today

    # Check for dates too far in the past
    min_date = date(1995, 1, 1)  # NSE was established in 1992, data from ~1995
    if start_date < min_date:
        start_date = min_date

    return start_date, end_date


def validate_symbol(symbol: str) -> str:
    """
    Validate and normalize an NSE symbol.

    NSE symbols:
    - Are uppercase
    - Can contain letters, numbers, hyphens, and ampersands
    - Cannot be empty
    - Cannot contain spaces (except special cases)

    Args:
        symbol: Stock symbol to validate

    Returns:
        Normalized symbol (uppercase, trimmed)

    Raises:
        NSEInvalidSymbolError: If symbol is invalid
    """
    if not symbol:
        raise NSEInvalidSymbolError(symbol, "Symbol cannot be empty")

    # Normalize
    symbol = symbol.strip().upper()

    # Basic validation
    if len(symbol) > 20:
        raise NSEInvalidSymbolError(symbol, "Symbol too long")

    # Check for valid characters
    if not re.match(r"^[A-Z0-9&\-]+$", symbol):
        raise NSEInvalidSymbolError(
            symbol,
            "Symbol contains invalid characters",
        )

    return symbol


def is_trading_day(d: date) -> bool:
    """
    Check if a date is likely a trading day.

    This is a basic check that excludes weekends.
    For accurate holiday checking, use the NSE holiday calendar.

    Args:
        d: Date to check

    Returns:
        True if likely a trading day
    """
    # Saturday = 5, Sunday = 6
    return d.weekday() < 5


def get_previous_trading_day(d: date) -> date:
    """
    Get the previous likely trading day.

    Skips weekends. For accurate holiday handling, use NSE calendar.

    Args:
        d: Reference date

    Returns:
        Previous trading day
    """
    d = d - timedelta(days=1)
    while not is_trading_day(d):
        d = d - timedelta(days=1)
    return d


def get_trading_days_between(start: date, end: date) -> list[date]:
    """
    Get list of likely trading days between two dates.

    Excludes weekends. Does not account for holidays.

    Args:
        start: Start date (inclusive)
        end: End date (inclusive)

    Returns:
        List of trading days
    """
    days = []
    current = start
    while current <= end:
        if is_trading_day(current):
            days.append(current)
        current += timedelta(days=1)
    return days


def standardize_dataframe(
    df: pd.DataFrame,
    symbol: str | None = None,
) -> pd.DataFrame:
    """
    Standardize a DataFrame to nsefeed format.

    Ensures:
    - Columns are lowercase
    - Date column exists and is datetime
    - OHLCV columns are numeric
    - Index is set to date

    Args:
        df: Input DataFrame
        symbol: Optional symbol to add as column

    Returns:
        Standardized DataFrame
    """
    if df.empty:
        return df

    # Make a copy
    df = df.copy()

    # Lowercase columns
    df.columns = [c.lower() for c in df.columns]

    # Ensure date column
    date_cols = ["date", "timestamp", "trade_date", "traddt"]
    date_col = None
    for col in date_cols:
        if col in df.columns:
            date_col = col
            break

    if date_col:
        df["date"] = pd.to_datetime(df[date_col])
        if date_col != "date":
            df = df.drop(columns=[date_col])
    elif df.index.name in date_cols or isinstance(df.index, pd.DatetimeIndex):
        df = df.reset_index()
        df = df.rename(columns={df.columns[0]: "date"})
        df["date"] = pd.to_datetime(df["date"])

    # Ensure numeric columns
    numeric_cols = ["open", "high", "low", "close", "volume", "value", "trades"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Add symbol if provided
    if symbol:
        df["symbol"] = symbol.upper()

    # Set index
    if "date" in df.columns:
        df = df.set_index("date")
        df = df.sort_index()

    return df


def filter_by_series(df: pd.DataFrame, series: list[str] | None = None) -> pd.DataFrame:
    """
    Filter DataFrame by series type.

    Args:
        df: DataFrame with 'series' column
        series: List of series to include (default: PRIMARY_SERIES)

    Returns:
        Filtered DataFrame
    """
    if series is None:
        series = PRIMARY_SERIES

    if "series" not in df.columns:
        return df

    series = [s.upper() for s in series]
    return df[df["series"].str.upper().isin(series)]


def aggregate_to_weekly(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate daily OHLC data to weekly.

    Args:
        df: Daily OHLC DataFrame

    Returns:
        Weekly OHLC DataFrame
    """
    if df.empty:
        return df

    # Ensure index is DatetimeIndex
    if not isinstance(df.index, pd.DatetimeIndex):
        if "date" in df.columns:
            df = df.set_index("date")
            df.index = pd.to_datetime(df.index)

    # Resample to weekly (week ending Friday)
    weekly = df.resample("W-FRI").agg({
        "open": "first",
        "high": "max",
        "low": "min",
        "close": "last",
        "volume": "sum",
    }).dropna()

    # Add value and trades if present
    if "value" in df.columns:
        weekly["value"] = df["value"].resample("W-FRI").sum()
    if "trades" in df.columns:
        weekly["trades"] = df["trades"].resample("W-FRI").sum()

    return weekly


def aggregate_to_monthly(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate daily OHLC data to monthly.

    Args:
        df: Daily OHLC DataFrame

    Returns:
        Monthly OHLC DataFrame
    """
    if df.empty:
        return df

    # Ensure index is DatetimeIndex
    if not isinstance(df.index, pd.DatetimeIndex):
        if "date" in df.columns:
            df = df.set_index("date")
            df.index = pd.to_datetime(df.index)

    # Resample to monthly
    monthly = df.resample("ME").agg({
        "open": "first",
        "high": "max",
        "low": "min",
        "close": "last",
        "volume": "sum",
    }).dropna()

    # Add value and trades if present
    if "value" in df.columns:
        monthly["value"] = df["value"].resample("ME").sum()
    if "trades" in df.columns:
        monthly["trades"] = df["trades"].resample("ME").sum()

    return monthly
