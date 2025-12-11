"""
Simple test script to verify the bot's structure and basic functionality.

This script tests the bot without requiring external API calls.
"""

from daily_trader_bot.bot import TradingBot
from daily_trader_bot.utils.config import Config
from daily_trader_bot.brokers.paper_trading import PaperTradingBroker
import logging

# Set up minimal logging
logging.basicConfig(level=logging.WARNING)


def test_configuration():
    """Test configuration management."""
    print("Testing Configuration...")
    config = Config()
    
    # Test default values
    assert config.get('broker.type') == 'paper_trading'
    assert config.get('broker.initial_balance') == 100000.0
    
    # Test setting values
    config.set('broker.initial_balance', 50000.0)
    assert config.get('broker.initial_balance') == 50000.0
    
    print("✓ Configuration tests passed")


def test_paper_broker():
    """Test paper trading broker."""
    print("\nTesting Paper Trading Broker...")
    
    config = {
        'initial_balance': 10000.0
    }
    broker = PaperTradingBroker(config)
    
    # Test connection
    assert broker.connect()
    assert broker.connected
    
    # Test balance
    balance = broker.get_account_balance()
    assert balance == 10000.0
    print(f"  Initial balance: ${balance:,.2f}")
    
    # Test placing a buy order
    order = broker.place_order(
        symbol='AAPL',
        quantity=10,
        order_type='market',
        side='buy',
        price=150.0
    )
    
    assert order['status'] == 'filled'
    print(f"  ✓ Buy order placed: {order['symbol']} x{order['quantity']} @ ${order['price']}")
    
    # Check balance after purchase
    new_balance = broker.get_account_balance()
    expected_balance = 10000.0 - (150.0 * 10)
    assert abs(new_balance - expected_balance) < 0.01
    print(f"  New balance: ${new_balance:,.2f}")
    
    # Check positions
    positions = broker.get_positions()
    assert len(positions) == 1
    assert positions[0]['symbol'] == 'AAPL'
    assert positions[0]['quantity'] == 10
    print(f"  ✓ Position created: {positions[0]}")
    
    # Test selling
    sell_order = broker.place_order(
        symbol='AAPL',
        quantity=5,
        order_type='market',
        side='sell',
        price=155.0
    )
    
    assert sell_order['status'] == 'filled'
    print(f"  ✓ Sell order placed: {sell_order['symbol']} x{sell_order['quantity']} @ ${sell_order['price']}")
    
    # Check updated position
    positions = broker.get_positions()
    assert positions[0]['quantity'] == 5
    print(f"  ✓ Position updated: {positions[0]['quantity']} shares remaining")
    
    # Calculate portfolio value
    current_prices = {'AAPL': 155.0}
    portfolio_value = broker.get_portfolio_value(current_prices)
    print(f"  Total portfolio value: ${portfolio_value:,.2f}")
    
    # Profit/Loss calculation
    profit = portfolio_value - 10000.0
    print(f"  Profit/Loss: ${profit:,.2f} ({(profit/10000.0)*100:.2f}%)")
    
    broker.disconnect()
    assert not broker.connected
    
    print("✓ Paper broker tests passed")


def test_bot_initialization():
    """Test bot initialization."""
    print("\nTesting Bot Initialization...")
    
    config = Config()
    bot = TradingBot(config)
    
    # Test components are initialized
    assert bot.broker is not None
    assert bot.data_source is not None
    assert bot.price_predictor is not None
    assert bot.strategy is not None
    
    print("  ✓ All components initialized")
    
    # Test connection
    bot.connect()
    assert bot.broker.connected
    print("  ✓ Connected to broker")
    
    # Test portfolio status
    portfolio = bot.get_portfolio_status()
    assert 'cash_balance' in portfolio
    assert 'total_value' in portfolio
    print(f"  ✓ Portfolio status retrieved: ${portfolio['total_value']:,.2f}")
    
    bot.disconnect()
    
    print("✓ Bot initialization tests passed")


