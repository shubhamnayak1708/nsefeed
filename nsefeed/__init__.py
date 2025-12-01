"""
nsefeed - A modern, yfinance-inspired Python library for NSE India market data.

This library provides a clean, intuitive interface for accessing NSE
equities, indices, and market data with proper error handling, caching,
and data validation.

Basic Usage:
    >>> import nsefeed as nf

    # Fetch historical data (yfinance-style API)
    >>> reliance = nf.Ticker("RELIANCE")
    >>> df = reliance.history(period="1mo")
    >>> print(df.head())

    # Get company info
    >>> print(reliance.info)

    # Download multiple tickers
    >>> data = nf.download(["RELIANCE", "TCS", "INFY"], period="1mo")

Features:
    - yfinance-inspired API design
    - Historical OHLC data from NSE bhav copies
    - SQLite caching to reduce server load
    - Rate limiting to respect NSE servers
    - Professional logging with timestamps
    - Comprehensive error handling

For more information, visit:
    https://github.com/yourusername/nsefeed
"""

from __future__ import annotations

__version__ = "0.1.0"
__author__ = "Your Name"
__license__ = "Apache-2.0"

# Core classes
from .ticker import Ticker
from .cache import clear_cache, NSECache
from .session import NSESession
from .logger import (
    enable_debug,
    disable_logging,
    set_log_level,
    get_logger,
)

# Exceptions
from .exceptions import (
    NSEError,
    NSEConnectionError,
    NSEDataNotFoundError,
    NSERateLimitError,
    NSEInvalidSymbolError,
    NSEInvalidDateError,
    NSESessionError,
    NSECacheError,
    NSEParseError,
)

# Public API
__all__ = [
    # Version
    "__version__",
    # Core classes
    "Ticker",
    "Index",  # Will be added in Phase 2
    # Functions
    "download",
    "clear_cache",
    # Logging
    "enable_debug",
    "disable_logging",
    "set_log_level",
    # Exceptions
    "NSEError",
    "NSEConnectionError",
    "NSEDataNotFoundError",
    "NSERateLimitError",
    "NSEInvalidSymbolError",
    "NSEInvalidDateError",
    "NSESessionError",
    "NSECacheError",
    "NSEParseError",
]


def download(
    tickers: str | list[str],
    period: str = "1mo",
    interval: str = "1d",
    start: str | None = None,
    end: str | None = None,
    threads: bool = True,
    progress: bool = True,
) -> dict[str, "pd.DataFrame"]:
    """
    Download historical data for multiple tickers.

    This function efficiently downloads data for multiple symbols by
    fetching bhav copies once per day and filtering for all requested
    symbols.

    Args:
        tickers: Single ticker symbol or list of symbols
                 Example: "RELIANCE" or ["RELIANCE", "TCS", "INFY"]

        period: Data period (ignored if start/end specified)
                Valid values: "1d", "5d", "1mo", "3mo", "6mo",
                             "1y", "2y", "5y", "10y", "ytd", "max"

        interval: Data interval
                  Valid values: "1d" (daily), "1wk" (weekly), "1mo" (monthly)

        start: Start date (optional, formats: "2024-01-15", "15-01-2024")

        end: End date (optional, defaults to today)

        threads: Whether to use parallel downloads (future feature)

        progress: Whether to show progress bar (future feature)

    Returns:
        Dictionary mapping symbols to their DataFrames
        Example: {"RELIANCE": DataFrame, "TCS": DataFrame, ...}

    Examples:
        >>> import nsefeed as nf

        # Download single ticker
        >>> data = nf.download("RELIANCE", period="1mo")
        >>> print(data["RELIANCE"].head())

        # Download multiple tickers
        >>> data = nf.download(["RELIANCE", "TCS", "INFY"], period="3mo")
        >>> for symbol, df in data.items():
        ...     print(f"{symbol}: {len(df)} rows")
    """
    import pandas as pd
    from .scrapers.bhav_copy import BhavCopyScraper
    from .utils import (
        parse_date,
        period_to_dates,
        validate_date_range,
        validate_symbol,
        aggregate_to_weekly,
        aggregate_to_monthly,
    )
    from . import logger

    # Normalize tickers to list
    if isinstance(tickers, str):
        tickers = [tickers]

    # Validate symbols
    tickers = [validate_symbol(t) for t in tickers]

    # Determine date range
    if start is not None or end is not None:
        from datetime import date as date_type
        start_date = parse_date(start) if start else None
        end_date = parse_date(end) if end else date_type.today()

        if start_date is None:
            # Default to 1 month before end
            from datetime import timedelta
            start_date = end_date - timedelta(days=30)
    else:
        start_date, end_date = period_to_dates(period)

    # Validate date range
    start_date, end_date = validate_date_range(start_date, end_date)

    logger.info(f"Downloading {len(tickers)} tickers: {start_date} to {end_date}")

    # Use bulk fetch for efficiency
    scraper = BhavCopyScraper(use_cache=True)
    results = scraper.fetch_bulk(tickers, start_date, end_date)

    # Apply interval aggregation if needed
    interval = interval.lower()
    if interval == "1wk":
        for symbol in results:
            if not results[symbol].empty:
                results[symbol] = aggregate_to_weekly(results[symbol])
    elif interval == "1mo":
        for symbol in results:
            if not results[symbol].empty:
                results[symbol] = aggregate_to_monthly(results[symbol])

    return results


# Placeholder for Index class (Phase 2)
class Index:
    """
    NSE Index class for accessing index data.

    Note: This class will be fully implemented in Phase 2.

    Args:
        name: Index name (e.g., "NIFTY", "NIFTYBANK")
    """

    def __init__(self, name: str) -> None:
        """Initialize Index."""
        from . import logger
        self._name = name.upper().replace(" ", "")
        logger.warning(f"Index class not yet fully implemented (Phase 2 feature)")

    @property
    def name(self) -> str:
        """Get the index name."""
        return self._name

    def history(self, period: str = "1mo", **kwargs) -> "pd.DataFrame":
        """Get historical index data (Phase 2 feature)."""
        import pandas as pd
        from . import logger
        logger.warning("Index.history() not yet implemented")
        return pd.DataFrame()

    @property
    def constituents(self) -> list[str]:
        """Get index constituents (Phase 2 feature)."""
        from . import logger
        logger.warning("Index.constituents not yet implemented")
        return []

    def __repr__(self) -> str:
        return f"Index('{self._name}')"
