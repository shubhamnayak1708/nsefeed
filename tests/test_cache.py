"""
Unit tests for the cache module.
"""

import pytest
import tempfile
import shutil
from datetime import date, datetime
from pathlib import Path
import pandas as pd

from nsefeed.cache import NSECache, clear_cache


@pytest.fixture
def temp_cache_dir():
    """Create a temporary cache directory."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture(autouse=True)
def reset_cache():
    """Reset cache singleton before each test."""
    NSECache.reset_instance()
    yield
    NSECache.reset_instance()


class TestNSECacheInit:
    """Tests for cache initialization."""

    def test_creates_cache_directory(self, temp_cache_dir):
        """Test that cache directory is created."""
        cache_path = Path(temp_cache_dir) / "subcache"
        cache = NSECache(cache_path)
        assert cache_path.exists()

    def test_creates_database(self, temp_cache_dir):
        """Test that database file is created."""
        cache = NSECache(temp_cache_dir)
        db_path = Path(temp_cache_dir) / "cache.db"
        assert db_path.exists()


class TestNSECacheOHLC:
    """Tests for OHLC data caching."""

    def test_set_and_get_ohlc(self, temp_cache_dir):
        """Test storing and retrieving OHLC data."""
        cache = NSECache(temp_cache_dir)

        # Create sample DataFrame
        df = pd.DataFrame({
            "open": [100.0, 101.0],
            "high": [105.0, 106.0],
            "low": [99.0, 100.0],
            "close": [104.0, 105.0],
            "volume": [1000000, 1100000],
        }, index=pd.to_datetime(["2024-01-02", "2024-01-03"]))
        df.index.name = "date"

        # Store data
        cache.set_ohlc("RELIANCE", df)

        # Retrieve data
        result = cache.get_ohlc(
            "RELIANCE",
            date(2024, 1, 1),
            date(2024, 1, 5)
        )

        assert result is not None
        assert len(result) == 2
        assert "open" in result.columns

    def test_get_ohlc_returns_none_for_missing(self, temp_cache_dir):
        """Test that missing data returns None."""
        cache = NSECache(temp_cache_dir)
        result = cache.get_ohlc("UNKNOWN", date(2024, 1, 1), date(2024, 1, 5))
        assert result is None

    def test_get_cached_date_range(self, temp_cache_dir):
        """Test getting cached date range."""
        cache = NSECache(temp_cache_dir)

        df = pd.DataFrame({
            "open": [100.0, 101.0, 102.0],
            "high": [105.0, 106.0, 107.0],
            "low": [99.0, 100.0, 101.0],
            "close": [104.0, 105.0, 106.0],
            "volume": [1000000, 1100000, 1200000],
        }, index=pd.to_datetime(["2024-01-02", "2024-01-03", "2024-01-04"]))
        df.index.name = "date"

        cache.set_ohlc("TCS", df)

        start, end = cache.get_cached_date_range("TCS")
        assert start == date(2024, 1, 2)
        assert end == date(2024, 1, 4)

    def test_symbol_case_insensitive(self, temp_cache_dir):
        """Test that symbols are normalized to uppercase."""
        cache = NSECache(temp_cache_dir)

        df = pd.DataFrame({
            "open": [100.0],
            "close": [105.0],
        }, index=pd.to_datetime(["2024-01-02"]))
        df.index.name = "date"

        cache.set_ohlc("reliance", df)

        result = cache.get_ohlc("RELIANCE", date(2024, 1, 1), date(2024, 1, 5))
        assert result is not None


class TestNSECacheMetadata:
    """Tests for metadata caching."""

    def test_set_and_get_metadata(self, temp_cache_dir):
        """Test storing and retrieving metadata."""
        cache = NSECache(temp_cache_dir)

        data = {"key": "value", "number": 42}
        cache.set_metadata("test_key", data, ttl=3600)

        result = cache.get_metadata("test_key")
        assert result == data

    def test_metadata_expiry(self, temp_cache_dir):
        """Test that expired metadata returns None."""
        cache = NSECache(temp_cache_dir)

        cache.set_metadata("expiring", {"data": 1}, ttl=-1)  # Already expired

        result = cache.get_metadata("expiring")
        assert result is None

    def test_delete_metadata(self, temp_cache_dir):
        """Test deleting metadata."""
        cache = NSECache(temp_cache_dir)

        cache.set_metadata("to_delete", {"data": 1})
        cache.delete_metadata("to_delete")

        result = cache.get_metadata("to_delete")
        assert result is None


class TestNSECacheOperations:
    """Tests for cache operations."""

    def test_clear_symbol(self, temp_cache_dir):
        """Test clearing data for a symbol."""
        cache = NSECache(temp_cache_dir)

        df = pd.DataFrame({
            "open": [100.0],
            "close": [105.0],
        }, index=pd.to_datetime(["2024-01-02"]))
        df.index.name = "date"

        cache.set_ohlc("INFY", df)
        cache.clear_symbol("INFY")

        result = cache.get_ohlc("INFY", date(2024, 1, 1), date(2024, 1, 5))
        assert result is None

    def test_clear_all(self, temp_cache_dir):
        """Test clearing all cache data."""
        cache = NSECache(temp_cache_dir)

        df = pd.DataFrame({
            "open": [100.0],
            "close": [105.0],
        }, index=pd.to_datetime(["2024-01-02"]))
        df.index.name = "date"

        cache.set_ohlc("TEST1", df)
        cache.set_ohlc("TEST2", df)
        cache.set_metadata("meta", {"data": 1})

        cache.clear_all()

        assert cache.get_ohlc("TEST1", date(2024, 1, 1), date(2024, 1, 5)) is None
        assert cache.get_metadata("meta") is None

    def test_get_cache_stats(self, temp_cache_dir):
        """Test cache statistics."""
        cache = NSECache(temp_cache_dir)

        df = pd.DataFrame({
            "open": [100.0, 101.0],
            "close": [105.0, 106.0],
        }, index=pd.to_datetime(["2024-01-02", "2024-01-03"]))
        df.index.name = "date"

        cache.set_ohlc("STATS_TEST", df)

        stats = cache.get_cache_stats()
        assert stats["symbols_cached"] >= 1
        assert stats["ohlc_rows"] >= 2
