#!/usr/bin/env python3
"""
Monte Carlo SDE Simulation Example using nsefeed.

This example demonstrates how to:
1. Fetch historical data for NIFTY 50 stocks
2. Calculate returns and volatility
3. Run a basic Geometric Brownian Motion (GBM) simulation

This is a foundation for more advanced SDE-based portfolio simulations.
"""

import numpy as np
import pandas as pd
import nsefeed as nf
from datetime import date

# Configuration
TICKERS = ["RELIANCE", "TCS", "HDFCBANK", "INFY", "ICICIBANK"]
SIMULATION_DAYS = 252  # Trading days in a year
NUM_SIMULATIONS = 1000


def fetch_historical_data(tickers: list, period: str = "1y") -> dict:
    """Fetch historical data for multiple tickers."""
    print(f"Fetching {period} historical data for {len(tickers)} stocks...")
    return nf.download(tickers=tickers, period=period)


def calculate_parameters(data: dict) -> pd.DataFrame:
    """Calculate annualized returns and volatility for each stock."""
    params = []
    
    for symbol, df in data.items():
        if df.empty or len(df) < 30:
            continue
            
        # Calculate daily returns
        returns = df["close"].pct_change().dropna()
        
        # Annualize (252 trading days)
        daily_mean = returns.mean()
        daily_std = returns.std()
        
        annual_return = daily_mean * 252
        annual_vol = daily_std * np.sqrt(252)
        
        params.append({
            "symbol": symbol,
            "last_price": df["close"].iloc[-1],
            "annual_return": annual_return,
            "annual_volatility": annual_vol,
            "daily_return": daily_mean,
            "daily_volatility": daily_std,
        })
    
    return pd.DataFrame(params)


def simulate_gbm(s0: float, mu: float, sigma: float, 
                 days: int, simulations: int) -> np.ndarray:
    """
    Simulate Geometric Brownian Motion (GBM).
    
    dS = μS dt + σS dW
    
    Args:
        s0: Initial stock price
        mu: Annual drift (expected return)
        sigma: Annual volatility
        days: Number of trading days to simulate
        simulations: Number of Monte Carlo paths
    
    Returns:
        Array of shape (simulations, days+1) with price paths
    """
    dt = 1 / 252  # Daily time step
    
    # Generate random shocks
    np.random.seed(42)  # For reproducibility
    dW = np.random.normal(0, 1, (simulations, days))
    
    # Initialize price paths
    paths = np.zeros((simulations, days + 1))
    paths[:, 0] = s0
    
    # Simulate using exact solution
    for t in range(1, days + 1):
        paths[:, t] = paths[:, t-1] * np.exp(
            (mu - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * dW[:, t-1]
        )
    
    return paths


def run_portfolio_simulation(params_df: pd.DataFrame, 
                            weights: dict = None) -> dict:
    """Run Monte Carlo simulation for a portfolio."""
    if weights is None:
        # Equal weight portfolio
        n = len(params_df)
        weights = {row["symbol"]: 1/n for _, row in params_df.iterrows()}
    
    print(f"\nRunning Monte Carlo simulation...")
    print(f"- {NUM_SIMULATIONS} simulations")
    print(f"- {SIMULATION_DAYS} trading days")
    print(f"- Portfolio weights: {weights}")
    
    portfolio_value = np.zeros((NUM_SIMULATIONS, SIMULATION_DAYS + 1))
    
    for _, row in params_df.iterrows():
        symbol = row["symbol"]
        if symbol not in weights:
            continue
            
        weight = weights[symbol]
        paths = simulate_gbm(
            s0=row["last_price"],
            mu=row["annual_return"],
            sigma=row["annual_volatility"],
            days=SIMULATION_DAYS,
            simulations=NUM_SIMULATIONS,
        )
        
        # Normalize and add to portfolio
        portfolio_value += weight * (paths / paths[:, 0:1])
    
    return {
        "paths": portfolio_value,
        "final_values": portfolio_value[:, -1],
        "mean_return": np.mean(portfolio_value[:, -1]) - 1,
        "std_return": np.std(portfolio_value[:, -1]),
        "var_95": np.percentile(portfolio_value[:, -1], 5) - 1,
        "var_99": np.percentile(portfolio_value[:, -1], 1) - 1,
    }


def main():
    print("=" * 60)
    print("Monte Carlo SDE Portfolio Simulation")
    print("=" * 60)
    
    # Step 1: Fetch historical data
    data = fetch_historical_data(TICKERS, period="1y")
    
    # Step 2: Calculate parameters
    print("\nCalculating return and volatility parameters...")
    params_df = calculate_parameters(data)
    print("\nStock Parameters:")
    print(params_df.to_string(index=False))
    
    # Step 3: Run simulation
    results = run_portfolio_simulation(params_df)
    
    # Step 4: Display results
    print("\n" + "=" * 60)
    print("Simulation Results (1 Year Forward)")
    print("=" * 60)
    print(f"Expected Portfolio Return: {results['mean_return']*100:.2f}%")
    print(f"Standard Deviation: {results['std_return']*100:.2f}%")
    print(f"95% VaR (worst 5% outcomes): {results['var_95']*100:.2f}%")
    print(f"99% VaR (worst 1% outcomes): {results['var_99']*100:.2f}%")
    
    # Percentile distribution
    print("\nReturn Distribution (percentiles):")
    percentiles = [1, 5, 10, 25, 50, 75, 90, 95, 99]
    for p in percentiles:
        value = np.percentile(results["final_values"], p) - 1
        print(f"  {p:2d}th percentile: {value*100:+.2f}%")
    
    print("\n" + "=" * 60)
    print("Simulation completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
