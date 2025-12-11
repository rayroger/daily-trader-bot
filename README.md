# Daily Trader Bot

A Python-based AI-assisted trading bot designed to follow daily market trends. This bot provides a flexible, extensible architecture that allows you to:

- 🏢 **Use different brokers** - Start with paper trading and easily switch to real brokers
- 📊 **Multiple data sources** - Fetch market data from Yahoo Finance, Google Finance, and more
- 🤖 **Various AI providers** - Leverage OpenAI, Anthropic, or custom AI models for market analysis
- 📈 **Price prediction** - Train and use ML models to predict stock prices
- 🎯 **Daily trend following** - Automated strategy that analyzes and trades based on daily trends

## Features

### 1. Extensible Broker Support
The bot uses abstract base classes to support multiple broker implementations:
- **Paper Trading Broker** (included) - Test strategies without real money
- **Custom Broker Interface** - Easily integrate with any broker API (Interactive Brokers, Alpaca, TD Ameritrade, etc.)

### 2. Multiple Data Source Integration
Fetch market data from various providers:
- **Yahoo Finance** (included) - Free, reliable market data
- **Custom Data Sources** - Add support for Bloomberg, Reuters, Polygon.io, IEX Cloud, etc.

### 3. AI Provider Flexibility
Leverage different AI services for market analysis:
- **OpenAI Integration** (included) - Use GPT models for sentiment analysis and insights
- **Custom AI Providers** - Integrate Anthropic Claude, Google Gemini, Azure OpenAI, or local models

### 4. Machine Learning Price Prediction
Built-in ML model for stock price prediction:
- Time series analysis with technical indicators
- Feature engineering (SMA, EMA, RSI, MACD, Bollinger Bands)
- Random Forest Regressor with confidence intervals
- Model persistence (save/load trained models)

### 5. Daily Trend Following Strategy
Sophisticated trading strategy that combines:
- Technical indicators (moving averages, RSI, MACD, Bollinger Bands)
- Volume analysis
- AI-powered market sentiment
- Price predictions
- Risk management (stop loss, take profit)

## Installation

```bash
# Clone the repository
git clone https://github.com/rayroger/daily-trader-bot.git
cd daily-trader-bot

# Install dependencies
pip install -r requirements.txt

# Optional: Set up AI provider API key
export OPENAI_API_KEY="your-api-key-here"
```

## Quick Start

### Basic Usage

```python
from daily_trader_bot.bot import TradingBot
from daily_trader_bot.utils.config import Config

# Initialize the bot with default configuration
bot = TradingBot()

# Connect to broker (paper trading by default)
bot.connect()

# Analyze a stock
signal = bot.analyze_symbol('AAPL')
print(f"Action: {signal['action']}")
print(f"Confidence: {signal['confidence']}")
print(f"Reasoning: {signal['reasoning']}")

# Get portfolio status
portfolio = bot.get_portfolio_status()
print(f"Balance: ${portfolio['cash_balance']:.2f}")
```

### Training a Price Prediction Model

```python
# Train model on historical data
training_results = bot.train_model('MSFT', lookback_days=365)
print(f"Model R²: {training_results['val_r2']:.4f}")

# Analyze with trained model
signal = bot.analyze_symbol('MSFT')
if signal['analysis']['price_prediction']:
    pred = signal['analysis']['price_prediction']
    print(f"Predicted price: ${pred['predicted_price']:.2f}")
    print(f"Expected change: {pred['predicted_change_pct']:.2f}%")
```

### Running a Trading Session

```python
# Analyze multiple stocks
symbols = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'AMZN']

# Run analysis without executing trades
session = bot.run_trading_session(symbols, execute_trades=False)

# Or execute trades automatically
session = bot.run_trading_session(symbols, execute_trades=True)

print(f"Analyzed {session['symbols_analyzed']} symbols")
print(f"Executed {len(session['orders'])} orders")
```

## Architecture

### Project Structure

```
daily-trader-bot/
├── daily_trader_bot/
│   ├── __init__.py
│   ├── bot.py                 # Main TradingBot class
│   ├── brokers/
│   │   ├── __init__.py
│   │   ├── base.py           # Abstract broker interface
│   │   └── paper_trading.py  # Paper trading implementation
│   ├── data_sources/
│   │   ├── __init__.py
│   │   ├── base.py           # Abstract data source interface
│   │   └── yahoo_finance.py  # Yahoo Finance implementation
│   ├── ai_providers/
│   │   ├── __init__.py
│   │   ├── base.py           # Abstract AI provider interface
│   │   └── openai_provider.py # OpenAI implementation
│   ├── models/
│   │   ├── __init__.py
│   │   └── price_predictor.py # ML price prediction model
│   ├── strategies/
│   │   ├── __init__.py
│   │   └── daily_trend_strategy.py # Daily trend strategy
│   └── utils/
│       ├── __init__.py
│       ├── config.py         # Configuration management
│       └── logger.py         # Logging utilities
├── examples/
│   ├── basic_usage.py        # Basic usage examples
│   └── custom_components.py  # Custom component examples
├── requirements.txt
└── README.md
```

