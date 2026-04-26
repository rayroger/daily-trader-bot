#!/usr/bin/env python3
"""
Daily trading bot runner for GitHub Actions.

This script:
1. Loads previous portfolio state
2. Runs analysis on configured symbols
3. Executes trades based on strategy
4. Saves updated portfolio state and history
"""

import os
import sys
from datetime import datetime
from daily_trader_bot.bot import TradingBot
from daily_trader_bot.utils.config import Config
from daily_trader_bot.utils.data_store import DataStore
import logging

# Set up logging for this module only (avoid duplicate output with TradingBot's logger)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def _parse_bool(value: str, default: bool) -> bool:
    """Parse a string into a boolean, accepting true/false/1/0/yes/no/on/off."""
    if value is None:
        return default
    v = value.strip().lower()
    if v in ("1", "true", "yes", "y", "on"):
        return True
    if v in ("0", "false", "no", "n", "off"):
        return False
    return default


def _parse_float(value: str, default: float) -> float:
    """Parse a string into a float, returning default on failure."""
    try:
        return float(value) if value is not None and str(value).strip() != "" else default
    except (ValueError, TypeError):
        return default


def main():
    """Main trading bot execution."""
    logger.info("=" * 60)
    logger.info("Daily Trading Bot - Automated Run")
    logger.info(f"Execution Time: {datetime.now().isoformat()}")
    logger.info("=" * 60)
    
    # Initialize data store
    data_store = DataStore()
    
    # Initialize configuration
    config = Config()

    # Apply env var overrides so that workflow_dispatch inputs and repo variables
    # are honoured at runtime.  Each override is a no-op when the variable is
    # absent or empty, so default behaviour is preserved.
    symbols_override = os.environ.get("SYMBOLS", "").strip()
    if symbols_override:
        config.set("trading.symbols", symbols_override)

    exec_override = os.environ.get("EXECUTE_TRADES")
    if exec_override is not None and exec_override.strip() != "":
        config.set("trading.auto_execute", _parse_bool(exec_override, True))

    min_conf_raw = os.environ.get("MIN_CONFIDENCE")
    if min_conf_raw is not None and min_conf_raw.strip() != "":
        config.set("strategy.min_confidence", _parse_float(min_conf_raw, 0.6))

    vol_thr_raw = os.environ.get("VOLUME_THRESHOLD")
    if vol_thr_raw is not None and vol_thr_raw.strip() != "":
        config.set("strategy.volume_threshold", _parse_float(vol_thr_raw, 1.5))

    debug_raw = os.environ.get("DEBUG_STRATEGY")
    if debug_raw is not None and debug_raw.strip() != "":
        config.set("strategy.debug", _parse_bool(debug_raw, False))
    
    # Check if portfolio exists, otherwise initialize
    portfolio_state = data_store.load_portfolio_state()
    
    if portfolio_state is None:
        logger.info("No existing portfolio found. Initializing new portfolio...")
        initial_balance = config.get('broker.initial_balance', 100000.0)
        data_store.initialize_portfolio(initial_balance)
        portfolio_state = data_store.load_portfolio_state()
        logger.info(f"Portfolio initialized with ${initial_balance:,.2f}")
    else:
        logger.info(f"Loaded existing portfolio: ${portfolio_state['cash_balance']:,.2f} cash")
    
    # Initialize bot
    logger.info("Initializing trading bot...")
    bot = TradingBot(config)
    
    # Load broker state if exists
    if portfolio_state:
        broker_state = {
            'balance': portfolio_state.get('cash_balance', config.get('broker.initial_balance')),
            'initial_balance': portfolio_state.get('initial_balance', config.get('broker.initial_balance')),
            'positions': {
                pos['symbol']: {
                    'quantity': pos['quantity'],
                    'avg_price': pos['avg_price'],
                    'total_cost': pos['total_cost']
                }
                for pos in portfolio_state.get('positions', [])
            },
            'order_history': []
        }
        bot.broker.load_state(broker_state)
        logger.info(f"Loaded {len(broker_state['positions'])} existing positions")
    
    # Connect to broker
    bot.connect()
    
    # Get symbols to analyze from config or use defaults
    symbols_str = config.get('trading.symbols', 'AAPL,MSFT,GOOGL,AMZN,TSLA')
    symbols = [s.strip() for s in (symbols_str or '').split(',') if s.strip()]
    
    if not symbols:
        logger.error("No valid symbols to analyze. Please configure trading.symbols")
        return 1
    
    logger.info(f"Analyzing symbols: {', '.join(symbols)}")
    
    # Run trading session
    try:
        # Determine if we should execute trades
        execute_trades = config.get('trading.auto_execute', True)
        logger.info(f"Auto-execute trades: {execute_trades}")
        
        session_results = bot.run_trading_session(
            symbols=symbols,
            execute_trades=execute_trades
        )
        
        logger.info("Trading session completed")
        logger.info(f"Symbols analyzed: {session_results['symbols_analyzed']}")
        logger.info(f"Orders placed: {len(session_results['orders'])}")
        
        # Log signals
        for signal in session_results['signals']:
            logger.info(
                f"  {signal['symbol']}: {signal['action'].upper()} "
                f"(confidence: {signal['confidence']:.2%}) @ ${signal['current_price']:.2f}"
            )
        
        # Log orders
        for order in session_results['orders']:
            logger.info(
                f"  ORDER: {(order.get('side') or 'unknown').upper()} {order.get('quantity', '?')} {order.get('symbol', '?')} "
                f"@ ${order.get('price', 0):.2f} - {order.get('status', 'unknown')}"
            )
        
        # Get updated portfolio status
        portfolio_status = bot.get_portfolio_status()
        
        logger.info("=" * 60)
        logger.info("Portfolio Status:")
        logger.info(f"  Cash Balance: ${portfolio_status['cash_balance']:,.2f}")
        logger.info(f"  Position Value: ${portfolio_status['position_value']:,.2f}")
        logger.info(f"  Total Value: ${portfolio_status['total_value']:,.2f}")
        logger.info(f"  Active Positions: {len(portfolio_status['positions'])}")
        
        for pos in portfolio_status['positions']:
            if 'profit_loss' in pos:
                pl_sign = '+' if pos['profit_loss'] >= 0 else ''
                logger.info(
                    f"    {pos['symbol']}: {pos['quantity']} shares @ ${pos['avg_price']:.2f} "
                    f"(P/L: {pl_sign}${pos['profit_loss']:.2f} / {pl_sign}{pos['profit_loss_pct']:.2f}%)"
                )
            else:
                logger.info(f"    {pos['symbol']}: {pos['quantity']} shares @ ${pos['avg_price']:.2f}")
        
        # Save portfolio state
        new_state = {
            'cash_balance': portfolio_status['cash_balance'],
            'positions': portfolio_status['positions'],
            'total_value': portfolio_status['total_value'],
            'initial_balance': bot.broker.initial_balance
        }
        data_store.save_portfolio_state(new_state)
        logger.info("Portfolio state saved")
        
        # Save trading history
        history_entry = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'symbols_analyzed': session_results['symbols_analyzed'],
            'signals': [
                {
                    'symbol': s['symbol'],
                    'action': s['action'],
                    'confidence': s['confidence'],
                    'current_price': s['current_price']
                }
                for s in session_results['signals']
            ],
            'orders': [
                {
                    'symbol': o['symbol'],
                    'side': o['side'],
                    'quantity': o['quantity'],
                    'price': o['price'],
                    'status': o['status']
                }
                for o in session_results['orders']
            ],
            'portfolio_value': portfolio_status['total_value'],
            'cash_balance': portfolio_status['cash_balance']
        }
        data_store.append_trading_history(history_entry)
        logger.info("Trading history saved")
        
        # Save daily analysis
        date_str = datetime.now().strftime('%Y-%m-%d')
        analysis_data = {
            'date': date_str,
            'session': session_results,
            'portfolio': portfolio_status
        }
        data_store.save_daily_analysis(date_str, analysis_data)
        logger.info(f"Daily analysis saved to analysis_{date_str}.json")
        
        # Print summary
        summary = data_store.get_portfolio_summary()
        logger.info("=" * 60)
        logger.info("Overall Summary:")
        logger.info(f"  Total Trading Days: {summary['trading_days']}")
        logger.info(f"  Total Trades: {summary['total_trades']}")
        logger.info(f"  Current Value: ${summary['total_value']:,.2f}")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"Error during trading session: {e}", exc_info=True)
        return 1
    
    finally:
        bot.disconnect()
    
    logger.info("Daily trading bot run completed successfully")
    return 0


if __name__ == "__main__":
    sys.exit(main())
