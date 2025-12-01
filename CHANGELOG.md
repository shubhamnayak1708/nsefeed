# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Index class for NIFTY 50, NIFTY BANK support
- Live data scraper
- Corporate actions (dividends, splits, bonuses)
- Async bulk downloads

## [0.1.0] - 2024-12-01

### Added
- **Core Infrastructure (Phase 1)**
  - `Ticker` class with yfinance-style API
  - `history()` method for fetching historical OHLCV data
  - `info` property for company information
  - `download()` function for bulk ticker downloads
  
- **NSE Session Management**
  - Singleton `NSESession` class for connection management
  - Automatic cookie/header handling
  - Session refresh on authentication failures
  - User-Agent rotation for resilience
  
- **Bhav Copy Scraper**
  - Support for old format (pre-July 2024)
  - Support for new UDiFF format (post-July 2024)
  - Automatic format fallback
  - Symbol filtering by series (EQ, BE, BZ)
  
- **SQLite Caching**
  - Thread-safe cache implementation
  - TTL support for different data types
  - OHLC data caching
  - Metadata caching with expiry
  - Cache statistics and management
  
- **Rate Limiting**
  - Built-in 3 req/sec limit to respect NSE servers
  - Exponential backoff on failures
  - Automatic retry with configurable attempts
  
- **Professional Logging**
  - Minimalistic timestamp format
  - Colored console output
  - Environment variable configuration
  - Optional file logging
  
- **Data Utilities**
  - Flexible date parsing (ISO, Indian, NSE formats)
  - Period to date range conversion
  - Weekly/monthly data aggregation
  - DataFrame standardization
  
- **Custom Exceptions**
  - `NSEConnectionError` - Network failures
  - `NSEDataNotFoundError` - Missing data
  - `NSERateLimitError` - Rate limiting
  - `NSEInvalidSymbolError` - Invalid symbols
  - `NSEInvalidDateError` - Invalid dates
  - `NSESessionError` - Session issues
  - `NSECacheError` - Cache failures
  - `NSEParseError` - Parsing failures
  
- **Testing**
  - Comprehensive unit test suite
  - 74 tests with mocking
  - Cache, session, ticker, and utility tests
  
- **Documentation**
  - Comprehensive README
  - API reference in docstrings
  - Example scripts
  - Type hints throughout

### Technical Details
- Python 3.9+ support
- pandas for data handling
- requests for HTTP
- SQLite for caching
- Modern pyproject.toml packaging

---

[Unreleased]: https://github.com/cryptolegit/nsefeed/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/cryptolegit/nsefeed/releases/tag/v0.1.0
