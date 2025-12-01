"""
Unit tests for utility functions.
"""

import pytest
from datetime import date, datetime, timedelta
import pandas as pd

from nsefeed.utils import (
    parse_date,
    format_date,
    period_to_dates,
    validate_date_range,
    validate_symbol,
    is_trading_day,
    get_previous_trading_day,
    get_trading_days_between,
    standardize_dataframe,
    filter_by_series,
    aggregate_to_weekly,
    aggregate_to_monthly,
)
from nsefeed.exceptions import (
    NSEInvalidDateError,
    NSEInvalidSymbolError,
)


class TestParseDate:
    """Tests for parse_date function."""

    def test_iso_format(self):
        """Test ISO date format."""
        assert parse_date("2024-01-15") == date(2024, 1, 15)

    def test_indian_format_dash(self):
        """Test Indian date format with dashes."""
        assert parse_date("15-01-2024") == date(2024, 1, 15)

    def test_indian_format_slash(self):
        """Test Indian date format with slashes."""
        assert parse_date("15/01/2024") == date(2024, 1, 15)

    def test_nse_format(self):
        """Test NSE bhav copy date format."""
        assert parse_date("15JAN2024") == date(2024, 1, 15)

    def test_nse_format_lowercase(self):
        """Test NSE format with lowercase."""
        assert parse_date("15jan2024") == date(2024, 1, 15)

    def test_datetime_input(self):
        """Test datetime object input."""
        dt = datetime(2024, 1, 15, 10, 30)
        assert parse_date(dt) == date(2024, 1, 15)

    def test_date_input(self):
        """Test date object input."""
        d = date(2024, 1, 15)
        assert parse_date(d) == d

    def test_none_with_default(self):
        """Test None input with default."""
        default = date(2024, 1, 1)
        assert parse_date(None, default=default) == default

    def test_invalid_format(self):
        """Test invalid date format."""
        with pytest.raises(NSEInvalidDateError):
            parse_date("not a date")


class TestFormatDate:
    """Tests for format_date function."""

    def test_display_format(self):
        """Test display format (ISO)."""
        result = format_date(date(2024, 1, 15), "display")
        assert result == "2024-01-15"

    def test_bhav_copy_old_format(self):
        """Test bhav copy old format."""
        result = format_date(date(2024, 1, 15), "bhav_copy_old")
        assert result == "15JAN2024"

    def test_bhav_copy_new_format(self):
        """Test bhav copy new format."""
        result = format_date(date(2024, 1, 15), "bhav_copy_new")
        assert result == "20240115"


class TestPeriodToDates:
    """Tests for period_to_dates function."""

    def test_1mo_period(self):
        """Test 1 month period."""
        start, end = period_to_dates("1mo")
        assert end == date.today()
        assert (end - start).days == 30

    def test_1y_period(self):
        """Test 1 year period."""
        start, end = period_to_dates("1y")
        assert end == date.today()
        assert (end - start).days == 365

    def test_ytd_period(self):
        """Test year-to-date period."""
        start, end = period_to_dates("ytd")
        assert start == date(date.today().year, 1, 1)

    def test_invalid_period(self):
        """Test invalid period."""
        with pytest.raises(NSEInvalidDateError):
            period_to_dates("invalid")


class TestValidateDateRange:
    """Tests for validate_date_range function."""

    def test_valid_range(self):
        """Test valid date range."""
        start, end = validate_date_range(
            date(2024, 1, 1),
            date(2024, 1, 31)
        )
        assert start == date(2024, 1, 1)
        assert end == date(2024, 1, 31)

    def test_swaps_if_reversed(self):
        """Test that reversed dates are swapped."""
        start, end = validate_date_range(
            date(2024, 1, 31),
            date(2024, 1, 1)
        )
        assert start == date(2024, 1, 1)
        assert end == date(2024, 1, 31)

    def test_clips_future_end_date(self):
        """Test that future end dates are clipped."""
        future = date.today() + timedelta(days=30)
        _, end = validate_date_range(date(2024, 1, 1), future)
        assert end <= date.today()

    def test_future_start_raises_error(self):
        """Test that future start date raises error."""
        future = date.today() + timedelta(days=30)
        with pytest.raises(NSEInvalidDateError):
            validate_date_range(future, future + timedelta(days=10))