def test_technical_indicators():
    """Test technical indicator calculations."""
    print("\nTesting Technical Indicators...")
    
    import pandas as pd
    import numpy as np
    from daily_trader_bot.strategies.daily_trend_strategy import DailyTrendStrategy
    
    # Create mock data
    dates = pd.date_range('2024-01-01', periods=100, freq='D')
    prices = 100 + np.cumsum(np.random.randn(100) * 2)
    
    data = pd.DataFrame({
        'Date': dates,
        'Open': prices * 0.99,
        'High': prices * 1.01,
        'Low': prices * 0.98,
        'Close': prices,
        'Volume': np.random.randint(1000000, 5000000, size=100)
    })
    
    # Create strategy (without requiring real data source)
    strategy = DailyTrendStrategy(
        data_source=None,
        ai_provider=None,
        price_predictor=None
    )
    
    # Calculate indicators
    indicators = strategy.calculate_technical_indicators(data)
    
    # Verify indicators exist
    assert 'sma_short' in indicators
    assert 'sma_long' in indicators
    assert 'rsi' in indicators
    assert 'macd' in indicators
    assert 'momentum' in indicators
    assert 'volatility' in indicators
    
    print(f"  ✓ Calculated {len(indicators)} technical indicators")
    print(f"    - RSI: {indicators['rsi']:.2f}")
    print(f"    - Momentum: {indicators['momentum']:.2f}%")
    print(f"    - Volatility: {indicators['volatility']:.2f}%")
    
    print("✓ Technical indicator tests passed")


def test_price_predictor_structure():
    """Test price predictor structure."""
    print("\nTesting Price Predictor...")
    
    from daily_trader_bot.models.price_predictor import PricePredictor
    
    config = {'n_estimators': 50, 'max_depth': 5}
    predictor = PricePredictor(config)
    
    assert not predictor.is_trained
    print("  ✓ Price predictor initialized")
    
    # Create mock data for training
    import pandas as pd
    import numpy as np
    
    dates = pd.date_range('2023-01-01', periods=200, freq='D')
    prices = 100 + np.cumsum(np.random.randn(200) * 2)
    
    data = pd.DataFrame({
        'Date': dates,
        'Open': prices * 0.99,
        'High': prices * 1.01,
        'Low': prices * 0.98,
        'Close': prices,
        'Volume': np.random.randint(1000000, 5000000, size=200)
    })
    
    # Train model
    results = predictor.train(data)
    
    assert predictor.is_trained
    print(f"  ✓ Model trained with R²: {results['val_r2']:.4f}")
    
    # Test prediction
    prediction = predictor.predict(data)
    
    assert 'predicted_price' in prediction
    assert 'current_price' in prediction
    assert 'predicted_change_pct' in prediction
    
    print(f"  ✓ Prediction made:")
    print(f"    - Current: ${prediction['current_price']:.2f}")
    print(f"    - Predicted: ${prediction['predicted_price']:.2f}")
    print(f"    - Expected change: {prediction['predicted_change_pct']:.2f}%")
    
    # Test feature importance
    importance = predictor.get_feature_importance()
    assert len(importance) > 0
    print(f"  ✓ Feature importance calculated ({len(importance)} features)")
    
    print("✓ Price predictor tests passed")


def main():
    """Run all tests."""
    print("=" * 60)
    print("Daily Trader Bot - Basic Tests")
    print("=" * 60)
    print()
    
    try:
        test_configuration()
        test_paper_broker()
        test_bot_initialization()
        test_technical_indicators()
        test_price_predictor_structure()
        
        print()
        print("=" * 60)
        print("✓ All tests passed successfully!")
        print("=" * 60)
        print()
        print("The bot is ready to use. To run with real data:")
        print("  python examples/basic_usage.py")
        print()
        
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
    exit(main())
