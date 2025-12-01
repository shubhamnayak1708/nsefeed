#!/usr/bin/env python3
"""
Basic usage example for nsefeed library.

This example demonstrates how to fetch historical OHLC data
for NSE stocks using the yfinance-style API.
"""

import nsefeed as nf

# Enable debug logging to see what's happening
# nf.enable_debug()


def main():
    print("=" * 60)
    print("nsefeed - Basic Usage Example")
    print("=" * 60)

    # Example 1: Fetch historical data for a single stock
    print("\n1. Fetching RELIANCE historical data (last 1 month)...")
    reliance = nf.Ticker("RELIANCE")
    df = reliance.history(period="1mo")
    print(df.head())

    # Example 2: Fetch data for a specific date range
    print("\n2. Fetching TCS data for a specific date range...")
    tcs = nf.Ticker("TCS")
    df = tcs.history(start="2024-01-01", end="2024-01-31")
    print(f"Rows fetched: {len(df)}")
    print(df.head())

    # Example 3: Get weekly aggregated data
    print("\n3. Fetching INFY weekly data (last 3 months)...")
    infy = nf.Ticker("INFY")
    df = infy.history(period="3mo", interval="1wk")
    print(df)

    # Example 4: Get company info
    print("\n4. Getting company info for HDFCBANK...")
    hdfc = nf.Ticker("HDFCBANK")
    info = hdfc.info
    if "error" not in info:
        print(f"Company: {info.get('companyName', 'N/A')}")
        print(f"Industry: {info.get('industry', 'N/A')}")
        print(f"Last Price: ₹{info.get('lastPrice', 'N/A')}")
    else:
        print(f"Note: Could not fetch live info - {info.get('error')}")

    print("\n" + "=" * 60)
    print("Examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
