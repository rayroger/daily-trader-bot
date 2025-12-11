"""
Example script demonstrating how to use the Daily Trader Bot.

This script shows basic usage including:
- Initializing the bot
- Analyzing stocks
- Training prediction models
- Running trading sessions
"""

from daily_trader_bot.bot import TradingBot
from daily_trader_bot.utils.config import Config
from datetime import datetime
import json


def main():
    """Main example function."""
    print("=" * 60)
    print("Daily Trader Bot - Example Usage")
    print("=" * 60)
    print()
    
    # Initialize configuration
    config = Config()
    
    # You can customize configuration
    config.set('broker.initial_balance', 50000.0)
    config.set('strategy.min_confidence', 0.65)
    
    # Initialize bot
    print("Initializing trading bot...")
    bot = TradingBot(config)
    
    # Connect to broker
    bot.connect()
    print()
    
    # Define symbols to analyze
    symbols = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'AMZN']
    print(f"Symbols to analyze: {', '.join(symbols)}")
    print()
    
    # Example 1: Analyze a single symbol
    print("-" * 60)
    print("Example 1: Analyzing AAPL")
    print("-" * 60)
    
    signal = bot.analyze_symbol('AAPL')
    
    print(f"Symbol: {signal['symbol']}")
    print(f"Action: {signal['action'].upper()}")
    print(f"Confidence: {signal['confidence']:.2%}")
    print(f"Current Price: ${signal['current_price']:.2f}")
    
    if signal['stop_loss']:
        print(f"Stop Loss: ${signal['stop_loss']:.2f}")
    if signal['take_profit']:
        print(f"Take Profit: ${signal['take_profit']:.2f}")
    
    print("\nReasoning:")
    for reason in signal['reasoning']:
        print(f"  - {reason}")
    print()
    
    # Example 2: Train prediction model
    print("-" * 60)
    print("Example 2: Training price prediction model for MSFT")
    print("-" * 60)
    
    try:
        training_results = bot.train_model('MSFT', lookback_days=180)
        print(f"Training Results:")
        print(f"  - Validation R²: {training_results['val_r2']:.4f}")
        print(f"  - Validation RMSE: ${training_results['val_rmse']:.2f}")
        print(f"  - Number of features: {training_results['n_features']}")
        print(f"  - Training samples: {training_results['n_samples']}")
        
        # Now analyze with trained model
        signal_with_prediction = bot.analyze_symbol('MSFT')
        
        if signal_with_prediction.get('analysis', {}).get('price_prediction'):
            pred = signal_with_prediction['analysis']['price_prediction']
            print(f"\nPrice Prediction:")
            print(f"  - Current Price: ${pred['current_price']:.2f}")
            print(f"  - Predicted Price: ${pred['predicted_price']:.2f}")
            print(f"  - Expected Change: {pred['predicted_change_pct']:.2f}%")
        print()
    except Exception as e:
        print(f"Could not train model: {e}")
        print("(This is expected if scikit-learn is not installed)")
        print()
    
    # Example 3: Run analysis on multiple symbols
    print("-" * 60)
    print("Example 3: Analyzing multiple symbols")
    print("-" * 60)
    
    signals = bot.run_analysis(symbols)
    
    print(f"\n{'Symbol':<10} {'Action':<10} {'Confidence':<12} {'Price':<10}")
    print("-" * 45)
    
    for sig in signals:
        print(
            f"{sig['symbol']:<10} "
            f"{sig['action'].upper():<10} "
            f"{sig['confidence']:.2%}     "
            f"${sig['current_price']:>8.2f}"
        )
    print()
    
    # Example 4: Run trading session (without executing)
    print("-" * 60)
    print("Example 4: Running trading session (analysis only)")
    print("-" * 60)
    
    session_results = bot.run_trading_session(
        symbols=['AAPL', 'MSFT', 'GOOGL'],
        execute_trades=False
    )
    
    print(f"Session completed at {session_results['timestamp']}")
    print(f"Symbols analyzed: {session_results['symbols_analyzed']}")
    print(f"Signals generated: {len(session_results['signals'])}")
    print()
    
    buy_signals = [s for s in session_results['signals'] if s['action'] == 'buy']
    sell_signals = [s for s in session_results['signals'] if s['action'] == 'sell']
    
    print(f"Buy signals: {len(buy_signals)}")
    for sig in buy_signals:
        print(f"  - {sig['symbol']} @ ${sig['current_price']:.2f} (confidence: {sig['confidence']:.2%})")
    
    print(f"\nSell signals: {len(sell_signals)}")
    for sig in sell_signals:
        print(f"  - {sig['symbol']} @ ${sig['current_price']:.2f} (confidence: {sig['confidence']:.2%})")
    print()
    
    # Example 5: Get portfolio status
    print("-" * 60)
    print("Example 5: Portfolio Status")
    print("-" * 60)
    
    portfolio = bot.get_portfolio_status()
    
    print(f"Cash Balance: ${portfolio['cash_balance']:,.2f}")
    print(f"Position Value: ${portfolio['position_value']:,.2f}")
    print(f"Total Portfolio Value: ${portfolio['total_value']:,.2f}")
    print(f"Number of Positions: {len(portfolio['positions'])}")
    print()
    
    # Example 6: Execute a trade (paper trading)
    print("-" * 60)
    print("Example 6: Executing a paper trade")
    print("-" * 60)
    
    # Find a buy signal
    buy_signal = next((s for s in signals if s['action'] == 'buy'), None)
    
    if buy_signal:
        print(f"Executing BUY signal for {buy_signal['symbol']}...")
        order = bot.execute_signal(buy_signal, quantity=5)
        
        if order and order.get('status') == 'filled':
            print(f"✓ Order filled successfully!")
            print(f"  - Symbol: {order['symbol']}")
            print(f"  - Quantity: {order['quantity']}")
            print(f"  - Price: ${order['price']:.2f}")
            print(f"  - Total Cost: ${order['price'] * order['quantity']:.2f}")
        else:
            print(f"✗ Order not filled: {order}")
    else:
        print("No buy signals found in this session")
    print()
    
    # Show updated portfolio
    portfolio = bot.get_portfolio_status()
    print("Updated Portfolio:")
    print(f"Cash Balance: ${portfolio['cash_balance']:,.2f}")
    print(f"Total Portfolio Value: ${portfolio['total_value']:,.2f}")
    
    if portfolio['positions']:
        print("\nCurrent Positions:")
        for pos in portfolio['positions']:
            print(f"  - {pos['symbol']}: {pos['quantity']} shares @ ${pos['avg_price']:.2f}")
            if 'profit_loss' in pos:
                pl_sign = '+' if pos['profit_loss'] >= 0 else ''
                print(f"    P/L: {pl_sign}${pos['profit_loss']:.2f} ({pl_sign}{pos['profit_loss_pct']:.2f}%)")
    print()
    
    # Disconnect
    bot.disconnect()
    
    print("=" * 60)
    print("Example completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