### Extending the Bot

#### Adding a Custom Broker

```python
from daily_trader_bot.brokers.base import BaseBroker

class MyCustomBroker(BaseBroker):
    def connect(self):
        # Implement connection logic
        pass
    
    def place_order(self, symbol, quantity, order_type, side, price=None):
        # Implement order placement
        pass
    
    # Implement other required methods...

# Use in your bot
bot = TradingBot()
bot.broker = MyCustomBroker(config)
```

#### Adding a Custom Data Source

```python
from daily_trader_bot.data_sources.base import BaseDataSource

class MyCustomDataSource(BaseDataSource):
    def get_historical_data(self, symbol, start_date, end_date, interval="1d"):
        # Fetch data from your source
        pass
    
    def get_current_price(self, symbol):
        # Get current price
        pass
    
    # Implement other required methods...

# Use in your bot
bot = TradingBot()
bot.data_source = MyCustomDataSource(config)
```

#### Adding a Custom AI Provider

```python
from daily_trader_bot.ai_providers.base import BaseAIProvider

class MyCustomAIProvider(BaseAIProvider):
    def analyze_sentiment(self, text):
        # Implement sentiment analysis
        pass
    
    def generate_trading_signal(self, symbol, historical_data, technical_indicators, news_sentiment=None):
        # Generate trading signals
        pass
    
    # Implement other required methods...

# Use in your bot
bot = TradingBot()
bot.ai_provider = MyCustomAIProvider(config)
```

## Configuration

The bot uses a flexible configuration system. You can customize settings:

```python
from daily_trader_bot.utils.config import Config

config = Config()

# Broker settings
config.set('broker.type', 'paper_trading')
config.set('broker.initial_balance', 100000.0)

# Strategy settings
config.set('strategy.trend_period', 20)
config.set('strategy.min_confidence', 0.6)
config.set('strategy.stop_loss_pct', 0.05)
config.set('strategy.take_profit_pct', 0.10)

# Model settings
config.set('model.n_estimators', 100)
config.set('model.max_depth', 10)

# Save configuration
config.save_to_file('my_config.json')

# Load configuration
config = Config('my_config.json')
bot = TradingBot(config)
```

## Examples

See the `examples/` directory for detailed examples:

- **`basic_usage.py`** - Comprehensive usage examples including:
  - Analyzing individual stocks
  - Training prediction models
  - Running trading sessions
  - Portfolio management
  
- **`custom_components.py`** - Shows how to create custom:
  - Broker implementations
  - Data sources
  - AI providers

Run examples:
```bash
python examples/basic_usage.py
python examples/custom_components.py
```

## Requirements

### Core Requirements
- Python 3.8+
- pandas >= 2.0.0
- numpy >= 1.24.0
- yfinance >= 0.2.28
- scikit-learn >= 1.3.0

### Optional Requirements
- openai >= 1.0.0 (for AI-powered analysis)

## Disclaimer

⚠️ **IMPORTANT DISCLAIMER**

This software is for educational and research purposes only. It is NOT intended for live trading with real money without proper testing, risk management, and understanding of the markets.

- **No Warranty**: This software comes with no warranty or guarantee of profitability
- **Risk**: Trading stocks involves substantial risk of loss
- **Not Financial Advice**: This bot does not provide financial advice
- **Test First**: Always test with paper trading before considering real money
- **Your Responsibility**: You are solely responsible for any trading decisions and losses

The authors and contributors are not responsible for any financial losses incurred through the use of this software.

## Contributing

Contributions are welcome! Areas for contribution:

1. **Broker Integrations**: Add support for more brokers (Interactive Brokers, Alpaca, etc.)
2. **Data Sources**: Integrate additional data providers
3. **AI Providers**: Add support for more AI services
4. **Strategies**: Implement new trading strategies
5. **Technical Indicators**: Add more technical analysis tools
6. **Testing**: Add unit tests and integration tests
7. **Documentation**: Improve documentation and examples

## License

MIT License - see LICENSE file for details

## Support

For questions, issues, or contributions:
- Open an issue on GitHub
- Check existing examples and documentation
- Review the code - it's well-documented!

## Roadmap

Future enhancements planned:
- [ ] Backtesting framework
- [ ] More broker integrations
- [ ] News sentiment integration
- [ ] Real-time streaming data
- [ ] Advanced risk management
- [ ] Portfolio optimization
- [ ] Web dashboard for monitoring
- [ ] Database integration for trade history
- [ ] More ML models (LSTM, Transformers)
- [ ] Multi-timeframe analysis

---

**Built with ❤️ for algorithmic traders and Python enthusiasts**
