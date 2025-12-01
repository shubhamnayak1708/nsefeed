"""
Constants and configuration for nsefeed library.

This module contains all static configuration values including:
- NSE API endpoints and archive URLs
- HTTP headers for session management
- Rate limiting configuration
- Index definitions (NIFTY 50, NIFTY BANK)
- Cache configuration
"""

from __future__ import annotations

from typing import Final

# =============================================================================
# NSE Website URLs
# =============================================================================

NSE_BASE_URL: Final[str] = "https://www.nseindia.com"
NSE_ARCHIVES_URL: Final[str] = "https://archives.nseindia.com"
NSE_NEW_ARCHIVES_URL: Final[str] = "https://nsearchives.nseindia.com"

# =============================================================================
# NSE API Endpoints (Unofficial - requires session cookies)
# =============================================================================

NSE_ENDPOINTS: Final[dict[str, str]] = {
    # Homepage - for session initialization
    "home": f"{NSE_BASE_URL}/",
    # Equity data
    "quote_equity": f"{NSE_BASE_URL}/api/quote-equity",
    "trade_info": f"{NSE_BASE_URL}/api/quote-equity",  # with section=trade_info
    "equity_master": f"{NSE_BASE_URL}/api/equity-master",
    # Index data
    "stock_indices": f"{NSE_BASE_URL}/api/equity-stockIndices",
    "index_names": f"{NSE_BASE_URL}/api/allIndices",
    # Historical data
    "historical": f"{NSE_BASE_URL}/api/historical/cm/equity",
    "chart_data": f"{NSE_BASE_URL}/api/chart-databyindex",
    # Corporate actions
    "corporate_actions": f"{NSE_BASE_URL}/api/corporates-corporateActions",
    # Market status
    "market_status": f"{NSE_BASE_URL}/api/marketStatus",
    # Holiday list
    "holiday_list": f"{NSE_BASE_URL}/api/holiday-master",
}

# =============================================================================
# Bhav Copy URL Templates
# =============================================================================

# Old format (works for historical data)
# Example: https://archives.nseindia.com/content/historical/EQUITIES/2024/JAN/cm02JAN2024bhav.csv.zip
BHAV_COPY_OLD_URL: Final[str] = (
    f"{NSE_ARCHIVES_URL}/content/historical/EQUITIES/"
    "{{year}}/{{month}}/cm{{date}}bhav.csv.zip"
)

# New format (UDiFF format, recent data)
# Example: https://nsearchives.nseindia.com/content/cm/BhavCopy_NSE_CM_0_0_0_20241129_F_0000.csv.zip
BHAV_COPY_NEW_URL: Final[str] = (
    f"{NSE_NEW_ARCHIVES_URL}/content/cm/"
    "BhavCopy_NSE_CM_0_0_0_{{date}}_F_0000.csv.zip"
)

# Delivery data URL
DELIVERY_DATA_URL: Final[str] = (
    f"{NSE_ARCHIVES_URL}/products/content/sec_bhavdata_full_"
    "{{date}}.csv"
)

# Index historical data URL
INDEX_HISTORICAL_URL: Final[str] = (
    f"{NSE_ARCHIVES_URL}/content/indices/ind_close_all_{{date}}.csv"
)

# =============================================================================
# HTTP Headers (Required for NSE requests)
# =============================================================================

DEFAULT_HEADERS: Final[dict[str, str]] = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
}

# Headers for archive downloads
ARCHIVE_HEADERS: Final[dict[str, str]] = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
}

# Rotating User-Agents for better resilience
USER_AGENTS: Final[list[str]] = [
    (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) "
        "Gecko/20100101 Firefox/121.0"
    ),
    (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) "
        "Version/17.2 Safari/605.1.15"
    ),
    (
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
]

# =============================================================================
# Rate Limiting Configuration
# =============================================================================

# Maximum requests per second (NSE unofficial limit)
MAX_REQUESTS_PER_SECOND: Final[float] = 3.0

# Minimum delay between requests (in seconds)
MIN_REQUEST_DELAY: Final[float] = 0.35  # Slightly more than 1/3 second

# Retry configuration
MAX_RETRIES: Final[int] = 3
RETRY_BACKOFF_FACTOR: Final[float] = 1.5  # Exponential backoff multiplier
INITIAL_RETRY_DELAY: Final[float] = 1.0  # Initial retry delay in seconds

# Request timeout (in seconds)
REQUEST_TIMEOUT: Final[int] = 30

# Session refresh interval (in seconds) - refresh session every 5 minutes
SESSION_REFRESH_INTERVAL: Final[int] = 300

# =============================================================================
# Cache Configuration
# =============================================================================

