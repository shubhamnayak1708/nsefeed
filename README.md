# nsefeed

[![PyPI version](https://badge.fury.io/py/nsefeed.svg)](https://badge.fury.io/py/nsefeed)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)

A modern, Python library for accessing NSE India market data. Clean API, robust caching, and proper error handling.

## ✨ Features

- 🎯 **yfinance-style API** - Familiar interface for Python developers
- 📊 **Historical OHLCV data** - From official NSE bhav copies
- 💾 **SQLite caching** - Reduces server load & improves performance
- ⏱️ **Rate limiting** - Respects NSE server limits (3 req/sec)
- 🔄 **Automatic retries** - Exponential backoff on failures
- 📝 **Professional logging** - Clean timestamps, configurable levels
- 🛡️ **Type hints** - Full type coverage for IDE support
- ✅ **Well tested** - Comprehensive test suite with mocking

## 🚀 Quick Start

### Installation

```bash
pip install nsefeed
```

### Basic Usage

```python
import nsefeed as nf

# Fetch historical data (yfinance-style API)
reliance = nf.Ticker("RELIANCE")
df = reliance.history(period="1mo")
print(df.head())
```

**Output:**
```
                  open     high      low    close      volume
date
2024-11-01     1245.50  1258.30  1240.00  1255.75     2345678
2024-11-04     1256.00  1268.90  1252.10  1265.40     2567890
2024-11-05     1266.00  1275.00  1260.00  1272.50     2123456
```

### Date Range Queries

```python
# Specific date range
df = reliance.history(start="2024-01-01", end="2024-06-30")

# Different intervals
df = reliance.history(period="3mo", interval="1wk")  # Weekly data
df = reliance.history(period="1y", interval="1mo")   # Monthly data
```

### Multiple Tickers

```python
# Download multiple tickers at once
data = nf.download(
    tickers=["RELIANCE", "TCS", "INFY", "HDFCBANK"],
    period="1mo"
)

# Access individual DataFrames
print(data["RELIANCE"].head())
print(data["TCS"].head())
```

### Company Information

```python
reliance = nf.Ticker("RELIANCE")
info = reliance.info

print(f"Company: {info['companyName']}")
print(f"Industry: {info['industry']}")
print(f"Last Price: ₹{info['lastPrice']}")
```

## 📖 API Reference

### Ticker Class

```python
ticker = nf.Ticker("SYMBOL")
```

**Methods:**

| Method | Description |
|--------|-------------|
| `history(period, interval, start, end)` | Get historical OHLCV data |
| `info` | Get company information (property) |
| `get_ohlc(start, end)` | Convenience method for OHLC only |

**Parameters for `history()`:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `period` | str | "1mo" | Data period: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max |
| `interval` | str | "1d" | Data interval: 1d (daily), 1wk (weekly), 1mo (monthly) |
| `start` | str/date | None | Start date (overrides period) |
| `end` | str/date | None | End date (defaults to today) |

### download() Function

```python
data = nf.download(
    tickers=["RELIANCE", "TCS"],
    period="1mo",
    interval="1d"
)
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `tickers` | str/list | required | Single symbol or list of symbols |
| `period` | str | "1mo" | Data period |
| `interval` | str | "1d" | Data interval |
| `start` | str | None | Start date |
| `end` | str | None | End date |

## 🔧 Configuration

### Logging

```python
import nsefeed as nf

# Enable debug logging
nf.enable_debug()

# Disable logging
nf.disable_logging()

# Set specific level
nf.set_log_level("WARNING")
```

**Environment Variables:**

```bash
export NSEFEED_LOG_LEVEL=DEBUG    # DEBUG, INFO, WARNING, ERROR
export NSEFEED_LOG_FILE=app.log   # Optional file logging
```

### Cache Management

```python
import nsefeed as nf

# Clear all cached data
nf.clear_cache()

# Get cache statistics
from nsefeed import NSECache
cache = NSECache()
stats = cache.get_cache_stats()
print(f"Symbols cached: {stats['symbols_cached']}")
print(f"OHLC rows: {stats['ohlc_rows']}")
```

Cache is stored at `~/.nsefeed/cache.db` by default.

## ⚠️ Error Handling

```python
import nsefeed as nf
from nsefeed.exceptions import (
    NSEInvalidSymbolError,
    NSEDataNotFoundError,
    NSEConnectionError
)

try:
    ticker = nf.Ticker("INVALIDSYMBOL")
    df = ticker.history(period="1mo")
except NSEInvalidSymbolError as e:
    print(f"Invalid symbol: {e}")
except NSEDataNotFoundError as e:
    print(f"No data available: {e}")
except NSEConnectionError as e:
    print(f"Connection failed: {e}")
```

## 📊 Data Sources

nsefeed uses official NSE data sources:

- **Historical Data**: NSE Bhav Copy files (daily EOD data)
  - Old format: `archives.nseindia.com/content/historical/EQUITIES/`
  - New format (UDiFF): `nsearchives.nseindia.com/content/cm/`
  
- **Live Data**: NSE API endpoints (coming in Phase 2)

## 🗺️ Roadmap

### ✅ Phase 1 (Current) - Core Infrastructure
- [x] NSE session management with cookies/headers
- [x] Bhav copy scraper for historical data
- [x] Ticker class with yfinance-style API
- [x] SQLite caching layer
- [x] Rate limiting (3 req/sec)
- [x] Professional logging
- [x] Unit tests

### 🔄 Phase 2 (Planned) - Enhanced Features
- [ ] Index class (NIFTY 50, NIFTY BANK)
- [ ] Live data scraper
- [ ] Corporate actions (dividends, splits, bonuses)
- [ ] Ticker.info enhancement
- [ ] Async bulk downloads

### 📦 Phase 3 (Planned) - Polish & Release
- [ ] Complete documentation
- [ ] Example scripts
- [ ] CI/CD pipeline
- [ ] PyPI release

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Setup

```bash
# Clone the repository
git clone https://github.com/cryptolegit/nsefeed.git
cd nsefeed

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run with coverage
pytest --cov=nsefeed --cov-report=html
```

## 📜 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Inspired by [yfinance](https://github.com/ranaroussi/yfinance) for API design
- [BennyThadikaran/NseIndiaApi](https://github.com/BennyThadikaran/NseIndiaApi) for NSE session handling patterns
- NSE India for providing public market data

## ⚖️ Disclaimer

This is an unofficial library. NSE India does not provide official APIs for programmatic access. This library scrapes publicly available data. Please use responsibly and respect rate limits.

---

**Made with ❤️ for the Indian trading community**