class TestValidateSymbol:
    """Tests for validate_symbol function."""

    def test_valid_symbol(self):
        """Test valid symbol."""
        assert validate_symbol("RELIANCE") == "RELIANCE"

    def test_lowercase_normalized(self):
        """Test lowercase is normalized."""
        assert validate_symbol("reliance") == "RELIANCE"

    def test_trimmed(self):
        """Test whitespace is trimmed."""
        assert validate_symbol("  TCS  ") == "TCS"

    def test_with_ampersand(self):
        """Test symbol with ampersand."""
        assert validate_symbol("M&M") == "M&M"

    def test_with_hyphen(self):
        """Test symbol with hyphen."""
        assert validate_symbol("BAJAJ-AUTO") == "BAJAJ-AUTO"

    def test_empty_raises_error(self):
        """Test empty symbol raises error."""
        with pytest.raises(NSEInvalidSymbolError):
            validate_symbol("")

    def test_special_chars_raise_error(self):
        """Test special characters raise error."""
        with pytest.raises(NSEInvalidSymbolError):
            validate_symbol("INVALID@SYMBOL")


class TestIsTradingDay:
    """Tests for is_trading_day function."""

    def test_monday_is_trading_day(self):
        """Test Monday is trading day."""
        # Find a Monday
        d = date(2024, 1, 15)  # This is a Monday
        assert is_trading_day(d) is True

    def test_saturday_not_trading_day(self):
        """Test Saturday is not trading day."""
        d = date(2024, 1, 13)  # This is a Saturday
        assert is_trading_day(d) is False

    def test_sunday_not_trading_day(self):
        """Test Sunday is not trading day."""
        d = date(2024, 1, 14)  # This is a Sunday
        assert is_trading_day(d) is False


class TestGetPreviousTradingDay:
    """Tests for get_previous_trading_day function."""

    def test_from_tuesday(self):
        """Test previous trading day from Tuesday."""
        tuesday = date(2024, 1, 16)  # Tuesday
        assert get_previous_trading_day(tuesday) == date(2024, 1, 15)  # Monday

    def test_from_monday(self):
        """Test previous trading day from Monday."""
        monday = date(2024, 1, 15)  # Monday
        assert get_previous_trading_day(monday) == date(2024, 1, 12)  # Friday


class TestGetTradingDaysBetween:
    """Tests for get_trading_days_between function."""

    def test_full_week(self):
        """Test trading days in a full week."""
        start = date(2024, 1, 15)  # Monday
        end = date(2024, 1, 19)    # Friday
        days = get_trading_days_between(start, end)
        assert len(days) == 5

    def test_includes_endpoints(self):
        """Test that endpoints are included."""
        start = date(2024, 1, 15)
        end = date(2024, 1, 15)
        days = get_trading_days_between(start, end)
        assert len(days) == 1
        assert days[0] == start


class TestStandardizeDataframe:
    """Tests for standardize_dataframe function."""

    def test_lowercase_columns(self):
        """Test columns are lowercased."""
        df = pd.DataFrame({
            "OPEN": [100],
            "CLOSE": [105],
        })
        result = standardize_dataframe(df)
        assert "open" in result.columns
        assert "close" in result.columns

    def test_date_column_as_index(self):
        """Test date column becomes index."""
        df = pd.DataFrame({
            "date": ["2024-01-15"],
            "open": [100],
        })
        result = standardize_dataframe(df)
        assert result.index.name == "date"


class TestFilterBySeries:
    """Tests for filter_by_series function."""

    def test_filters_to_eq(self):
        """Test filtering to EQ series."""
        df = pd.DataFrame({
            "symbol": ["TEST", "TEST", "TEST"],
            "series": ["EQ", "BE", "SM"],
            "close": [100, 101, 102],
        })
        result = filter_by_series(df, ["EQ"])
        assert len(result) == 1
        assert result.iloc[0]["series"] == "EQ"


class TestAggregation:
    """Tests for data aggregation functions."""

    def test_aggregate_to_weekly(self):
        """Test weekly aggregation."""
        dates = pd.date_range("2024-01-01", periods=10, freq="D")
        df = pd.DataFrame({
            "open": range(10),
            "high": range(10, 20),
            "low": range(10),
            "close": range(5, 15),
            "volume": [1000] * 10,
        }, index=dates)
        df.index.name = "date"

        result = aggregate_to_weekly(df)
        assert len(result) < len(df)

    def test_aggregate_to_monthly(self):
        """Test monthly aggregation."""
        dates = pd.date_range("2024-01-01", periods=60, freq="D")
        df = pd.DataFrame({
            "open": range(60),
            "high": range(60, 120),
            "low": range(60),
            "close": range(30, 90),
            "volume": [1000] * 60,
        }, index=dates)
        df.index.name = "date"

        result = aggregate_to_monthly(df)
        assert len(result) < len(df)
