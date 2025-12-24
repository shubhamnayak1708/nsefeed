"""
Comprehensive Test Script for nsefeed Package

This script tests all major functionalities of nsefeed to ensure the package works correctly.
Run this in a fresh Python environment after installing nsefeed.

Usage:
    pip install nsefeed
    python test_nsefeed_functionality.py
"""

import sys
from datetime import datetime

def print_header(text):
    """Print a section header."""
    print(f"\n{'='*80}")
    print(f"  {text}")
    print(f"{'='*80}\n")

def print_success(text):
    """Print success message."""
    print(f"✓ {text}")

def print_info(text):
    """Print info message."""
    print(f"  {text}")

def print_warning(text):
    """Print warning message."""
    print(f"⚠ {text}")

def print_error(text):
    """Print error message."""
    print(f"✗ {text}")


def test_basic_import():
    """Test 1: Basic Package Import"""
    print_header("Test 1: Basic Package Import")

    try:
        import nsefeed as nf
        print_success("Package imported successfully")
        print_info(f"Version: {nf.__version__}")
        print_info(f"Author: {nf.__author__}")
        print_info(f"License: {nf.__license__}")
        return True
    except Exception as e:
        print_error(f"Failed to import nsefeed: {e}")
        return False


def test_ticker_api():
    """Test 2: Ticker API (Core Functionality)"""
    print_header("Test 2: Ticker API - Historical Data")

    try:
        import nsefeed as nf

        # Test Ticker creation
        ticker = nf.Ticker("RELIANCE")
        print_success(f"Created Ticker object for: {ticker.symbol}")

        # Test history method with different periods
        print_info("Fetching 5 days of historical data...")
        df = ticker.history(period="5d")

        if df.empty:
            print_warning("DataFrame is empty (market might be closed or data unavailable)")
            return False

        print_success(f"Retrieved {len(df)} days of data")
        print_info(f"Columns: {list(df.columns)}")
        print_info(f"Date range: {df.index[0]} to {df.index[-1]}")
        print_info(f"Sample data:\n{df.head(2)}")

        return True

    except Exception as e:
        print_error(f"Ticker API failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_download_multiple_tickers():
    """Test 3: Download Multiple Tickers"""
    print_header("Test 3: Download Multiple Tickers")

    try:
        import nsefeed as nf

        symbols = ["TCS", "INFY", "WIPRO"]
        print_info(f"Downloading data for: {', '.join(symbols)}")

        data = nf.download(symbols, period="5d")

        print_success(f"Downloaded data for {len(data)} symbols")

        for symbol, df in data.items():
            if not df.empty:
                print_info(f"{symbol}: {len(df)} days")
            else:
                print_warning(f"{symbol}: No data available")

        return True

    except Exception as e:
        print_error(f"Download failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_indices_module():
    """Test 4: Indices Module (Working Functions)"""
    print_header("Test 4: Indices Module - Working Functions")

    try:
        import nsefeed as nf

        # Test 4.1: index_list
        print_info("Test 4.1: Getting list of indices...")
        indices = nf.indices.index_list("BroadMarketIndices")
        print_success(f"Found {len(indices)} broad market indices")
        print_info(f"Sample: {indices[:5]}")

        # Test 4.2: constituent_stock_list
        print_info("\nTest 4.2: Getting NIFTY 50 constituents...")
        stocks = nf.indices.constituent_stock_list("BroadMarketIndices", "Nifty 50")
        print_success(f"Retrieved {len(stocks)} constituent stocks")
        print_info(f"Columns: {list(stocks.columns)}")
        print_info(f"Sample stocks:\n{stocks[['Symbol', 'Company Name']].head(3)}")

        return True

    except Exception as e:
        print_error(f"Indices module failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_indices_deprecated_functions():
    """Test 5: Indices Module (Deprecated Functions - Should Raise NotImplementedError)"""
    print_header("Test 5: Indices Module - Deprecated Functions (Expected to Fail)")

    try:
        import nsefeed as nf

        # Test 5.1: index_data (should raise NotImplementedError)
        print_info("Test 5.1: Trying index_data() (should raise NotImplementedError)...")
        try:
            df = nf.indices.index_data("NIFTY 50", period="1M")
            print_error("index_data() should have raised NotImplementedError!")
            return False
        except NotImplementedError as e:
            print_success("index_data() correctly raises NotImplementedError")
            print_info(f"Message: {str(e)[:100]}...")

        # Test 5.2: india_vix_data (should raise NotImplementedError)
        print_info("\nTest 5.2: Trying india_vix_data() (should raise NotImplementedError)...")
        try:
            df = nf.indices.india_vix_data(period="1M")
            print_error("india_vix_data() should have raised NotImplementedError!")
            return False
        except NotImplementedError as e:
            print_success("india_vix_data() correctly raises NotImplementedError")
            print_info(f"Message: {str(e)[:100]}...")

        return True

    except Exception as e:
        print_error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_equity_module():
    """Test 6: Equity Module"""
    print_header("Test 6: Equity Module - Price/Volume Data")

    try:
        import nsefeed as nf

        # Test price, volume, and deliverable position data
        print_info("Fetching price/volume/deliverable data for RELIANCE (5 days)...")
        df = nf.equity.get_price_volume_and_deliverable_position_data("RELIANCE", period="5d")

        if df.empty:
            print_warning("No data retrieved (market might be closed)")
            return False

        print_success(f"Retrieved {len(df)} days of equity data")
        print_info(f"Columns: {list(df.columns)}")
        print_info(f"Sample data:\n{df.head(2)}")

        return True

    except Exception as e:
        print_error(f"Equity module failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_derivatives_module():
    """Test 7: Derivatives Module"""
    print_header("Test 7: Derivatives Module - Futures Data")

    try:
        import nsefeed as nf

        print_info("Fetching futures data for NIFTY (5 days)...")
        df = nf.derivatives.get_future_price_volume_data("NIFTY", "FUTIDX", period="5d")

        if df.empty:
            print_warning("No futures data retrieved")
            return False

        print_success(f"Retrieved {len(df)} days of futures data")
        print_info(f"Columns: {list(df.columns)}")
        print_info(f"Instruments: {df['INSTRUMENT'].unique()[:5]}")

        return True

    except Exception as e:
        print_error(f"Derivatives module failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_error_handling():
    """Test 8: Error Handling"""
    print_header("Test 8: Error Handling")

    try:
        import nsefeed as nf
        from nsefeed.exceptions import NSEInvalidSymbolError, NSEDataNotFoundError

        # Test 8.1: Invalid symbol
        print_info("Test 8.1: Testing invalid symbol handling...")
        try:
            ticker = nf.Ticker("INVALID_SYMBOL_XYZ")
            df = ticker.history(period="5d")
            # May return empty DataFrame or raise error
            if df.empty:
                print_success("Invalid symbol handled gracefully (empty DataFrame)")
            else:
                print_warning("Invalid symbol returned data (unexpected)")
        except Exception as e:
            print_success(f"Invalid symbol raised exception: {type(e).__name__}")

        # Test 8.2: Invalid index category
        print_info("\nTest 8.2: Testing invalid index category...")
        try:
            indices = nf.indices.index_list("InvalidCategory")
            print_error("Should have raised ValueError for invalid category")
            return False
        except ValueError as e:
            print_success("Invalid index category correctly raises ValueError")
            print_info(f"Message: {str(e)[:80]}...")

        return True

    except Exception as e:
        print_error(f"Error handling test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_session_management():
    """Test 9: Session Management"""
    print_header("Test 9: Session Management")

    try:
        import nsefeed as nf
        from nsefeed.session import NSESession

        # Test singleton pattern
        session1 = NSESession.get_instance()
        session2 = NSESession.get_instance()

        if session1 is session2:
            print_success("NSESession singleton pattern working correctly")
        else:
            print_error("NSESession singleton pattern not working!")
            return False

        # Test session methods exist
        print_info("Checking session methods...")
        assert hasattr(session1, 'get'), "Session missing get() method"
        assert hasattr(session1, 'post'), "Session missing post() method"
        print_success("Session has required methods (get, post)")

        return True

    except Exception as e:
        print_error(f"Session management test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_cache_functionality():
    """Test 10: Cache Functionality"""
    print_header("Test 10: Cache Functionality")

    try:
        import nsefeed as nf
        from nsefeed.cache import NSECache

        # Test cache instance
        cache = NSECache()
        print_success("Cache instance created")

        # Test clear_cache function
        nf.clear_cache()
        print_success("clear_cache() function works")

        return True

    except Exception as e:
        print_error(f"Cache test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all tests and print summary."""
    print("\n" + "="*80)
    print("  NSEFEED COMPREHENSIVE FUNCTIONALITY TEST")
    print("="*80)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    tests = [
        ("Basic Import", test_basic_import),
        ("Ticker API", test_ticker_api),
        ("Multiple Tickers Download", test_download_multiple_tickers),
        ("Indices Module (Working)", test_indices_module),
        ("Indices Module (Deprecated)", test_indices_deprecated_functions),
        ("Equity Module", test_equity_module),
        ("Derivatives Module", test_derivatives_module),
        ("Error Handling", test_error_handling),
        ("Session Management", test_session_management),
        ("Cache Functionality", test_cache_functionality),
    ]

    results = []

    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print_error(f"Test '{test_name}' crashed: {e}")
            results.append((test_name, False))

    # Print summary
    print_header("TEST SUMMARY")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        symbol = "✓" if result else "✗"
        print(f"{symbol} {test_name:.<50} {status}")

    print(f"\n{'='*80}")
    print(f"Results: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    print(f"Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*80}\n")

    if passed == total:
        print("🎉 All tests passed! nsefeed is working correctly.")
        return 0
    else:
        print(f"⚠️  {total - passed} test(s) failed. Review the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
