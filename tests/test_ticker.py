"""
Unit tests for the Ticker class.

These tests use mocking to avoid actual network requests during testing.
"""

import pytest
from datetime import date, datetime
from unittest.mock import Mock, patch, MagicMock
import pandas as pd

from nsefeed.ticker import Ticker
from nsefeed.exceptions import (
    NSEInvalidSymbolError,
    NSEInvalidDateError,
    NSEDataNotFoundError,
)


class TestTickerInit:
    """Tests for Ticker initialization."""

    @pytest.fixture(autouse=True)
    def mock_session_and_cache(self):
        """Mock NSESession and NSECache for all init tests."""
        with patch("nsefeed.ticker.NSESession") as mock_session:
            with patch("nsefeed.ticker.NSECache"):
                with patch("nsefeed.ticker.BhavCopyScraper"):
                    mock_session.get_instance.return_value = Mock()
                    yield

    def test_valid_symbol(self, mock_session_and_cache):
        """Test initialization with valid symbol."""
        ticker = Ticker("RELIANCE")
        assert ticker.symbol == "RELIANCE"

    def test_symbol_case_insensitive(self, mock_session_and_cache):
        """Test that symbols are normalized to uppercase."""
        ticker = Ticker("reliance")
        assert ticker.symbol == "RELIANCE"

    def test_symbol_with_spaces_trimmed(self, mock_session_and_cache):
        """Test that symbols are trimmed."""
        ticker = Ticker("  RELIANCE  ")
        assert ticker.symbol == "RELIANCE"

    def test_invalid_symbol_empty(self, mock_session_and_cache):
        """Test that empty symbol raises error."""
        with pytest.raises(NSEInvalidSymbolError):
            Ticker("")

    def test_invalid_symbol_special_chars(self, mock_session_and_cache):
        """Test that special characters raise error."""
        with pytest.raises(NSEInvalidSymbolError):
            Ticker("INVALID@SYMBOL")

    def test_ticker_repr(self, mock_session_and_cache):
        """Test string representation."""
        ticker = Ticker("TCS")
        assert repr(ticker) == "Ticker('TCS')"


class TestTickerHistory:
    """Tests for Ticker.history() method."""

    @pytest.fixture
    def mock_bhav_scraper(self):
        """Create a mock bhav copy scraper."""
        with patch("nsefeed.ticker.NSESession") as mock_session:
            with patch("nsefeed.ticker.NSECache"):
                with patch("nsefeed.ticker.BhavCopyScraper") as mock:
                    mock_session.get_instance.return_value = Mock()
                    mock_instance = Mock()
                    mock.return_value = mock_instance

                    # Create sample DataFrame
                    sample_data = pd.DataFrame({
                        "open": [100.0, 101.0, 102.0],
                        "high": [105.0, 106.0, 107.0],
                        "low": [99.0, 100.0, 101.0],
                        "close": [104.0, 105.0, 106.0],
                        "volume": [1000000, 1100000, 1200000],
                    }, index=pd.to_datetime(["2024-01-02", "2024-01-03", "2024-01-04"]))
                    sample_data.index.name = "date"

                    mock_instance.fetch_for_symbol.return_value = sample_data
                    yield mock_instance

    def test_history_with_period(self, mock_bhav_scraper):
        """Test fetching history with period."""
        ticker = Ticker("RELIANCE")
        df = ticker.history(period="1mo")

        assert not df.empty
        assert "open" in df.columns
        assert "close" in df.columns
        assert "volume" in df.columns

    def test_history_with_dates(self, mock_bhav_scraper):
        """Test fetching history with explicit dates."""
        ticker = Ticker("RELIANCE")
        df = ticker.history(start="2024-01-01", end="2024-01-31")

        mock_bhav_scraper.fetch_for_symbol.assert_called_once()
        call_args = mock_bhav_scraper.fetch_for_symbol.call_args
        assert call_args[0][0] == "RELIANCE"

    def test_history_invalid_interval(self, mock_bhav_scraper):
        """Test that invalid interval raises error."""
        ticker = Ticker("RELIANCE")
        with pytest.raises(ValueError, match="Invalid interval"):
            ticker.history(period="1mo", interval="invalid")

    def test_history_empty_result(self, mock_bhav_scraper):
        """Test that empty result raises error."""
        mock_bhav_scraper.fetch_for_symbol.return_value = pd.DataFrame()

        ticker = Ticker("UNKNOWN")
        with pytest.raises(NSEDataNotFoundError):
            ticker.history(period="1mo")

    def test_history_weekly_aggregation(self, mock_bhav_scraper):
        """Test weekly interval aggregation."""
        ticker = Ticker("RELIANCE")
        df = ticker.history(period="1mo", interval="1wk")

        # Should be aggregated (fewer rows than daily)
        assert not df.empty


class TestTickerInfo:
    """Tests for Ticker.info property."""

    @pytest.fixture
    def mock_session(self):
        """Create a mock NSE session."""
        with patch("nsefeed.ticker.NSESession") as mock:
            mock_instance = Mock()
            mock.get_instance.return_value = mock_instance

            mock_instance.get_json.return_value = {
                "info": {
                    "companyName": "Reliance Industries Limited",
                    "industry": "REFINERIES",
                    "isin": "INE002A01018",
                    "faceVal": 10,
                    "activeSeries": ["EQ"],
                },
                "priceInfo": {
                    "lastPrice": 2500.00,
                    "change": 25.50,
                    "pChange": 1.03,
                    "previousClose": 2474.50,
                }
            }
            yield mock_instance

    def test_info_returns_dict(self, mock_session):
        """Test that info returns a dictionary."""
        with patch("nsefeed.ticker.BhavCopyScraper"):
            with patch("nsefeed.ticker.NSECache") as mock_cache:
                mock_cache.return_value.get_metadata.return_value = None
                ticker = Ticker("RELIANCE")
                info = ticker.info

                assert isinstance(info, dict)
                assert info.get("symbol") == "RELIANCE"


class TestTickerValidation:
    """Tests for input validation."""

    def test_date_formats(self):
        """Test various date format handling."""
        from nsefeed.utils import parse_date

        # ISO format
        assert parse_date("2024-01-15") == date(2024, 1, 15)

        # Indian format
        assert parse_date("15-01-2024") == date(2024, 1, 15)

        # NSE format
        assert parse_date("15JAN2024") == date(2024, 1, 15)

    def test_period_validation(self):
        """Test period string validation."""
        from nsefeed.utils import period_to_dates

        start, end = period_to_dates("1mo")
        assert start < end

        with pytest.raises(NSEInvalidDateError):
            period_to_dates("invalid")


class TestTickerCaching:
    """Tests for caching behavior."""

    def test_info_cached(self):
        """Test that info is cached."""
        with patch("nsefeed.ticker.NSESession"):
            with patch("nsefeed.ticker.BhavCopyScraper"):
                with patch("nsefeed.ticker.NSECache") as mock_cache:
                    mock_cache_instance = Mock()
                    mock_cache.return_value = mock_cache_instance

                    # First call - cache miss
                    mock_cache_instance.get_metadata.return_value = None

                    ticker = Ticker("RELIANCE")

                    # Set up mock for info property
                    with patch.object(ticker, "_session") as mock_sess:
                        mock_sess.get_json.return_value = {
                            "info": {"companyName": "Test"},
                            "priceInfo": {}
                        }

                        # Access info
                        _ = ticker.info

                        # Second access should use cached value
                        _ = ticker.info

                        # Session should only be called once
                        assert mock_sess.get_json.call_count == 1
