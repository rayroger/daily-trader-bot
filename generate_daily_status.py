#!/usr/bin/env python3
"""
Daily status report generator for the trading bot.

This script:
1. Loads current portfolio state
2. Fetches benchmark performance (SPY and QQQ)
3. Calculates portfolio returns and metrics
4. Compares performance against benchmarks
5. Generates and saves a formatted status report
"""

import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

from daily_trader_bot.utils.config import Config
from daily_trader_bot.utils.data_store import DataStore
from daily_trader_bot.data_sources.yahoo_finance import YahooFinanceDataSource

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DailyStatusReporter:
    """Generate daily status reports for the trading bot portfolio."""
    
    def __init__(self):
        """Initialize the status reporter."""
        self.data_store = DataStore()
        self.config = Config()
        self.data_source = YahooFinanceDataSource({})
        
    def get_benchmark_performance(self, symbol: str, days: int = 1) -> Optional[Dict]:
        """
        Get benchmark performance over specified period.
        
        Args:
            symbol: Benchmark symbol (e.g., 'SPY', 'QQQ')
            days: Number of days to look back
            
        Returns:
            Dictionary with performance metrics or None if unavailable
        """
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days + 5)  # Extra days for market closures
            
            data = self.data_source.get_historical_data(
                symbol=symbol,
                start_date=start_date,
                end_date=end_date,
                interval='1d'
            )
            
            if len(data) < 2:
                logger.warning(f"Insufficient data for {symbol}")
                return None
            
            # Get the most recent and previous close
            current_price = float(data['Close'].iloc[-1])
            
            # For daily return, use previous day
            if len(data) >= 2:
                prev_price_1d = float(data['Close'].iloc[-2])
                daily_return = ((current_price - prev_price_1d) / prev_price_1d) * 100
            else:
                daily_return = 0.0
            
            # For longer periods, calculate from N days ago
            if len(data) > days:
                prev_price_period = float(data['Close'].iloc[-(days + 1)])
                period_return = ((current_price - prev_price_period) / prev_price_period) * 100
            else:
                period_return = daily_return
            
            return {
                'symbol': symbol,
                'current_price': current_price,
                'daily_return': daily_return,
                'period_return': period_return,
                'days': days
            }
            
        except Exception as e:
            logger.error(f"Error fetching benchmark data for {symbol}: {e}")
            return None
    
    def calculate_portfolio_returns(self, portfolio_state: Dict, history: List[Dict]) -> Dict:
        """
        Calculate portfolio returns over various periods.
        
        Args:
            portfolio_state: Current portfolio state
            history: Trading history entries
            
        Returns:
            Dictionary with return metrics
        """
        current_value = portfolio_state.get('total_value', 0)
        initial_balance = portfolio_state.get('initial_balance', 100000.0)
        
        # Overall return since inception
        overall_return = ((current_value - initial_balance) / initial_balance) * 100
        overall_profit = current_value - initial_balance
        
        # Daily return (from most recent history entry if available)
        daily_return = 0.0
        daily_profit = 0.0
        if len(history) > 0:
            last_entry = history[-1]
            last_value = last_entry.get('portfolio_value', current_value)
            if len(history) > 1:
                prev_value = history[-2].get('portfolio_value', initial_balance)
                daily_return = ((last_value - prev_value) / prev_value) * 100
                daily_profit = last_value - prev_value
        
        # Calculate returns for different periods
        returns = {
            'current_value': current_value,
            'initial_balance': initial_balance,
            'overall_return_pct': overall_return,
            'overall_profit': overall_profit,
            'daily_return_pct': daily_return,
            'daily_profit': daily_profit,
            'trading_days': len(history)
        }
        
        # Calculate period returns if we have enough history
        if len(history) >= 7:
            week_ago_value = history[-7].get('portfolio_value', initial_balance)
            weekly_return = ((current_value - week_ago_value) / week_ago_value) * 100
            returns['weekly_return_pct'] = weekly_return
            returns['weekly_profit'] = current_value - week_ago_value
        
        if len(history) >= 30:
            month_ago_value = history[-30].get('portfolio_value', initial_balance)
            monthly_return = ((current_value - month_ago_value) / month_ago_value) * 100
            returns['monthly_return_pct'] = monthly_return
            returns['monthly_profit'] = current_value - month_ago_value
        
        return returns
    
    def generate_report(self) -> str:
        """
        Generate a formatted daily status report.
        
        Returns:
            Formatted report as a string
        """
        logger.info("Generating daily status report...")
        
        # Load portfolio data
        portfolio_state = self.data_store.load_portfolio_state()
        if not portfolio_state:
            return "❌ No portfolio data available. Initialize the bot first."
        
        history = self.data_store.get_trading_history()
        
        # Calculate portfolio returns
        returns = self.calculate_portfolio_returns(portfolio_state, history)
        
        # Get benchmark performance
        spy_perf = self.get_benchmark_performance('SPY', days=1)
        qqq_perf = self.get_benchmark_performance('QQQ', days=1)  # NASDAQ-100 ETF
        
        # Build report
        report_lines = []
        report_lines.append("=" * 70)
        report_lines.append("📊 DAILY TRADING BOT STATUS REPORT")
        report_lines.append("=" * 70)
        report_lines.append(f"Report Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("")
        
        # Portfolio Overview
        report_lines.append("💼 PORTFOLIO OVERVIEW")
        report_lines.append("-" * 70)
        report_lines.append(f"Initial Balance:        ${returns['initial_balance']:>15,.2f}")
        report_lines.append(f"Current Value:          ${returns['current_value']:>15,.2f}")
        report_lines.append(f"Cash Balance:           ${portfolio_state.get('cash_balance', 0):>15,.2f}")
        
        position_value = returns['current_value'] - portfolio_state.get('cash_balance', 0)
        report_lines.append(f"Position Value:         ${position_value:>15,.2f}")
        report_lines.append(f"Active Positions:       {len(portfolio_state.get('positions', [])):>15}")
        report_lines.append(f"Trading Days:           {returns['trading_days']:>15}")
        report_lines.append("")
        
        # Performance Metrics
        report_lines.append("📈 PERFORMANCE METRICS")
        report_lines.append("-" * 70)
        
        # Overall performance
        profit_sign = "+" if returns['overall_profit'] >= 0 else ""
        report_lines.append(f"Overall Return:         {profit_sign}{returns['overall_return_pct']:>14.2f}%")
        report_lines.append(f"Overall Profit/Loss:    {profit_sign}${returns['overall_profit']:>13,.2f}")
        report_lines.append("")
        
        # Daily performance
        daily_sign = "+" if returns['daily_profit'] >= 0 else ""
        report_lines.append(f"Daily Return:           {daily_sign}{returns['daily_return_pct']:>14.2f}%")
        report_lines.append(f"Daily Profit/Loss:      {daily_sign}${returns['daily_profit']:>13,.2f}")
        
        # Weekly/Monthly if available
        if 'weekly_return_pct' in returns:
            weekly_sign = "+" if returns['weekly_profit'] >= 0 else ""
            report_lines.append(f"Weekly Return (7d):     {weekly_sign}{returns['weekly_return_pct']:>14.2f}%")
            report_lines.append(f"Weekly Profit/Loss:     {weekly_sign}${returns['weekly_profit']:>13,.2f}")
        
        if 'monthly_return_pct' in returns:
            monthly_sign = "+" if returns['monthly_profit'] >= 0 else ""
            report_lines.append(f"Monthly Return (30d):   {monthly_sign}{returns['monthly_return_pct']:>14.2f}%")
            report_lines.append(f"Monthly Profit/Loss:    {monthly_sign}${returns['monthly_profit']:>13,.2f}")
        
        report_lines.append("")
        
        # Benchmark Comparison
        report_lines.append("📊 BENCHMARK COMPARISON")
        report_lines.append("-" * 70)
        
        if spy_perf:
            spy_sign = "+" if spy_perf['daily_return'] >= 0 else ""
            report_lines.append(f"SPY (S&P 500):")
            report_lines.append(f"  Daily Return:         {spy_sign}{spy_perf['daily_return']:>14.2f}%")
            report_lines.append(f"  Current Price:        ${spy_perf['current_price']:>15,.2f}")
            
            # Compare to portfolio
            if returns['trading_days'] > 0:
                vs_spy = returns['daily_return_pct'] - spy_perf['daily_return']
                vs_spy_sign = "+" if vs_spy >= 0 else ""
                report_lines.append(f"  vs. Portfolio:        {vs_spy_sign}{vs_spy:>14.2f}% {'📈' if vs_spy > 0 else '📉' if vs_spy < 0 else '➡️'}")
        else:
            report_lines.append("SPY (S&P 500):        Data unavailable")
        
        report_lines.append("")
        
        if qqq_perf:
            qqq_sign = "+" if qqq_perf['daily_return'] >= 0 else ""
            report_lines.append(f"QQQ (NASDAQ-100):")
            report_lines.append(f"  Daily Return:         {qqq_sign}{qqq_perf['daily_return']:>14.2f}%")
            report_lines.append(f"  Current Price:        ${qqq_perf['current_price']:>15,.2f}")
            
            # Compare to portfolio
            if returns['trading_days'] > 0:
                vs_qqq = returns['daily_return_pct'] - qqq_perf['daily_return']
                vs_qqq_sign = "+" if vs_qqq >= 0 else ""
                report_lines.append(f"  vs. Portfolio:        {vs_qqq_sign}{vs_qqq:>14.2f}% {'📈' if vs_qqq > 0 else '📉' if vs_qqq < 0 else '➡️'}")
        else:
            report_lines.append("QQQ (NASDAQ-100):     Data unavailable")
        
        report_lines.append("")
        
        # Position Details
        positions = portfolio_state.get('positions', [])
        if positions:
            report_lines.append("💰 CURRENT POSITIONS")
            report_lines.append("-" * 70)
            
            for pos in positions:
                symbol = pos['symbol']
                quantity = pos['quantity']
                avg_price = pos['avg_price']
                
                # Try to get current price
                try:
                    current_price = self.data_source.get_current_price(symbol)
                    market_value = current_price * quantity
                    cost_basis = avg_price * quantity
                    unrealized_pl = market_value - cost_basis
                    unrealized_pl_pct = (unrealized_pl / cost_basis) * 100
                    pl_sign = "+" if unrealized_pl >= 0 else ""
                    
                    report_lines.append(f"{symbol}:")
                    report_lines.append(f"  Shares:               {quantity:>15}")
                    report_lines.append(f"  Avg Price:            ${avg_price:>15,.2f}")
                    report_lines.append(f"  Current Price:        ${current_price:>15,.2f}")
                    report_lines.append(f"  Market Value:         ${market_value:>15,.2f}")
                    report_lines.append(f"  Unrealized P/L:       {pl_sign}${unrealized_pl:>13,.2f} ({pl_sign}{unrealized_pl_pct:.2f}%)")
                    
                except Exception as e:
                    logger.warning(f"Could not fetch current price for {symbol}: {e}")
                    report_lines.append(f"{symbol}:")
                    report_lines.append(f"  Shares:               {quantity:>15}")
                    report_lines.append(f"  Avg Price:            ${avg_price:>15,.2f}")
                    report_lines.append(f"  Current Price:        N/A")
                
                report_lines.append("")
        else:
            report_lines.append("💰 CURRENT POSITIONS")
            report_lines.append("-" * 70)
            report_lines.append("No active positions")
            report_lines.append("")
        
        report_lines.append("=" * 70)
        
        report = "\n".join(report_lines)
        logger.info("Daily status report generated successfully")
        
        return report
    
    def save_report(self, report: str) -> str:
        """
        Save report to file.
        
        Args:
            report: Formatted report string
            
        Returns:
            Path to saved report file
        """
        # Create reports directory if it doesn't exist
        reports_dir = os.path.join(self.data_store.data_dir, "reports")
        os.makedirs(reports_dir, exist_ok=True)
        
        # Generate filename with date
        date_str = datetime.now().strftime('%Y-%m-%d')
        report_file = os.path.join(reports_dir, f"status_report_{date_str}.txt")
        
        # Save report
        with open(report_file, 'w') as f:
            f.write(report)
        
        logger.info(f"Report saved to {report_file}")
        
        return report_file


def main():
    """Main execution function."""
    logger.info("=" * 70)
    logger.info("Daily Status Report Generator")
    logger.info("=" * 70)
    
    try:
        # Create reporter
        reporter = DailyStatusReporter()
        
        # Generate report
        report = reporter.generate_report()
        
        # Print to console
        print("\n" + report + "\n")
        
        # Save to file
        report_file = reporter.save_report(report)
        
        logger.info("=" * 70)
        logger.info("Status report completed successfully")
        logger.info(f"Report saved to: {report_file}")
        logger.info("=" * 70)
        
        return 0
        
    except Exception as e:
        logger.error(f"Error generating status report: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