# Default cache directory (relative to user home)
DEFAULT_CACHE_DIR: Final[str] = ".nsefeed"

# Cache database filename
CACHE_DB_NAME: Final[str] = "cache.db"

# Cache TTL (Time To Live) in seconds
CACHE_TTL: Final[dict[str, int]] = {
    "historical_data": 7 * 24 * 3600,  # 7 days for historical OHLC
    "live_data": 5 * 60,  # 5 minutes for live data
    "company_info": 24 * 3600,  # 24 hours for company info
    "index_constituents": 7 * 24 * 3600,  # 7 days for index lists
    "market_status": 60,  # 1 minute for market status
}

# =============================================================================
# Date Formats
# =============================================================================

# NSE uses various date formats
DATE_FORMATS: Final[dict[str, str]] = {
    "bhav_copy_old": "%d%b%Y",  # 02JAN2024
    "bhav_copy_new": "%Y%m%d",  # 20240102
    "api": "%d-%m-%Y",  # 02-01-2024
    "display": "%Y-%m-%d",  # 2024-01-02
    "index_file": "%d%m%Y",  # 02012024
}

# =============================================================================
# Valid Series Types
# =============================================================================

EQUITY_SERIES: Final[list[str]] = [
    "EQ",  # Equity
    "BE",  # Book Entry
    "BZ",  # Trade to Trade (Z group)
    "SM",  # SME
    "ST",  # SME Trade to Trade
    "N1",  # NIFTY 50 ETF
    "N2",  # Other ETFs
    "N3",  # Gold ETFs
    "N4",  # Other ETFs
    "N5",  # Infrastructure ETFs
    "N6",  # PSU ETFs
    "N7",  # Shariah ETFs
    "N8",  # Dividend ETFs
]

# Primary series for regular stocks
PRIMARY_SERIES: Final[list[str]] = ["EQ", "BE", "BZ"]

# =============================================================================
# Period Mappings (yfinance-compatible)
# =============================================================================

PERIOD_DAYS: Final[dict[str, int]] = {
    "1d": 1,
    "5d": 5,
    "1mo": 30,
    "3mo": 90,
    "6mo": 180,
    "1y": 365,
    "2y": 730,
    "5y": 1825,
    "10y": 3650,
    "ytd": -1,  # Special handling for year-to-date
    "max": -2,  # Special handling for maximum available
}

# =============================================================================
# Interval Mappings
# =============================================================================

VALID_INTERVALS: Final[list[str]] = [
    "1d",  # Daily (primary, from bhav copy)
    "1wk",  # Weekly (aggregated from daily)
    "1mo",  # Monthly (aggregated from daily)
]

# =============================================================================
# Market Hours (IST)
# =============================================================================

MARKET_OPEN_HOUR: Final[int] = 9
MARKET_OPEN_MINUTE: Final[int] = 15
MARKET_CLOSE_HOUR: Final[int] = 15
MARKET_CLOSE_MINUTE: Final[int] = 30

# Pre-market session
PRE_MARKET_OPEN_HOUR: Final[int] = 9
PRE_MARKET_OPEN_MINUTE: Final[int] = 0
PRE_MARKET_CLOSE_HOUR: Final[int] = 9
PRE_MARKET_CLOSE_MINUTE: Final[int] = 8

# =============================================================================
# Bhav Copy Column Mappings
# =============================================================================

# Old bhav copy format columns
BHAV_COPY_OLD_COLUMNS: Final[dict[str, str]] = {
    "SYMBOL": "symbol",
    "SERIES": "series",
    "OPEN": "open",
    "HIGH": "high",
    "LOW": "low",
    "CLOSE": "close",
    "LAST": "last",
    "PREVCLOSE": "prev_close",
    "TOTTRDQTY": "volume",
    "TOTTRDVAL": "value",
    "TIMESTAMP": "date",
    "TOTALTRADES": "trades",
    "ISIN": "isin",
}

# New bhav copy format columns (UDiFF format)
BHAV_COPY_NEW_COLUMNS: Final[dict[str, str]] = {
    "TckrSymb": "symbol",
    "SctySrs": "series",
    "OpnPric": "open",
    "HghPric": "high",
    "LwPric": "low",
    "ClsPric": "close",
    "LastPric": "last",
    "PrvsClsgPric": "prev_close",
    "TtlTradgVol": "volume",
    "TtlTrfVal": "value",
    "TradDt": "date",
    "TtlNbOfTxsExctd": "trades",
    "ISIN": "isin",
}

# Output DataFrame columns (standardized)
OUTPUT_COLUMNS: Final[list[str]] = [
    "date",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "value",
    "trades",
]
