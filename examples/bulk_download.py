#!/usr/bin/env python3
"""
Bulk download example for nsefeed library.

This example demonstrates how to efficiently download
historical data for multiple stocks at once.
"""

import nsefeed as nf

# NIFTY 50 constituents (subset for demo)
NIFTY50_SAMPLE = [
    "RELIANCE", "TCS", "HDFCBANK", "INFY", "ICICIBANK",
    "HINDUNILVR", "ITC", "SBIN", "BHARTIARTL", "KOTAKBANK",
]

# NIFTY BANK constituents
NIFTY_BANK = [
    "HDFCBANK", "ICICIBANK", "KOTAKBANK", "AXISBANK", "SBIN",
    "INDUSINDBK", "BANKBARODA", "PNB", "AUBANK", "FEDERALBNK",
]


def main():
    print("=" * 60)
    print("nsefeed - Bulk Download Example")
    print("=" * 60)

    # Download multiple tickers at once
    print("\n1. Downloading NIFTY 50 sample stocks (last 1 month)...")
    
    data = nf.download(
        tickers=NIFTY50_SAMPLE,
        period="1mo",
    )
    
    # Print summary
    print("\nDownloaded data summary:")
    print("-" * 40)
    for symbol, df in data.items():
        if not df.empty:
            print(f"{symbol}: {len(df)} rows, "
                  f"Date range: {df.index.min().date()} to {df.index.max().date()}")
        else:
            print(f"{symbol}: No data")

    # Example: Calculate returns
    print("\n2. Calculating returns for downloaded stocks...")
    print("-" * 40)
    
    for symbol, df in data.items():
        if not df.empty and len(df) > 1:
            first_close = df["close"].iloc[0]
            last_close = df["close"].iloc[-1]
            returns = ((last_close / first_close) - 1) * 100
            print(f"{symbol}: {returns:+.2f}%")

    # Download weekly data for NIFTY BANK
    print("\n3. Downloading NIFTY BANK stocks (weekly, 3 months)...")
    
    bank_data = nf.download(
        tickers=NIFTY_BANK,
        period="3mo",
        interval="1wk",
    )
    
    print("\nNIFTY BANK weekly data summary:")
    for symbol, df in bank_data.items():
        if not df.empty:
            print(f"{symbol}: {len(df)} weeks")

    print("\n" + "=" * 60)
    print("Bulk download completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
