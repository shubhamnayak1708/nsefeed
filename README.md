<div align="left">

<img src="docs/src/nsefeed-logo.webp" alt="nsefeed" width="400"/>

[![PyPI version](https://badge.fury.io/py/nsefeed.svg)](https://badge.fury.io/py/nsefeed)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-under%20development-yellow.svg)]()

A modern Python library for NSE India market data with yfinance-inspired API design.

[Installation](#installation) | [Quick Start](#quick-start) | [Examples](#examples) | [API Reference](#api-reference)

</div>

---

## ✨ Features

- **yfinance-style API** - Familiar interface for Python developers
- **Historical OHLCV Data** - Official NSE bhav copies with SQLite caching
- **Comprehensive Coverage** - Capital Market, Derivatives, and Debt modules
- **Type Hints** - Full type coverage for IDE support
- **Production Ready** - Rate limiting, error handling, and session management

## 📦 Installation

```bash
pip install nsefeed

# With .env file support
pip install nsefeed[dotenv]
```

## 🚀 Quick Start

```python
import nsefeed as nf

# Fetch historical data (yfinance-style)
ticker = nf.Ticker("RELIANCE")
df = ticker.history(period="1mo")
print(df.head())

# Download multiple tickers
data = nf.download(["RELIANCE", "TCS", "INFY"], period="1mo")
```

## 📊 Usage Examples

### Historical Data

```python
import nsefeed as nf

ticker = nf.Ticker("RELIANCE")

# Different periods and intervals
df = ticker.history(period="1mo")           # 1 month daily
df = ticker.history(period="1y", interval="1wk")  # 1 year weekly
df = ticker.history(start="2025-01-01", end="2025-12-01")  # Custom range

# DataFrame columns: open, high, low, close, volume, value, trades
```

### Batch Download

```python
import nsefeed as nf

# Download multiple stocks
stocks = ["RELIANCE", "TCS", "HDFCBANK", "INFY", "ICICIBANK"]
data = nf.download(stocks, period="1mo")

for symbol, df in data.items():
    print(f"{symbol}: Latest close Rs.{df['close'].iloc[-1]:.2f}")
```

### Portfolio Analysis

```python
import nsefeed as nf

portfolio = {"RELIANCE": 100, "TCS": 50, "HDFCBANK": 75}
data = nf.download(list(portfolio.keys()), period="1mo")

total_value = sum(data[s]['close'].iloc[-1] * q for s, q in portfolio.items())
print(f"Portfolio Value: Rs.{total_value:,.2f}")
```

### Strategy Backtesting

```python
import nsefeed as nf

ticker = nf.Ticker("TATASTEEL")
df = ticker.history(period="6mo")

# Calculate moving averages
df['SMA_20'] = df['close'].rolling(window=20).mean()
df['SMA_50'] = df['close'].rolling(window=50).mean()

# Generate signals
df['signal'] = 0
df.loc[df['SMA_20'] > df['SMA_50'], 'signal'] = 1   # Buy
df.loc[df['SMA_20'] < df['SMA_50'], 'signal'] = -1  # Sell
```

## 🔧 Configuration

```python
import nsefeed as nf

# Logging
nf.set_log_level("INFO")
nf.enable_debug()

# Cache management
nf.clear_cache()
```

Or use `.env` file:

```bash
NSEFEED_LOG_LEVEL=INFO
NSEFEED_RATE_LIMIT=3.0
NSEFEED_CACHE_DIR=
```

## 📚 API Reference

### Core API

- `Ticker(symbol)` - Access historical data for a symbol
  - `.history(period, start, end, interval)` - Get OHLCV data
  - `.info` - Company information

- `download(tickers, period, start, end, interval)` - Batch download multiple tickers

### Advanced Modules

**Capital Market** (21 functions)
- `get_quote()`, `get_bulk_deals()`, `get_block_deals()`, `get_market_status()`, `get_nifty50_list()`, and more

**Derivatives** (11 functions)
- `get_option_chain()`, `get_fno_quote()`, `get_future_price_volume()`, and more

**Debt** (1 function)
- `get_corporate_bond_trades()`

> **Note**: Live API functions require NSE API access and may be rate-limited. Use `Ticker` class for reliable historical data.

## 🧪 Testing

```bash
# Run comprehensive tests
.\test.bat

# Quick test
python -c "import nsefeed as nf; print(nf.Ticker('RELIANCE').history(period='5d'))"
```

## ⚠️ Important Notes

### Data Reliability

✅ **Recommended**: `Ticker` class and `download()` - Fetch from official NSE bhav copies (highly reliable)

⚡ **Advanced**: Live API functions in `capital_market`, `derivatives`, `debt` modules may be rate-limited or require additional authentication

### Features

- **Rate Limiting**: Automatic (3 requests/second default)
- **Caching**: SQLite cache at `~/.nsefeed/cache.db`
- **Type Safety**: Full type hints for IDE support

## 🏗️ Architecture

```
nsefeed/
├── ticker.py           # Ticker class (yfinance-style)
├── session.py          # NSE session management
├── cache.py            # SQLite caching
├── config.py           # Configuration
├── scrapers/           # Bhav copy scrapers
├── capital_market/     # Capital market data (21 functions)
├── derivatives/        # Derivatives data (11 functions)
└── debt/               # Debt market data (1 function)
```

## 🤝 Contributing

Contributions are welcome! This library aims to be the best NSE data source for the Python/trading community.

### Development Status

🚧 **Under Active Development** - Features and APIs may change. Core `Ticker` functionality is stable.

## 💰 Support This Project

If you find this project valuable, consider supporting its development:

<a href="https://www.buymeacoffee.com/shubhamnayak" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/default-orange.png" alt="Buy Me A Coffee" height="41" width="174"></a>

**⚡ Built by [Shubham Nayak](https://linkedin.com/in/shubham-nayak-591375276)**

## 📄 License

Apache License 2.0 - Copyright 2025 nsefeed developers

## 🙏 Acknowledgments

- Inspired by [yfinance](https://github.com/ranaroussi/yfinance) by Ran Aroussi
- NSE India for providing public data
- The Python trading community

## ⚖️ Disclaimer

This library is for educational and research purposes. Not affiliated with or endorsed by NSE India. Users are responsible for complying with NSE's terms of service. Always verify critical data with official NSE sources.

---

<div align="center">

**Made with ❤️ for the Indian trading community**

[Report Issues](https://github.com/nsefeed/nsefeed/issues) | [Documentation](COMPREHENSIVE_GUIDE.md)

</div>
