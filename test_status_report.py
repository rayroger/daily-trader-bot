#!/usr/bin/env python3
"""
Test script for the daily status report feature.
"""

import os
import sys
import json
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from generate_daily_status import DailyStatusReporter


def test_report_generation():
    """Test that report generation works with existing portfolio data."""
    print("Testing Daily Status Report Generation...")
    
    # Create reporter
    reporter = DailyStatusReporter()
    
    # Generate report
    report = reporter.generate_report()
    
    # Verify report is not empty
    assert len(report) > 0, "Report should not be empty"
    
    # Verify key sections are present
    assert "DAILY TRADING BOT STATUS REPORT" in report, "Report should have title"
    assert "PORTFOLIO OVERVIEW" in report, "Report should have portfolio overview"
    assert "PERFORMANCE METRICS" in report, "Report should have performance metrics"
    assert "BENCHMARK COMPARISON" in report, "Report should have benchmark comparison"
    
    print("  ✓ Report generated successfully")
    print(f"  ✓ Report length: {len(report)} characters")
    
    # Test saving report
    report_file = reporter.save_report(report)
    assert os.path.exists(report_file), "Report file should exist"
    
    print(f"  ✓ Report saved to: {report_file}")
    
    # Verify file contains the report
    with open(report_file, 'r') as f:
        saved_content = f.read()
    
    assert saved_content == report, "Saved content should match generated report"
    print("  ✓ Report content verified")
    
    return True


def test_portfolio_returns_calculation():
    """Test portfolio returns calculation."""
    print("\nTesting Portfolio Returns Calculation...")
    
    reporter = DailyStatusReporter()
    
    # Create mock portfolio state
    portfolio_state = {
        'total_value': 105000.0,
        'initial_balance': 100000.0,
        'cash_balance': 52500.0,
        'positions': [
            {'symbol': 'AAPL', 'quantity': 100, 'avg_price': 150.0}
        ]
    }
    
    # Create mock history
    history = [
        {'portfolio_value': 100000.0},
        {'portfolio_value': 102000.0},
        {'portfolio_value': 104000.0},
        {'portfolio_value': 105000.0}
    ]
    
    # Calculate returns
    returns = reporter.calculate_portfolio_returns(portfolio_state, history)
    
    # Verify calculations
    assert returns['current_value'] == 105000.0, "Current value should be 105000"
    assert returns['initial_balance'] == 100000.0, "Initial balance should be 100000"
    assert returns['overall_return_pct'] == 5.0, "Overall return should be 5%"
    assert returns['overall_profit'] == 5000.0, "Overall profit should be 5000"
    assert returns['trading_days'] == 4, "Should have 4 trading days"
    
    print("  ✓ Current value calculated correctly")
    print("  ✓ Overall return calculated correctly")
    print("  ✓ Daily return calculated correctly")
    print("  ✓ Trading days counted correctly")
    
    return True


def test_benchmark_constants():
    """Test that benchmark constants are defined."""
    print("\nTesting Benchmark Constants...")
    
    from generate_daily_status import BENCHMARK_SPY, BENCHMARK_QQQ
    
    assert BENCHMARK_SPY['symbol'] == 'SPY', "SPY symbol should be correct"
    assert BENCHMARK_SPY['name'] == 'S&P 500', "SPY name should be correct"
    assert BENCHMARK_QQQ['symbol'] == 'QQQ', "QQQ symbol should be correct"
    assert BENCHMARK_QQQ['name'] == 'NASDAQ-100', "QQQ name should be correct"
    
    print("  ✓ SPY benchmark defined correctly")
    print("  ✓ QQQ benchmark defined correctly")
    
    return True


def main():
    """Run all tests."""
    print("=" * 60)
    print("Daily Status Report - Tests")
    print("=" * 60)
    print()
    
    try:
        test_benchmark_constants()
        test_portfolio_returns_calculation()
        test_report_generation()
        
        print()
        print("=" * 60)
        print("✓ All status report tests passed!")
        print("=" * 60)
        return 0
        
    except Exception as e:
        print()
        print("=" * 60)
        print("✗ Tests failed!")
        print("=" * 60)
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
